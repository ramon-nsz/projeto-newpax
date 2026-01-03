from models.database import SessionLocal, EstoqueChapa, Movimentacao
from sqlalchemy.exc import SQLAlchemyError
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

def cadastrar_novo_material(tipo_material, espessura, cor, quantidade, num_os, funcionario):
    db = SessionLocal()
    try:
        # 1. Limpeza e Padronização
        tipo_limpo = tipo_material.strip().upper()
        esp_limpa = espessura.strip().upper()
        cor_limpa = cor.strip().upper()

        # 2. Busca se o material já existe para somar o estoque
        material_existente = db.query(EstoqueChapa).filter(
            EstoqueChapa.tipo_material == tipo_limpo,
            EstoqueChapa.espessura == esp_limpa,
            EstoqueChapa.cor == cor_limpa
        ).first()

        if material_existente:
            material_existente.quantidade_est += int(quantidade)
            id_final = material_existente.id_estchapa
        else:
            # Cria novo registro se não existir
            novo_material = EstoqueChapa(
                tipo_material=tipo_limpo,
                espessura=esp_limpa,
                cor=cor_limpa,
                quantidade_est=int(quantidade)
            )
            db.add(novo_material)
            db.flush() # Gera o ID para usar na movimentação abaixo
            id_final = novo_material.id_estchapa

        # 3. Registra a Movimentação (Histórico)
        mov_entrada = Movimentacao(
            tipo='ENTRADA',
            qtd=int(quantidade),
            id_estchapa=id_final,
            id_clienteos=str(num_os).strip().upper(),
            colaborador=funcionario,
            data_hora=datetime.now()
        )
        db.add(mov_entrada)
        
        db.commit() # Salva tudo de forma atômica
        return True, f"Material {tipo_limpo} cadastrado com sucesso!"

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Erro SQL: {e}")
        return False, "Erro crítico no banco de dados."
    except Exception as e:
        db.rollback()
        print(f"Erro Geral: {e}")
        return False, f"Erro inesperado: {str(e)}"
    finally:
        db.close()