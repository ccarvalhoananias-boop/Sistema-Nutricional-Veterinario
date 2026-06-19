"""
Engine de Cálculo Nutricional Veterinário.
Contém a lógica de negócio puramente matemática para emagrecimento e ganho de peso.
"""

import math
from typing import Dict, Any, Tuple
from config import SCORE_IDEAL, PERCENTUAL_DESVIO_POR_PONTO, FATORES_NEM, EXPOENTES_NEM, LIMIAR_DUAS_ETAPAS_PCT

def calcular_peso_meta(peso_atual: float, score_corporal: int) -> Tuple[float, float]:
    """
    Calcula o desvio percentual e o peso meta/ideal com base no Score de Condição Corporal.
    
    Exemplo:
        Entrada: peso_atual=12.0, score_corporal=7
        Saída: (20.0, 10.0) -> Significa +20% de desvio e peso meta de 10kg.
    """
    desvio_pct = (score_corporal - SCORE_IDEAL) * PERCENTUAL_DESVIO_POR_PONTO
    peso_meta = peso_atual / (1.0 + (desvio_pct / 100.0))
    return round(desvio_pct, 2), round(peso_meta, 2)


def determinar_etapas(desvio_pct: float, peso_meta: float) -> Dict[str, Any]:
    """
    Determina se o tratamento terá 1 ou 2 etapas e calcula o peso alvo de cada uma.
    Pacientes com desvio acima de 20% fazem a Etapa 1 até atingir o limite seguro de 20%.
    """
    abs_desvio = abs(desvio_pct)
    
    if abs_desvio <= LIMIAR_DUAS_ETAPAS_PCT:
        return {
            "total_etapas": 1,
            "peso_etapa_1": peso_meta,
            "peso_etapa_2": None
        }
    else:
        # Se for emagrecimento (desvio positivo, ex: score 8 = +30%)
        if desvio_pct > 0:
            # Etapa 1 leva o animal até +20% do peso ideal (meta intermediária segura)
            peso_etapa_1 = peso_meta * 1.20
        else: # Se for ganho de peso (desvio negativo, ex: score 3 = -20%)
            peso_etapa_1 = peso_meta * 0.80
            
        return {
            "total_etapas": 2,
            "peso_etapa_1": round(peso_etapa_1, 2),
            "peso_etapa_2": peso_meta
        }


def calcular_nem(especie: str, status_castrado: bool, peso_trabalho: float, fator_escolhido: float) -> float:
    """
    Calcula a Necessidade Energética de Manutenção (NEM) usando o peso da etapa
    e o fator dinâmico definido pelo veterinário.
    
    Fórmula: Fator * (Peso ^ Expoente)
    """
    # Validação simples de segurança
    if especie not in EXPOENTES_NEM:
        raise ValueError(f"Espécie inválida: {especie}. Escolha 'cao' ou 'gato'.")
        
    expoente = EXPOENTES_NEM[especie]
    nem = fator_escolhido * (peso_trabalho ** expoente)
    return round(nem, 2)


def gerar_projeção_semanal(peso_inicial: float, peso_meta: float, taxa_semanal: float = 0.015) -> list:
    """
    Gera uma estimativa de curva de peso semana a semana com o peso esperado de 1% e 2%.
    Interrompe a geração quando o peso esperado cruza ou atinge o peso meta.
    """
    cronograma = []
    semana = 0
    peso_atual_1pct = peso_inicial
    peso_atual_2pct = peso_inicial
    
    # Determina se é emagrecimento ou ganho
    emagrecendo = peso_inicial > peso_meta
    
    # Registra a semana zero (dados atuais)
    cronograma.append({
        "semana": semana,
        "esperado_1pct": round(peso_atual_1pct, 2),
        "esperado_2pct": round(peso_atual_2pct, 2)
    })
    
    # Roda uma simulação de até 52 semanas para evitar loops infinitos
    while semana < 52:
        semana += 1
        if emagrecendo:
            peso_atual_1pct *= 0.99  # Perda de 1%
            peso_atual_2pct *= 0.98  # Perda de 2%
            # Se o ritmo mais lento (1%) atingir a meta, paramos o cronograma
            if peso_atual_1pct <= peso_meta:
                break
        else:
            peso_atual_1pct *= 1.005 # Ganho de 0.5%
            peso_atual_2pct *= 1.01  # Ganho de 1%
            if peso_atual_1pct >= peso_meta:
                break
                
        cronograma.append({
            "semana": semana,
            "esperado_1pct": round(peso_atual_1pct, 2),
            "esperado_2pct": round(peso_atual_2pct, 2)
        })
        
    return cronograma
def obter_limites_fator(especie: str, status_castrado: bool) -> dict:
    """
    Retorna as faixas [min, padrao, max] do fator NEM com base na espécie e castração.
    """
    categoria = "castrado" if status_castrado else "ativo"
    return FATORES_NEM[especie][categoria]