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
    codigo_membro = Column(String(20), unique=True, index=True, nullable=True) # e.g. "M0001"
    situacao = Column(String(30), default="Ativo")  # "Ativo", "Inativo", "Afastado"
    nome = Column(String(150), nullable=False)
    cpf = Column(String(20), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Contato e Endereço
    whatsapp = Column(String(30), nullable=True)
    telefone = Column(String(30), nullable=True) # compatibility
    email = Column(String(100), nullable=True)
    cep = Column(String(20), nullable=True)
    cidade = Column(String(100), nullable=True)
    uf = Column(String(10), nullable=True)
    endereco = Column(String(200), nullable=True)
    numero = Column(String(30), nullable=True)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)

    # Contato de Emergência
    emergencia_nome = Column(String(150), nullable=True)
    emergencia_parentesco = Column(String(50), nullable=True)
    emergencia_telefone = Column(String(30), nullable=True)
    emergencia_observacao = Column(Text, nullable=True)

    # Vínculo com a Casa e Informações Religiosas
    data_ingresso = Column(Date, default=datetime.date.today)
    cargo = Column(String(100), nullable=False, default="Médium")
    orixa_cabeca = Column(String(100), nullable=True)
    orixa_adjunto = Column(String(100), nullable=True)
    entidades_linhas = Column(Text, nullable=True)

    # Observações Internas — Acesso Restrito
    observacoes_internas = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True) # compatibility
    responsavel_cadastro = Column(String(150), nullable=True)
    responsavel_ultima_alteracao = Column(String(150), nullable=True)

    # Configurações financeiras e consultas
    ativo = Column(Boolean, default=True)
    valor_mensalidade = Column(Float, nullable=False, default=50.0)
    isento_mensalidade = Column(Boolean, default=False)
    aprovado_consulta_privada = Column(Boolean, default=False)
    valor_consulta = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


def migrate_membro_schema(engine):
    """
    Ensure newly added columns exist in SQLite/PostgreSQL database without destroying data.
    Backfills sequential codigo_membro for existing records if null.
    """
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        columns = [c["name"] for c in inspector.get_columns("membros")]
        
        new_cols = {
            "codigo_membro": "VARCHAR(20)",
            "situacao": "VARCHAR(30) DEFAULT 'Ativo'",
            "cpf": "VARCHAR(20)",
            "data_nascimento": "DATE",
            "data_cadastro": "TIMESTAMP",
            "whatsapp": "VARCHAR(30)",
            "cep": "VARCHAR(20)",
            "cidade": "VARCHAR(100)",
            "uf": "VARCHAR(10)",
            "endereco": "VARCHAR(200)",
            "numero": "VARCHAR(30)",
            "complemento": "VARCHAR(100)",
            "bairro": "VARCHAR(100)",
            "emergencia_nome": "VARCHAR(150)",
            "emergencia_parentesco": "VARCHAR(50)",
            "emergencia_telefone": "VARCHAR(30)",
            "emergencia_observacao": "TEXT",
            "orixa_cabeca": "VARCHAR(100)",
            "orixa_adjunto": "VARCHAR(100)",
            "entidades_linhas": "TEXT",
            "observacoes_internas": "TEXT",
            "responsavel_cadastro": "VARCHAR(150)",
            "responsavel_ultima_alteracao": "VARCHAR(150)",
            "updated_at": "TIMESTAMP"
        }

        with engine.begin() as conn:
            for col_name, col_type in new_cols.items():
                if col_name not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE membros ADD COLUMN {col_name} {col_type}"))
                        print(f"Migration: added column {col_name} to membros table.")
                    except Exception as col_err:
                        print(f"Notice adding column {col_name}: {col_err}")

            # Backfill codigo_membro and situacao for existing records without code
            try:
                res = conn.execute(text("SELECT id FROM membros WHERE codigo_membro IS NULL OR codigo_membro = '' ORDER BY id ASC")).fetchall()
                if res:
                    max_code = 0
                    existing_codes = conn.execute(text("SELECT codigo_membro FROM membros WHERE codigo_membro IS NOT NULL AND codigo_membro != ''")).fetchall()
                    for (c_val,) in existing_codes:
                        if c_val and c_val.startswith("M"):
                            try:
                                num = int(c_val[1:])
                                if num > max_code:
                                    max_code = num
                            except ValueError:
                                pass
                    for row in res:
                        max_code += 1
                        code_str = f"M{max_code:04d}"
                        conn.execute(text("UPDATE membros SET codigo_membro = :code, situacao = 'Ativo' WHERE id = :mid"), {"code": code_str, "mid": row[0]})
                    print(f"Migration: backfilled codes for {len(res)} existing members.")
            except Exception as backfill_err:
                print(f"Notice backfilling member codes: {backfill_err}")

    except Exception as e:
        print(f"Warning running migrate_membro_schema: {e}")


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
    valor = Column(Text, nullable=False)



