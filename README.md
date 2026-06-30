# NewPax — Sistema de Controle de Estoque

Aplicação web para controle de inventário de chapas (materiais de comunicação visual), desenvolvida para substituir controles manuais em papel e planilhas paralelas por um sistema centralizado, rastreável e em tempo real.

**🔗 Demo ao vivo:** [projeto-newpax.vercel.app](https://projeto-newpax.vercel.app)

---

## 📌 Contexto

Na empresa onde trabalho, o controle de estoque de chapas era feito manualmente — anotações em papel e planilhas que não se conversavam entre si, gerando perda de rastreabilidade (quem retirou material, quando, e para qual Ordem de Serviço). Por iniciativa própria, identifiquei o problema e desenvolvi este sistema do zero: do levantamento do processo até o deploy em produção.

**Resultado:** controle de estoque 100% digitalizado, com rastreabilidade total de movimentações e disponibilidade de dados em tempo real, hoje em uso ativo na empresa.

## ⚙️ Funcionalidades

- **Cadastro de materiais** (`/cadastrar_novo`) — registro de novas chapas com tipo, espessura, cor e quantidade.
- **Registro de saída** (`/movimentar`) — colaborador dá baixa no material associando a movimentação a uma Ordem de Serviço (OS) e ao responsável, com validação de saldo disponível.
- **Relatório de movimentações** (`/relatorio`) — histórico completo, ordenado por data, de todas as entradas/saídas.
- **Setup automatizado** (`/setup`) — rota de inicialização que cria as tabelas no banco na primeira execução, sem precisar de acesso manual ao banco.

## 🏗️ Stack & Arquitetura

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Flask 3 |
| ORM | SQLAlchemy 2.0 |
| Banco de dados | PostgreSQL (hospedado no Supabase) |
| Driver DB | psycopg2-binary |
| Servidor WSGI | Gunicorn |
| Deploy | Vercel (Serverless Functions) |
| Versionamento | Git / GitHub |

**Decisões técnicas que valem destaque:**
- **Connection Pooling em modo Transaction (porta 6543)** — necessário porque funções serverless da Vercel abrem e fecham conexões a cada invocação; sem pooling configurado corretamente, o banco esgotaria conexões rapidamente.
- **Arquitetura em camadas** — separação entre rotas (`main.py`), regras de negócio (`services.py`) e modelos de dados (`models/database.py`), em vez de lógica concentrada nas rotas.
- **Infraestrutura serverless com custo zero quando ociosa** — escolha deliberada de Vercel + Supabase (tier gratuito) por ser um projeto interno de baixo volume, evitando custo de servidor dedicado.

## 🗂️ Modelo de dados (resumo)

- `EstoqueChapa` — saldo atual de cada tipo/espessura/cor de chapa.
- `Movimentacao` — histórico de entradas e saídas, vinculado a colaborador, OS/cliente e timestamp.

## 🚀 Como rodar localmente

```bash
# Clone o repositório
git clone https://github.com/ramon-nsz/projeto-newpax.git
cd projeto-newpax

# Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure a variável de ambiente do banco (Supabase/PostgreSQL)
# Crie um arquivo .env ou exporte diretamente:
export DATABASE_URL="postgresql://usuario:senha@host:porta/banco"
export SECRET_KEY="sua_chave_secreta"

# Rode a aplicação
python main.py
```

Acesse `http://localhost:5000`. No primeiro acesso, visite `/setup` para criar as tabelas no banco.

## 📈 Possíveis evoluções

- Autenticação de usuários (login por colaborador, hoje o nome é digitado livremente).
- Testes automatizados (unitários para `services.py`).
- Exportação de relatórios em CSV/Excel.
- Dashboard com indicadores (consumo por período, materiais com baixo estoque).

## 👤 Autor

**Eduardo Ramon Nunes de Souza**
Estudante de Sistemas de Informação | Python, SQL & Cloud

- [LinkedIn](https://www.linkedin.com/in/ramon-nunes2/)
- [GitHub](https://github.com/ramon-nsz)
