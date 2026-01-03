from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://postgres:123@localhost:5432/newpax_estoque"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    id_colaborador = Column(Integer) # Simplificado para teste
    id_estchapa = Column(Integer, ForeignKey("estoque_chapas.id_estchapa"))
    # MUDANÇA: Agora é String para aceitar a digitação livre
    id_clienteos = Column(String(50), nullable=True) 

    __table_args__ = (CheckConstraint(tipo.in_(['ENTRADA', 'SAIDA']), name='check_tipo_mov'),)

def init_db():
    Base.metadata.create_all(bind=engine)