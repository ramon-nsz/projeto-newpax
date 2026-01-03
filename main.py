from flask import Flask, render_template, request, redirect, url_for, flash
from models.database import SessionLocal, EstoqueChapa, Movimentacao, init_db
from services import cadastrar_novo_material, registrar_saida 
from datetime import datetime

app = Flask(__name__)
app.secret_key = "pax_secret"

# Chamamos o init_db apenas para garantir que as tabelas existam, 
# sem apagar os dados que já estão lá.
init_db()

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
                    colaborador=funcionario,
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
            funcionario = request.form.get('funcionario')
            tipo = request.form.get('tipo_material')
            esp = request.form.get('espessura')
            cor = request.form.get('cor')
            qtd_str = request.form.get('quantidade')
            os_destino = request.form.get('num_os')

            if not funcionario or not tipo or not qtd_str:
                flash("⚠️ Erro: Nome, Tipo e Quantidade são obrigatórios!")
                return redirect(url_for('cadastrar_novo'))

            qtd = int(qtd_str)
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

    return render_template('registrar_material.html')

@app.route('/relatorio')
def relatorio():
    db = SessionLocal()
    try:
        historico = db.query(Movimentacao).order_by(Movimentacao.data_hora.desc()).all()
        return render_template('relatorio.html', movimentacoes=historico)
    except Exception as e:
        flash(f"Erro ao carregar relatório: {e}")
        return redirect(url_for('index'))
    finally:
        db.close()

if __name__ == "__main__":
    app.run(debug=True)