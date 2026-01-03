from models.database import SessionLocal, EstoqueChapa, Movimentacao
from datetime import datetime

def registrar_saida(id_chapa, qtd, id_os, funcionario): # Adicionado funcionario
    db = SessionLocal()
    try:
        chapa = db.query(EstoqueChapa).filter(EstoqueChapa.id_estchapa == id_chapa).first()
        
        if not chapa or chapa.quantidade_est < qtd:
            return False 

        chapa.quantidade_est -= qtd

        nova_mov = Movimentacao(
            tipo='SAIDA',
            qtd=qtd,
            id_estchapa=id_chapa,
            id_clienteos=str(id_os),
            data_hora=datetime.now(),
            colaborador=funcionario # Agora usa o nome real
        )

        db.add(nova_mov) 
        db.commit()      
        return True
    except Exception as e:
        db.rollback()
        print(f"Erro ao registrar saída: {e}")
        return False
    finally:
        db.close()

def cadastrar_novo_material(tipo_material, espessura, cor, quantidade, num_os, funcionario): # Adicionado funcionario
    db = SessionLocal()
    try:
        tipo_limpo = tipo_material.strip().upper()
        espessura_limpa = espessura.strip().upper()
        cor_limpa = cor.strip().upper()

        material_existente = db.query(EstoqueChapa).filter(
            EstoqueChapa.tipo_material == tipo_limpo,
            EstoqueChapa.espessura == espessura_limpa,
            EstoqueChapa.cor == cor_limpa
        ).first()

        if material_existente:
            material_existente.quantidade_est += quantidade
            id_final = material_existente.id_estchapa
        else:
            novo_material = EstoqueChapa(
                tipo_material=tipo_limpo,
                espessura=espessura_limpa,
                cor=cor_limpa,
                quantidade_est=quantidade
            )
            db.add(novo_material)
            db.flush() 
            id_final = novo_material.id_estchapa

        mov_entrada = Movimentacao(
            tipo='ENTRADA',
            qtd=quantidade,
            id_estchapa=id_final,
            id_clienteos=str(num_os).strip().upper(),
            colaborador=funcionario, # Registra quem deu entrada no material
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