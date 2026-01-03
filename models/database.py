import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# --- CONFIGURAÇÃO DE AMBIENTE (DINÂMICA) ---
# Tenta pegar a URL do Render. Se não existir, usa a sua local.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Ajuste necessário: SQLAlchemy exige 'postgresql://' e o Render envia 'postgres://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Sua URL local de desenvolvimento
    DATABASE_URL = "postgresql://postgres:123@localhost:5432/newpax_estoque"

# --- INICIALIZAÇÃO DO BANCO ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS ---
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

def init_db():
    Base.metadata.create_all(bind=engine)