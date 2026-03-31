import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

# 1. Definição da URL com Fallback Seguro
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Ajuste para compatibilidade do SQLAlchemy (postgres:// -> postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Injetamos o sslmode diretamente na string de conexão para evitar o erro de keyword argument
    if "localhost" not in DATABASE_URL and "sslmode" not in DATABASE_URL:
        connector = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{connector}sslmode=require"
else:
    # Fallback para SQLite local apenas se não houver variável de ambiente
    DATABASE_URL = "sqlite:///./test.db" 

# 2. Configuração do Engine
# Removido connect_args para evitar o erro "'sslmode' is an invalid keyword argument"
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

# 3. Sessão e Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Modelos
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
    chapa = relationship("EstoqueChapa")

    __table_args__ = (CheckConstraint("tipo IN ('ENTRADA', 'SAIDA')", name='check_tipo_mov'),)

# 5. Função de Inicialização
def init_db():
    Base.metadata.create_all(bind=engine)