import sqlite3
import os
import pandas as pd
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join("dados", "nutricao_vet.db")
DASHBOARD_PATH = os.path.join("dados", "dashboard_indicadores.xlsx")

def conectar_banco() -> sqlite3.Connection:
    """Estabelece uma conexão com o banco de dados SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def inicializar_banco() -> None:
    """Cria as tabelas do sistema caso elas ainda não existam."""
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbCadastro (
        id_paciente TEXT PRIMARY KEY,
        nome_animal TEXT NOT NULL,
        tutor TEXT NOT NULL,
        especie TEXT CHECK(especie IN ('cao', 'gato')) NOT NULL,
        sexo TEXT CHECK(sexo IN ('M', 'F')) NOT NULL,
        castrado INTEGER CHECK(castrado IN (0, 1)) NOT NULL,
        peso_atual REAL NOT NULL,
        score_corporal INTEGER CHECK(score_corporal BETWEEN 1 AND 9) NOT NULL,
        data_avaliacao TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbDieta (
        id_dieta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente TEXT NOT NULL,
        etapa INTEGER CHECK(etapa IN (1, 2)) NOT NULL,
        tipo TEXT CHECK(tipo IN ('Racao', 'Sache', 'Petisco')) NOT NULL,
        alimento TEXT NOT NULL,
        em_kcal_g REAL NOT NULL,
        kcal_destinadas REAL NOT NULL,
        quantidade_g_dia REAL NOT NULL,
        n_refeicoes INTEGER NOT NULL,
        g_refeicao REAL NOT NULL,
        nem_etapa REAL NOT NULL,
        FOREIGN KEY (id_paciente) REFERENCES tbCadastro (id_paciente) ON DELETE CASCADE
    );
    """)

    conexao.commit()
    conexao.close()


def atualizar_planilha_dashboard() -> None:
    """
    Lê o banco de dados SQLite, calcula os indicadores macro da clínica
    e salva em um arquivo Excel/LibreOffice com múltiplas abas.
    """
    conexao = conectar_banco()
    
    # Carrega os dados cadastrados em DataFrames do Pandas
    df_pacientes = pd.read_sql_query("SELECT * FROM tbCadastro", conexao)
    conexao.close()
    
    if df_pacientes.empty:
        return

    # 1. Tabela de Métricas Gerais
    total_pacientes = len(df_pacientes)
    peso_medio_atual = df_pacientes["peso_atual"].mean()
    ecc_medio = df_pacientes["score_corporal"].mean()
    
    df_geral = pd.DataFrame({
        "Indicador": ["Total de Pacientes Atendidos", "Média de Peso Atual (kg)", "Média de Score Corporal (ECC)"],
        "Valor": [total_pacientes, round(peso_medio_atual, 2), round(ecc_medio, 1)]
    })

    # 2. Tabela de Distribuição por Espécie
    df_especie = df_pacientes["especie"].value_counts().reset_index()
    df_especie.columns = ["Espécie", "Quantidade de Pacientes"]
    df_especie["Espécie"] = df_especie["Espécie"].map({"cao": "Cão", "gato": "Gato"})

    # 3. Tabela de Classificação de Risco (Sobrepeso / Obesidade)
    def classificar_ecc(ecc):
        if ecc == 5: return "Ideal"
        elif ecc < 5: return "Abaixo do Peso"
        elif ecc <= 7: return "Sobrepeso"
        else: return "Obesidade Crônica"
        
    df_pacientes["Status Clínico"] = df_pacientes["score_corporal"].apply(classificar_ecc)
    df_status = df_pacientes["Status Clínico"].value_counts().reset_index()
    df_status.columns = ["Status Clínico", "Quantidade"]

    # Grava tudo no arquivo Excel criando abas separadas de forma limpa
    with pd.ExcelWriter(DASHBOARD_PATH, engine="openpyxl") as writer:
        df_geral.to_excel(writer, sheet_name="Métricas Gerais", index=False)
        df_especie.to_excel(writer, sheet_name="Por Espécie", index=False)
        df_status.to_excel(writer, sheet_name="Status Clínico", index=False)


def salvar_paciente(dados: Dict[str, Any]) -> None:
    """Insere ou atualiza um paciente na tabela tbCadastro e atualiza os indicadores."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("""
    INSERT OR REPLACE INTO tbCadastro (
        id_paciente, nome_animal, tutor, especie, sexo, castrado, peso_atual, score_corporal, data_avaliacao
    ) VALUES (:id_paciente, :nome_animal, :tutor, :especie, :sexo, :castrado, :peso_atual, :score_corporal, :data_avaliacao);
    """, dados)
    
    conexao.commit()
    conexao.close()
    
    # Roda a atualização automática dos indicadores logo após salvar!
    atualizar_planilha_dashboard()


def salvar_itens_dieta(id_paciente: str, itens: List[Dict[str, Any]]) -> None:
    """Salva os itens da dieta de um paciente."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM tbDieta WHERE id_paciente = ?;", (id_paciente,))
    
    for item in itens:
        item['id_paciente'] = id_paciente
        cursor.execute("""
        INSERT INTO tbDieta (
            id_paciente, etapa, tipo, alimento, em_kcal_g, kcal_destinadas, quantidade_g_dia, n_refeicoes, g_refeicao, nem_etapa
        ) VALUES (:id_paciente, :etapa, :tipo, :alimento, :em_kcal_g, :kcal_destinadas, :quantidade_g_dia, :n_refeicoes, :g_refeicao, :nem_etapa);
        """, item)
        
    conexao.commit()
    conexao.close()


def buscar_paciente(id_paciente: str) -> Optional[Dict[str, Any]]:
    """Busca um paciente pelo ID."""
    conexao = conectar_banco()
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM tbCadastro WHERE id_paciente = ?;", (id_paciente,))
    linha = cursor.fetchone()
    conexao.close()
    
    if linha:
        return dict(linha)
    return None