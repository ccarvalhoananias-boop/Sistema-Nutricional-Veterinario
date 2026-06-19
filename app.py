"""
Interface Principal do Sistema Nutricional Veterinário em Streamlit.
Módulo 3: Versão Estabilizada sem Loops de Recarregamento.
"""
import sys
import os

# Força o Python a incluir a pasta atual no caminho de busca de módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Daqui para baixo continua o seu código normal...
import streamlit as str_app
from datetime import datetime
from engine.calculos import calcular_peso_meta, determinar_etapas, calcular_nem, obter_limites_fator
# ... resto do código
import streamlit as str_app
from datetime import datetime
from engine.calculos import calcular_peso_meta, determinar_etapas, calcular_nem, obter_limites_fator
from engine.database import inicializar_banco, salvar_paciente, salvar_itens_dieta
from engine.alimentos import filtrar_alimentos_por_tipo

# Inicializa o banco de dados
inicializar_banco()

# Configuração da página
str_app.set_page_config(page_title="Nutrição Vet - Gestão de Peso", page_icon="🐾", layout="wide")

# Inicialização da memória temporária (Session State) para o controle de alimentos adicionais
if "n_alimentos_etapa1" not in str_app.session_state:
    str_app.session_state.n_alimentos_etapa1 = 1
if "n_alimentos_etapa2" not in str_app.session_state:
    str_app.session_state.n_alimentos_etapa2 = 1

str_app.title("🐾 Sistema Nutricional Veterinário — Manejo de Peso")
str_app.markdown("---")

# -------------------------------------------------------------------------
# BLOCO 1: CADASTRO E DIAGNÓSTICO
# -------------------------------------------------------------------------
col_cadastro, col_resultados = str_app.columns([1, 1])

with col_cadastro:
    str_app.header("📋 Ficha de Avaliação Clinical")
    id_paciente = str_app.text_input("ID do Paciente (Prontuário / Microchip):", placeholder="EX: PET-123").strip()
    nome_animal = str_app.text_input("Nome do Animal:")
    tutor = str_app.text_input("Nome do Tutor:")
    
    col_esp, col_sexo = str_app.columns(2)
    with col_esp:
        especie = str_app.selectbox("Espécie:", ["cao", "gato"], format_func=lambda x: "Cão" if x == "cao" else "Gato")
    with col_sexo:
        sexo = str_app.selectbox("Sexo:", ["M", "F"], format_func=lambda x: "Macho (M)" if x == "M" else "Fêmea (F)")
        
    castrado_op = str_app.radio("O animal é castrado?", ["Sim", "Não"], horizontal=True)
    is_castrado = 1 if castrado_op == "Sim" else 0
    
    col_p, col_ecc = str_app.columns(2)
    with col_p:
        peso_atual = str_app.number_input("Peso Atual (kg):", min_value=0.1, max_value=100.0, value=10.0, step=0.1)
    with col_ecc:
        score_corporal = str_app.slider("Score de Condição Corporal (ECC):", min_value=1, max_value=9, value=5, key="slider_ecc")
    
    limites = obter_limites_fator(especie, is_castrado == 1)
    str_app.caption(f"Sugestão Fator NEM: Mín: {limites['min']} | Padrão: {limites['padrao']} | Máx: {limites['max']}")
    fator_escolhido = str_app.slider("Selecione o fator ideal:", min_value=float(limites['min'] - 10), max_value=float(limites['max'] + 10), value=float(limites['padrao']), step=5.0, key="slider_fator_nem")

# Processamento matemático
desvio, peso_meta = calcular_peso_meta(peso_atual, score_corporal)
etapas_info = determinar_etapas(desvio, peso_meta)
total_etapas = etapas_info["total_etapas"]

with col_resultados:
    str_app.header("📊 Diagnóstico e Metas")
    if score_corporal == 5:
        str_app.success(f"Condição Corporal Ideal! Desvio: {desvio}%")
    elif score_corporal > 5:
        str_app.error(f"Paciente com Sobrepeso/Obesidade. Desvio: +{desvio}%")
    else:
        str_app.warning(f"Paciente Abaixo do Peso Ideal. Desvio: {desvio}%")
        
    str_col1, str_col2 = str_app.columns(2)
    str_col1.metric("Peso Atual", f"{peso_atual} kg")
    str_col2.metric("Peso Meta (Ideal)", f"{peso_meta} kg")
    str_app.markdown(f"**Estratégia:** Tratamento recomendado em **{total_etapas} etapa(s)**.")

str_app.markdown("---")

todos_itens_dieta = []

# -------------------------------------------------------------------------
# FUNÇÃO ESTABILIZADA DE FORMULAÇÃO DE DIETAS
# -------------------------------------------------------------------------
def formular_dieta_estabilizada(num_etapa: int, peso_alvo: float, nem_meta: float, total_alimentos: int):
    str_app.subheader(f"🍽️ Dieta da ETAPA {num_etapa} (Alvo: {peso_alvo} kg | Meta: {nem_meta} kcal/dia)")
    
    # Listas para coletar as escolhas da tela
    escolhas_tipos = []
    escolhas_nomes = []
    escolhas_kcal = []
    escolhas_refs = []
    escolhas_dados_al = []
    
    kcal_outros = 0.0
    
    # Loop 1: Apenas renderiza os componentes de entrada na tela
    for i in range(total_alimentos):
        if i == 0:
            str_app.markdown(f"🍀 **Alimento Principal #1** (Recebe o saldo de Kcal automaticamente)")
            col_tipo, col_nome, col_ref = str_app.columns([1.5, 3.5, 1.5])
        else:
            str_app.markdown(f"➕ **Alimento Adicional #{i+1}**")
            col_tipo, col_nome, col_kcal, col_ref = str_app.columns([1.5, 3.5, 1.5, 1.5])
            
        with col_tipo:
            tipo = str_app.selectbox("Tipo:", ["Racao", "Sache", "Petisco"], key=f"tipo_e{num_etapa}_a{i}")
            escolhas_tipos.append(tipo)
            
        with col_nome:
            lista = filtrar_alimentos_por_tipo(tipo)
            nomes = [al["nome"] for al in lista] if lista else []
            if nom_sel := (str_app.selectbox("Selecionar Produto:", nomes, key=f"nome_e{num_etapa}_a{i}") if nomes else None):
                escolhas_nomes.append(nom_sel)
                dados_al = next(item for item in lista if item["nome"] == nom_sel)
                escolhas_dados_al.append(dados_al)
            else:
                str_app.warning("Nenhum produto cadastrado.")
                return
                
        if i > 0:
            with col_kcal:
                k_dest = str_app.number_input("Digitar Kcal:", min_value=0.0, max_value=float(nem_meta), value=0.0, step=5.0, key=f"kcal_in_e{num_etapa}_a{i}")
                escolhas_kcal.append(k_dest)
                kcal_outros += k_dest
                
        with col_ref:
            n_ref = str_app.number_input("Refeições/dia:", min_value=1, max_value=6, value=2, key=f"ref_e{num_etapa}_a{i}")
            escolhas_refs.append(n_ref)
            
        str_app.markdown("<br>", unsafe_allow_html=True)

    # Cálculo do saldo do Alimento 1 fora do loop
    kcal_alimento1 = max(0.0, nem_meta - kcal_outros)
    # Insere as kcal do alimento 1 na posição correta (índice 0)
    escolhas_kcal.insert(0, kcal_alimento1)
    
    if kcal_outros > nem_meta:
        str_app.error(f"⚠️ Atenção: As calorias adicionais ({kcal_outros:.1f} kcal) ultrapassaram o teto da dieta!")
    
    str_app.markdown("#### 🎯 Prescrição em Gramas (Destaque Clínico):")
    
    # Loop 2: Calcula e renderiza os resultados visuais em cartões estáticos
    for i in range(total_alimentos):
        v_kcal = escolhas_kcal[i]
        d_al = escolhas_dados_al[i]
        ref_dia = escolhas_refs[i]
        
        g_dia = v_kcal / d_al['em_kcal_g'] if d_al['em_kcal_g'] > 0 else 0.0
        g_ref = g_dia / ref_dia if ref_dia > 0 else 0.0
        
        # UI Premium: Linha de resultado destacada por alimento
        col_txt, col_card1, col_card2 = str_app.columns([2.5, 1, 1])
        with col_txt:
            str_app.info(f"**{escolhas_nomes[i]}** ({escolhas_tipos[i]})\n\n🔋 Energia: **{v_kcal:.1f} kcal** alocadas.")
        with col_card1:
            str_app.metric(label="Qtd. Diária Total", value=f"{g_dia:.1f} g")
        with col_card2:
            str_app.metric(label=f"Por Refeição ({ref_dia}x)", value=f"{g_ref:.1f} g")
            
        # Alimenta a lista para persistência no banco SQLite
        todos_itens_dieta.append({
            "etapa": num_etapa, "tipo": escolhas_tipos[i], "alimento": escolhas_nomes[i], "em_kcal_g": d_al['em_kcal_g'],
            "kcal_destinadas": v_kcal, "quantidade_g_dia": round(g_dia, 2), "n_refeicoes": ref_dia,
            "g_refeicao": round(g_ref, 2), "nem_etapa": nem_meta
        })

    # Barra de progresso final
    total_alocado = sum(escolhas_kcal)
    pct = min(1.0, total_alocado / nem_meta) if nem_meta > 0 else 0.0
    str_app.progress(pct)
    str_app.success(f"✅ Dieta travada com segurança em 100% da meta clínica: {total_alocado:.1f} / {nem_meta} kcal/dia")


# -------------------------------------------------------------------------
# RENDERIZAÇÃO DAS SEÇÕES NA TELA
# -------------------------------------------------------------------------

# --- ETAPA 1 ---
peso_t1 = etapas_info["peso_etapa_1"]
nem_t1 = calcular_nem(especie, is_castrado == 1, peso_t1, faktor_escolhido if 'faktor_escolhido' in locals() else fator_escolhido)

col_btn1, _ = str_app.columns([1.5, 3])
with col_btn1:
    if str_app.button("➕ Adicionar Alimento à Etapa 1", key="btn_e1"):
        str_app.session_state.n_alimentos_etapa1 += 1
        str_app.rerun()

formular_dieta_estabilizada(1, peso_t1, nem_t1, str_app.session_state.n_alimentos_etapa1)

str_app.markdown("---")

# --- ETAPA 2 (SÓ CASO SEJA DIRETRIZ CLÍNICA) ---
if total_etapas == 2:
    peso_t2 = etapas_info["peso_etapa_2"]
    nem_t2 = calcular_nem(especie, is_castrado == 1, peso_t2, fator_escolhido)
    
    col_btn2, _ = str_app.columns([1.5, 3])
    with col_btn2:
        if str_app.button("➕ Adicionar Alimento à Etapa 2", key="btn_e2"):
            str_app.session_state.n_alimentos_etapa2 += 1
            str_app.rerun()
            
    formular_dieta_estabilizada(2, peso_t2, nem_t2, str_app.session_state.n_alimentos_etapa2)
    str_app.markdown("---")


# -------------------------------------------------------------------------
# BOTÃO DE ACÇÃO FINAL
# -------------------------------------------------------------------------
if str_app.button("💾 CONCLUIR E SALVAR PRONTUÁRIO INTEGRADO", use_container_width=True, type="primary"):
    if not id_paciente or not nome_animal or not tutor:
        str_app.error("❌ Erro: Preencha os campos obrigatórios (ID, Nome e Tutor) antes de salvar.")
    else:
        dados_paciente = {
            "id_paciente": id_paciente, "nome_animal": nome_animal, "tutor": tutor,
            "especie": especie, "sexo": sexo, "castrado": is_castrado,
            "peso_atual": peso_atual, "score_corporal": score_corporal,
            "data_avaliacao": datetime.today().strftime('%Y-%m-%d')
        }
        salvar_paciente(dados_paciente)
        salvar_itens_dieta(id_paciente, todos_itens_dieta)
        
        str_app.balloons()
        str_app.success(f"🎉 Excelente! Ficha clínica e as dietas foram gravadas com sucesso no SQLite!")
        
        # Reseta os contadores para o padrão limpo
        str_app.session_state.n_alimentos_etapa1 = 1
        str_app.session_state.n_alimentos_etapa2 = 1
