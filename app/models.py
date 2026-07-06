import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Float
from app.database import Base

class User(Base):
    """
    User model for administrators and future medium accounts.
    Ready for integration with password hashing and session tokens.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default="secretario")  # programador, pai_de_santo, tesoureiro, secretario
    full_name = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)
    birth_date = Column(Date, nullable=True)
    is_approved = Column(Boolean, default=True) # Default to True so existing users are approved
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AgendaEvent(Base):
    """
    Events scheduled for the temple (Giras, study sessions, special works).
    Used to display the temple schedule.
    """
    __tablename__ = "agenda_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    time = Column(String(10), nullable=False)  # e.g., "19:30"
    type = Column(String(50), default="Gira")  # Gira, Estudos, Desenvolvimento, Atendimento
    status = Column(String(50), default="Confirmada")  # Confirmada, Especial, Cancelada
    publico = Column(Boolean, default=True)  # True = Aberta ao público, False = Fechada (membros)
    segmento = Column(String(50), default="Umbanda")  # Umbanda, Candomblé
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Aviso(Base):
    """
    Bulletin board announcements for the public or internal mediums.
    """
    __tablename__ = "avisos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    date_posted = Column(Date, default=datetime.date.today)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Membro(Base):
    """
    Membros/Médiuns do terreiro.
    """
    __tablename__ = "membros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    cargo = Column(String(100), nullable=False)  # e.g., "Médium de incorporação", "Ogã", "Cambone"
    telefone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    data_ingresso = Column(Date, default=datetime.date.today)
    ativo = Column(Boolean, default=True)
    observacoes = Column(Text, nullable=True)
    valor_mensalidade = Column(Float, nullable=False, default=50.0) # Valor padrão da mensalidade do membro
    isento_mensalidade = Column(Boolean, default=False) # Isenção de mensalidade
    aprovado_consulta_privada = Column(Boolean, default=False)
    valor_consulta = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TransacaoFinanceira(Base):
    """
    Transações de caixa do terreiro (mensalidades, doações, despesas).
    """
    __tablename__ = "transacoes_financeiras"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    tipo = Column(String(20), nullable=False)  # "receita" ou "despesa"
    categoria = Column(String(100), nullable=False)  # "Mensalidade", "Doação", "Aluguel", "Velas", etc.
    data = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class QuadroAviso(Base):
    """
    Quadro de avisos interno para uso restrito de membros/administradores do terreiro.
    """
    __tablename__ = "quadro_avisos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    date_posted = Column(Date, default=datetime.date.today)
    author_name = Column(String(100), nullable=False)  # Nome de quem publicou o aviso
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class MensalidadePagamento(Base):
    """
    Controle de pagamento de mensalidades dos membros da corrente.
    """
    __tablename__ = "mensalidades_pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    membro_id = Column(Integer, nullable=False)  # ID do Membro correspondente
    ano = Column(Integer, nullable=False)        # Ano de referência (ex: 2026)
    mes = Column(Integer, nullable=False)        # Mês de referência (1 a 12)
    pago = Column(Boolean, default=False)        # Status do pagamento
    isento = Column(Boolean, default=False, nullable=False)
    valor = Column(Float, nullable=False, default=50.0) # Valor pago ou a pagar
    data_pagamento = Column(Date, nullable=True) # Data em que o pagamento foi realizado
    observacao = Column(String(200), nullable=True) # Observações adicionais
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ConsultaPrivada(Base):
    """
    Agendamento de consultas privadas com Pai de Santo ou outros membros autorizados.
    """
    __tablename__ = "consultas_privadas"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String(150), nullable=False)
    telefone_cliente = Column(String(30), nullable=False)
    email_cliente = Column(String(100), nullable=True)
    data = Column(Date, nullable=False)
    horario = Column(String(10), nullable=False)  # Ex: "14:00"
    membro_id = Column(Integer, nullable=False)   # ID do Membro (Pai de Santo ou outro médium autorizado)
    tipo = Column(String(50), default="Consulta")  # Consulta ou Trabalho
    status = Column(String(50), default="Pendente") # Pendente, Confirmada, Realizada, Cancelada
    valor_consulta = Column(Float, nullable=True, default=0.0) # Valor específico desta consulta
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ConfiguracaoSistema(Base):
    """
    Tabela de configurações gerais do sistema.
    """
    __tablename__ = "configuracoes_sistema"

    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String(100), unique=True, index=True, nullable=False)
    valor = Column(String(255), nullable=False)



