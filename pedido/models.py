# -*- encoding: utf-8 -*-

from django.db import models
from sgo.models import OtifModel
from grade.models import Grade
from cliente.models import Cliente, PreCarregamento
import datetime, time
from falta.models import Motivo, MotivoDeAlteracaoDaAgenda, MotivoAtraso
from business_unit.models import BusinessUnitSpecificModel

# TODO: Atualizar a documentação
"""

Aplicação: Pedido

    Modelo: Carregamento
        business_unit       Código do estabelecimento (JDF, STO, JAG ou OSA)
        nm_ab_cliente       Código do cliente
        nr_nota_fis         Número da Nota fiscal
        nr_pedido           Número do pedido do cliente
        ds_ordem_compra     Número da ordem de compra
        ds_placa            Placa do veículo
        ds_transp           Nome da transportadora
        nr_lacre            Número do Lacre
        dt_hr_chegada       Data e Hora da chegada
        dt_hr_ini_carga     Data e Hora do inicio do carregamento
        dt_hr_fim_carga     Data e Hora do fim do carregamento
        dt_hr_liberacao     Data e Hora da liberação do caminhão

        ds_status_cheg      Calculado (Se hr_chegada > (data e Hr Grade - Limite carga da tabela
                            ARZ_LIMITE_CLIENTE) então "Atrasado" senão "No Horário")

        ds_status_lib       Calculado (Se Hr de Liberação > (data e Hr Grade + Limite Liberacao da tabela
                            ARZ_LIMITE_CLIENTE) então "Atrasado" senão "No Horário")

        ds_obs_carga        Conteúdo livre
        id_no_show          S ou N
        vl_fixo             Valor fixo da multa
        vl_base_multa       Valor base da multa
        vl_multa            Calculado (Se "id_no_show" = S então (("Valor base
                            multa" * 0,05)+"vl_fixo") senão, 0)

    Modelo: Item
        business_unit       Código do estabelecimento (JDF, STO, JAG ou OSA)
        nm_ab_cliente       Código do cliente
        nr_nota_fis         Número da Nota fiscal
        dt_saida            Data de saída do pedido
        hr_grade            Hora da grade do cliente
        cd_produto          Código do produto
        un_embalagem        Unidade de embalagem
        qt_embalagem        Quantidade de embalagens
        qt_pilha            Quantidade da pilha
        qt_carregada        Quantidade carregada
        qt_falta            Quantidade faltante
        id_motivo
        qt_pallet           Quantidade de pallets
        vl_base_multa       Valor base da multa
        vl_multa            Calculado (Se "id_no_show" = S então (("Valor base
                            multa" * 0,05)+"vl_fixo") senão, 0)
"""

class Carregamento(BusinessUnitSpecificModel):
    class Meta:
        permissions = (
            ("can_schedule", "Pode Agendar Pedidos"),
            ("can_load", "Pode Carregar"),
        )

    SEM_PROGRAMACAO = 0    
    PROGRAMADO = 1
    NA_PLANTA = 2
    INICIO = 3
    FIM = 4
    LIBERADO = 5
    NO_CLIENTE = 6
    DESCARREGADO = 7
    STATUS=(
        (SEM_PROGRAMACAO, 'Carregamento sem programação'),
        (PROGRAMADO, 'Carregamento programado'),
        (NA_PLANTA, 'Caminhão na planta'),
        (INICIO, 'Carregamento iniciado'),
        (FIM, 'Carregamento finalizado'),
        (LIBERADO, 'Caminhão liberado'),
        (NO_CLIENTE, 'Caminhão no cliente'),
        (DESCARREGADO, 'Pedido entregue')
    )

    SIM=1
    NAO=2
    NO_SHOW=(
        (SIM,'S'),
        (NAO,'N')
    )
    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', blank='true', null='true', )
    nr_nota_fis = models.CharField('Nota fiscal', max_length=32, null='true', blank='true', )
    nr_pedido = models.CharField('Pedido', max_length=24, null='true', blank='true', )
    ds_ord_compra = models.CharField('Ordem compra', max_length=15, null='true', blank='true', )
    dt_saida = models.DateField('Data Programada', null='true', blank='true', )
    hr_grade = models.TimeField('Horário', null='true', blank='true',)
    ds_placa = models.CharField('Placa do veículo', max_length=8, null='true', blank='true', )
    ds_transp = models.CharField('Transportadora', max_length=30, null='true', blank='true', )
    nr_lacre = models.CharField('Número do lacre', max_length=10, null='true', blank='true', )
    dt_hr_chegada = models.DateTimeField('Chegada do caminhão', null='true', blank='true', )
    dt_hr_ini_carga = models.DateTimeField('Inicio do carregamento', null='true', blank='true', )
    dt_hr_fim_carga = models.DateTimeField('Fim do carregamento', null='true', blank='true', )
    dt_hr_liberacao = models.DateTimeField('Liberação do caminhão', null='true', blank='true', )
    ds_status_carrega = models.IntegerField('Status', choices=STATUS, default=SEM_PROGRAMACAO, 
                                            null='true', blank='true')
    ds_status_cheg = models.CharField('Status de chegada', max_length=15, null='true', blank='true')
    ds_status_lib = models.CharField('Status de liberação', max_length=15, null='true', blank='true')
    qt_pallet = models.IntegerField('Quantidade de Pallets', default=0, )
    ds_obs_carga = models.CharField('Obs', max_length=500, null='true', blank='true', )
    id_no_show = models.IntegerField('No Show', choices= NO_SHOW, null='true', blank='true',)
    pallets = models.CharField('Pallets', max_length=1000, null='true', blank='true',)
    cd_rota = models.CharField('Rota', max_length=10, null= 'true', blank='true')
    
    motivo_atraso = models.ForeignKey(MotivoAtraso, verbose_name='Motivo do Atraso', 
                                    blank='true', null='true', related_name='motivo_atraso')
    ds_obs_atraso = models.CharField('Observação Atraso', max_length=300, blank='true', null='true', )
    
    # campos agendamento
    tipo_frete = models.CharField('Frete', max_length = 5, null='true',blank='true')
    dt_hr_agenda = models.DateTimeField('Agendamento da entrega', null='true', blank='true', )
    dt_hr_cheg_cliente = models.DateTimeField('Chegada no cliente', null='true', blank='true', )
    dt_hr_descarrega = models.DateTimeField('Descarregamento', null='true', blank='true', )
    motivo_altera_agenda = models.ForeignKey(MotivoDeAlteracaoDaAgenda, 
                                            verbose_name='Motivo da alteração da agenda', 
                                            null='true', blank='true', )
    protocolo_agenda = models.CharField('Protocolo do agendamento', max_length=100, null='true', blank='true', )
    ds_obs_agenda = models.CharField('Obs', max_length=500, null='true', blank='true', )
    ds_status_cheg_cliente = models.CharField('Status de chegada no cliente',
                                             max_length=15, null='true', blank='true')
    
    def __unicode__(self):
        if self.nr_nota_fis: 
            nf =  self.nr_nota_fis
        else:
            nf = ''
        return ''.join([self.cliente.nm_ab_cli, nf])

    def set_chega_cliente(self):
        """
        Se o frete for CIF, e a data/hora de chegada no cliente 
        for posterior à data/hora de agendamento, o status deverá ser em atraso se não,
        no horário.
        """ 
        
        if self.dt_hr_cheg_cliente and self.dt_hr_agenda:
            if self.tipo_frete == 'CIF' and self.dt_hr_cheg_cliente > self.dt_hr_agenda:
                    self.ds_status_cheg_cliente = 'Atrasado'
            else:
                self.ds_status_cheg_cliente = 'No Horário'
        else:
            self.ds_status_cheg_cliente = '-'
        
        self.ds_status_carrega = self.NO_CLIENTE
        self.save()

    def set_descarregado(self):
        self.ds_status_carrega = self.DESCARREGADO
        self.save()

    def set_agenda(self, data, motivo, protocolo, obs):
        if data: self.dt_hr_agenda = data
        if motivo: self.motivo_altera_agenda = motivo
        if protocolo: self.protocolo_agenda = protocolo
        if obs:self.ds_obs_agenda = obs

        self.ds_status_carrega = self.PROGRAMADO
        self.save()

    def set_chegada(self, date, grade, placa, lacre):
        if date: self.dt_hr_chegada = date
        if grade: self.hr_grade = grade
        if placa: self.ds_placa = placa
        if lacre: self.nr_lacre = lacre

        # Se ainda não foi setada data e hora de chegada, colocar a data atual
        if not self.dt_hr_chegada: self.dt_hr_chegada = datetime.datetime.now().replace(microsecond=0)

        # Se ainda não foi setada data de previsão colocar a data de chegada
        if not self.dt_saida: self.dt_saida = datetime.datetime.strptime(str(self.dt_hr_chegada),
                                                                         "%Y-%m-%d %H:%M:%S").date()

        # Se ainda não foi setada hora de grade, colocar hora de chegada sem microsegundos
        if not self.hr_grade: self.hr_grade = datetime.datetime.strptime(str(self.dt_hr_chegada),
                                                                         "%Y-%m-%d %H:%M:%S").time().replace(microsecond=0)

        self.ds_status_carrega = self.NA_PLANTA
        self.ds_status_cheg=self.get_status_cheg()
        self.save()

    def set_inicio(self, date, placa, lacre, is_pre_carregamento):
        if date: self.dt_hr_ini_carga = date
        if placa: self.ds_placa = placa
        if lacre: self.nr_lacre = lacre
        # Se o cliente estiver no grupo de pré carregamento, a quantidade carregada de cada ítem, 
        # deve ser igual a quantidade de embalagens a carregar do mesmo ítem somente se ainda não
        # foi preenchido nada no campo de quantidade carregada.
        if is_pre_carregamento:
            items = self.carregamento_items.all()
            for item in items:
                if item.qt_carregada == 0:
                    item.qt_carregada = item.qt_embalagem
                item.save()
        self.ds_status_carrega = self.INICIO

        self.save()

    def set_fim(self, date, placa, lacre):
        if date: self.dt_hr_fim_carga = date
        if placa: self.ds_placa = placa
        if lacre: self.nr_lacre = lacre
        self.ds_status_carrega = self.FIM
        self.save()

    def set_libera(self, date, placa, lacre):

        if date: self.dt_hr_liberacao = date
        if placa: self.ds_placa = placa
        if lacre: self.nr_lacre = lacre

        # Se ainda não foi setada data e hora de liberação, colocar a data atual
        if not self.dt_hr_liberacao: self.dt_hr_liberacao = datetime.datetime.now().replace(microsecond=0)

        self.ds_status_carrega = self.LIBERADO
        self.ds_status_lib=self.get_status_lib()
        self.save()

    def get_status_cheg(self):
        """Calculado(Se Hr de chegada > (data e Hr Grade - Limite carga da tabela ARZ_LIMITE_CLIENTE) então "Atrasado"
        senão "No Horário")
        """

        hr_grade = datetime.datetime.strptime(str(self.hr_grade), "%H:%M:%S").time()

        #data programada
        dt_saida = datetime.datetime.strptime(str(self.dt_saida), "%Y-%m-%d").date()

        dt_previsao = (datetime.datetime.combine(dt_saida, hr_grade))
        # baseado no limite de carregamento do cliente, calcula a data/hora máxima para não ser considerado atraso
        # Se não foi cadastrado limite para o carregamento, considera 0
        try:
            delta = datetime.timedelta(hours=self.cliente.hr_lim_carga.hour or 0,
                                        minutes =self.cliente.hr_lim_carga.minute or 0)
        except:
            delta = datetime.timedelta(hours=0, minutes=0)

        dt_hr_maxima = dt_previsao + delta
        dt_hr_chegada = datetime.datetime.strptime(str(self.dt_hr_chegada), "%Y-%m-%d %H:%M:%S")
        if dt_hr_chegada > dt_hr_maxima:
            return "Atrasado"
        else:
            return "No Horário"

    def get_status_lib(self):
        """Calculado(Se Hr de liberação > (data e Hr Grade + Limite liberação da tabela ARZ_LIMITE_CLIENTE) então
        "Atrasado" senão "No Horário")"""
        hr_grade = datetime.datetime.strptime(str(self.hr_grade), "%H:%M:%S").time()

        #data programada
        dt_saida = datetime.datetime.strptime(str(self.dt_saida), "%Y-%m-%d").date()

        dt_previsao = (datetime.datetime.combine(dt_saida, hr_grade))
        # baseado no limite do cliente, calcula a data/hora máxima para não ser considerado atraso
        # Se não foi cadastrado limite para de liberação, considera 0
        try:
            delta = datetime.timedelta(hours=self.cliente.hr_lim_lib.hour or 0,
                                        minutes=self.cliente.hr_lim_lib.minute or 0)
        except:
            delta = datetime.timedelta(hours=0, minutes=0)

        dt_hr_maxima = dt_previsao + delta
        dt_hr_liberacao = datetime.datetime.strptime(str(self.dt_hr_liberacao), "%Y-%m-%d %H:%M:%S")
        if dt_hr_liberacao > dt_hr_maxima:
            return "Atrasado"
        else:
            return "No Horário"
    
    def add_motivo_atraso(self, motivo, ds_obs):
        if motivo: self.motivo_atraso = motivo
        if ds_obs: self.ds_obs_atraso = ds_obs
        self.save()


class Item(BusinessUnitSpecificModel):

    cd_produto = models.CharField('Código do produto', max_length=32, null='true', blank='true', )
    ds_produto = models.CharField('Descrição do produto', max_length=200, null='true', blank='true')
    un_embalagem = models.CharField('Unidade de embalagem', max_length=3, null='true', blank='true', )
    qt_embalagem = models.IntegerField('Quantidade de embalagens', default=0, )
    qt_pilha = models.CharField('Pilhas', max_length=10, null='true', blank='true', )
    qt_carregada = models.IntegerField('Quantidade carregada', default=0,)
    # qt_falta = models.IntegerField('Quantidade em falta', null='true', blank='true', )
    motivo = models.ForeignKey(Motivo, null='true', blank='true', )
    carregamento = models.ForeignKey(Carregamento, related_name='carregamento_items')

    @property
    def qt_falta(self):
        return self.qt_embalagem - self.qt_carregada

    def __unicode__(self):
        return self.ds_produto or ''
    
    def pre_carregamento(self):
         if self.qt_carregada == 0:
                self.qt_carregada = self.qt_embalagem


class FillRate(Item):
    class Meta:
        proxy = True


class NoShow(Carregamento):
    class Meta:
        proxy = True