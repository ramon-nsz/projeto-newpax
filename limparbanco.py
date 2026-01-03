from models.database import engine, Base
import models.database # Garante que os modelos sejam carregados

print("Limpando tabelas...")
Base.metadata.drop_all(bind=engine)
print("Criando tabelas novas...")
Base.metadata.create_all(bind=engine)
print("Pronto! O banco está atualizado.")