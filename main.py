from flask import Flask, render_template, request, redirect, url_for, flash
from models.database import SessionLocal, EstoqueChapa, Movimentacao, init_db
from services import cadastrar_novo_material, registrar_saida 
from datetime import datetime

app = Flask(__name__)
app.secret_key = "pax_secret"

#init_db() # Cria as tabelas se não existirem

@app.route('/')
def index():
    db = SessionLocal()
    chapas = db.query(EstoqueChapa).all()
    db.close()
    return render_template('index.html', chapas=chapas)

@app.route('/movimentar', methods=['GET', 'POST'])
def movimentar():
    db = SessionLocal()
    if request.method == 'POST':
        try:
            funcionario = request.form['funcionario']
            id_chapa = int(request.form['chapa'])
            qtd = int(request.form['quantidade'])
            num_os = request.form['num_os']
            
            chapa = db.query(EstoqueChapa).filter(EstoqueChapa.id_estchapa == id_chapa).first()
            if chapa and chapa.quantidade_est >= qtd:
                chapa.quantidade_est -= qtd
                mov = Movimentacao(
                    tipo='SAIDA',
                    qtd=qtd,
                    id_estchapa=id_chapa,
                    id_clienteos=str(num_os),
                    colaborador=funcionario, # salva o nome do funcionario
                    data_hora=datetime.now()
                )
                db.add(mov)
                db.commit()
                flash(f"✅ Saída da OS {num_os} registrada!")
                return redirect(url_for('relatorio'))
            else:
                flash("❌ Erro: Saldo insuficiente.")
        except Exception as e:
            db.rollback()
            flash(f"❌ Erro: {e}")
        finally:
            db.close()
            
    chapas = db.query(EstoqueChapa).all()
    db.close()
    return render_template('saida_material.html', chapas=chapas)

@app.route('/cadastrar_novo', methods=['GET', 'POST'])
def cadastrar_novo():
    if request.method == 'POST':
        try:
            # 1. Coleta os dados (com nomes exatos do seu HTML)
            funcionario = request.form.get('funcionario')
            tipo = request.form.get('tipo_material')
            esp = request.form.get('espessura')
            cor = request.form.get('cor')
            qtd_str = request.form.get('quantidade')
            os_destino = request.form.get('num_os')

            # 2. Validação visual imediata
            if not funcionario or not tipo or not qtd_str:
                flash("⚠️ Erro: Nome, Tipo e Quantidade são obrigatórios!")
                return redirect(url_for('cadastrar_novo'))

            qtd = int(qtd_str)

            # 3. Chama o serviço e DESEMPACOTA os dois retornos
            sucesso, mensagem = cadastrar_novo_material(tipo, esp, cor, qtd, os_destino, funcionario)

            if sucesso:
                flash(f"✅ {mensagem}")
                return redirect(url_for('index'))
            else:
                flash(f"❌ Erro no Banco: {mensagem}")
        
        except ValueError:
            flash("⚠️ A quantidade deve ser um número inteiro!")
        except Exception as e:
            flash(f"🚨 Erro crítico: {str(e)}")
            print(f"DEBUG: {str(e)}") # Aparece no seu terminal

    return render_template('registrar_material.html')

@app.route('/relatorio') # <-- Este é o endereço (URL)
def relatorio():         # <-- Este é o nome da função (endpoint)
    db = SessionLocal()
    try:
        # Buscamos as movimentações e incluímos os dados da chapa relacionada
        historico = db.query(Movimentacao).order_by(Movimentacao.data_hora.desc()).all()
        return render_template('relatorio.html', movimentacoes=historico)
    except Exception as e:
        flash(f"Erro ao carregar relatório: {e}")
        return redirect(url_for('index'))
    finally:
        db.close()

# ESTA LINHA DEVE SER SEMPRE A ÚLTIMA DO ARQUIVO
if __name__ == "__main__":
    app.run(debug=True)