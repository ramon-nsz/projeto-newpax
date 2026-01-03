import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# 1. Definição da URL com Log de Depuração
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    print("✅ Conexão: Variável DATABASE_URL encontrada!")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    print("⚠️ ALERTA: DATABASE_URL não encontrada no ambiente! Usando LOCALHOST como reserva.")
    DATABASE_URL = "postgresql://postgres:123@localhost:5432/newpax_estoque"

# 2. Configuração do Engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 3. Criação da Base e Sessão (PRECISA VIR ANTES DAS CLASSES)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Modelos (Classes)
class EstoqueChapa(Base):
    __tablename__ = "estoque_chapas"
    id_estchapa = Column(Integer, primary_key=True, index=True)
    tipo_material = Column(String(100), nullable=False)
    espessura = Column(String(20))
    cor = Column(String(30))
    quantidade_est = Column(Integer, default=0)

class Movimentacao(Base):
    __tablename__ = "movimentacoes"
    id_movimentacao = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10)) 
    qtd = Column(Integer, nullable=False)
    data_hora = Column(DateTime, default=datetime.now)
    colaborador = Column(String(50), nullable=False) 
    id_estchapa = Column(Integer, ForeignKey("estoque_chapas.id_estchapa"))
    id_clienteos = Column(String(50), nullable=True) 

    __table_args__ = (CheckConstraint(tipo.in_(['ENTRADA', 'SAIDA']), name='check_tipo_mov'),)

# No final do arquivo database.py
def init_db():
    Base.metadata.create_all(bind=engine)

# Adicione isso para garantir que o banco atualize sempre que o app ligar
init_db()