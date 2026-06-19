"""
Módulo de Gerenciamento e Conversão do Banco de Alimentos.
Lida com a leitura de dados do Excel e padronização de unidades calóricas.
"""

import os
import pandas as pd
from typing import List, Dict, Any

# Descobre dinamicamente a pasta raiz do projeto e aponta para o Excel lá dentro
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_ALIMENTOS = os.path.join(BASE_DIR, "banco_alimentos.xlsx")

def converter_para_kcal_g(valor: float, unidade: str) -> float:
    """
    Padroniza qualquer unidade calórica comercial para o formato padrão kcal/g.
    
    Regras:
    - kcal/kg   -> divide por 1000
    - kcal/100g -> divide por 100
    - kcal/g    -> permanece igual
    """
    unidade_limpa = unidade.strip().lower()
    
    if unidade_limpa == "kcal/kg":
        return round(valor / 1000.0, 4)
    elif unidade_limpa == "kcal/100g":
        return round(valor / 100.0, 4)
    elif unidade_limpa == "kcal/g":
        return round(valor, 4)
    else:
        raise ValueError(f"Unidade desconhecida: {unidade}. Use 'kcal/kg', 'kcal/100g' ou 'kcal/g'.")


def carregar_e_padronizar_alimentos() -> pd.DataFrame:
    """
    Carrega a planilha de alimentos e adiciona a coluna calculada 'em_kcal_g'.
    Retorna um DataFrame do Pandas.
    """
    if not os.path.exists(CAMINHO_ALIMENTOS):
        raise FileNotFoundError(f"O arquivo {CAMINHO_ALIMENTOS} não foi encontrado. Certifique-se de criá-lo.")
        
    # Lê a planilha Excel
    df = pd.read_excel(CAMINHO_ALIMENTOS)
    
    # Cria a nova coluna aplicando a função de conversão linha por linha
    df['em_kcal_g'] = df.apply(
        lambda linha: converter_para_kcal_g(linha['valor_calorico'], linha['unidade_original']), 
        axis=1
    )
    
    return df


def filtrar_alimentos_por_tipo(tipo_alimento: str) -> List[Dict[str, Any]]:
    """
    Filtra a base de dados retornando apenas os alimentos do tipo selecionado.
    Tipos válidos: 'Racao', 'Sache', 'Petisco'.
    """
    df = carregar_e_padronizar_alimentos()
    
    # Filtra as linhas correspondentes
    df_filtrado = df[df['tipo'].str.lower() == tipo_alimento.lower()]
    
    # Converte o resultado em uma lista de dicionários (fácil de usar na interface)
    return df_filtrado.to_dict(orient="records")


if __name__ == "__main__":
    # Teste rápido local para verificar se o módulo lê o Excel corretamente
    try:
        print("🤖 Testando carregamento de alimentos...")
        tabela = carregar_e_padronizar_alimentos()
        print("\n📊 Base de Alimentos com Energia Padronizada (kcal/g):")
        print(tabela[['nome', 'tipo', 'valor_calorico', 'unidade_original', 'em_kcal_g']])
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
