"""
Configurações Globais e Constantes do Sistema Nutricional Veterinário.
Centraliza fatores de cálculo, limites de escore e regras de negócio.
"""

# Constantes de Score de Condição Corporal (ECC / BCS)
SCORE_IDEAL = 5
PERCENTUAL_DESVIO_POR_PONTO = 10.0  # Cada ponto longe do ideal representa 10% de desvio

# Fatores Dinâmicos para o cálculo do NEM (Necessidade Energética de Manutenção)
# Agora estruturado em intervalos: [Mínimo, Padrão/Sugerido, Máximo]
FATORES_NEM = {
    "cao": {
        "ativo": {
            "min": 110.0,
            "padrao": 130.0,
            "max": 140.0
        },
        "castrado": {
            "min": 80.0,
            "padrao": 90.0,
            "max": 100.0
        }
    },
    "gato": {
        "ativo": {
            "min": 90.0,
            "padrao": 100.0,
            "max": 120.0
        },
        "castrado": {
            "min": 70.0,
            "padrao": 75.0,
            "max": 85.0
        }
    }
}

# Expoentes da fórmula do NEM por espécie
EXPOENTES_NEM = {
    "cao": 0.75,
    "gato": 0.67
}

# Parâmetros de Manejo de Peso (Percentuais de perda/ganho semanais baseados no peso atual)
MANEJO_PESO = {
    "emagrecimento": {
        "taxa_min_semanal": 0.01,  # 1% ao menos
        "taxa_max_semanal": 0.02,  # 2% no máximo
    },
    "ganho": {
        "taxa_min_semanal": 0.005, # 0.5% ao menos
        "taxa_max_semanal": 0.010, # 1% no máximo
    }
}

# Regra de Etapas: Limiar de desvio para fracionar o tratamento em 2 etapas
LIMIAR_DUAS_ETAPAS_PCT = 20.0