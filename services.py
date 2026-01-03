from models.database import SessionLocal, EstoqueChapa, Movimentacao
from datetime import datetime

def registrar_saida(id_chapa, qtd, id_os):
    db = SessionLocal()
    try:
        # 1. Busca a chapa no banco
        chapa = db.query(EstoqueChapa).filter(EstoqueChapa.id_estchapa == id_chapa).first()
        
        if not chapa or chapa.quantidade_est < qtd:
            return False # Estoque insuficiente ou chapa não existe

        # 2. Subtrai do saldo físico
        chapa.quantidade_est -= qtd

        # 3. CRIA O REGISTRO NO HISTÓRICO (Esta parte é a que estava faltando ou falhando)
        nova_mov = Movimentacao(
            tipo='SAIDA',
            qtd=qtd,
            id_estchapa=id_chapa,
            id_clienteos=str(id_os),
            data_hora=datetime.now(),
            id_colaborador=1 # ID padrão para teste
        )

        db.add(nova_mov) # Adiciona o histórico na fila do banco
        db.commit()      # Salva tudo de uma vez (Saldo e Histórico)
        return True
    except Exception as e:
        db.rollback()
        print(f"Erro ao registrar saída: {e}")
        return False
    finally:
        db.close()

def cadastrar_novo_material(tipo_material, espessura, cor, quantidade, num_os):
    db = SessionLocal()
    try:
        # 1. PADRONIZAÇÃO: Transforma tudo em MAIÚSCULO e remove espaços extras
        # Isso evita que "ACM" e "acm" virem linhas diferentes no banco.
        tipo_limpo = tipo_material.strip().upper()
        espessura_limpa = espessura.strip().upper()
        cor_limpa = cor.strip().upper()

        # 2. BUSCA: Procura se esse material exato já existe no estoque
        material_existente = db.query(EstoqueChapa).filter(
            EstoqueChapa.tipo_material == tipo_limpo,
            EstoqueChapa.espessura == espessura_limpa,
            EstoqueChapa.cor == cor_limpa
        ).first()

        if material_existente:
            # Se já existe, apenas SOMA ao que já tem (Independente do cliente/OS)
            material_existente.quantidade_est += quantidade
            id_final = material_existente.id_estchapa
        else:
            # Se for realmente um material novo, cria a primeira linha
            novo_material = EstoqueChapa(
                tipo_material=tipo_limpo,
                espessura=espessura_limpa,
                cor=cor_limpa,
                quantidade_est=quantidade
            )
            db.add(novo_material)
            db.flush() 
            id_final = novo_material.id_estchapa

        # 3. HISTÓRICO: Aqui é onde o nome do Cliente/OS fica guardado
        # O histórico aceita várias linhas para o mesmo ID de material.
        mov_entrada = Movimentacao(
            tipo='ENTRADA',
            qtd=quantidade,
            id_estchapa=id_final,
            id_clienteos=str(num_os).strip().upper(), # Guarda a OS do cliente
            data_hora=datetime.now()
        )
        db.add(mov_entrada)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        return False
    finally:
        db.close()