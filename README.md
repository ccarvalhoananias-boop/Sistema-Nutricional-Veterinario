# 🐾 Sistema Nutricional Veterinário — Manejo de Peso

Este é um aplicativo web desenvolvido em Python e Streamlit projetado para auxiliar médicos veterinários no diagnóstico, planejamento e formulação de dietas personalizadas para cães e gatos em tratamento de manejo de peso (sobrepeso, obesidade ou ganho de peso).

## 🚀 Funcionalidades

* **Ficha Clínica Digital:** Cadastro simplificado do paciente (ID, Nome, Tutor, Espécie, Sexo, Status de Castração).
* **Diagnóstico Automático:** Cálculo instantâneo do desvio de peso ideal com base no Score de Condição Corporal (ECC) de 1 a 9.
* **Estipulação de Metas Dinâmicas:** Divisão do tratamento em etapas clínicas automáticas com cálculo do NEM (Necessidade Energética de Manutenção).
* **Formulação de Dieta Inteligente:** Permite a adição de múltiplos alimentos (Ração, Sachê, Petisco) sob demanda com **ajuste calórico em cascata automático** (o alimento principal recalcula seu volume conforme novos itens são adicionados).
* **Dashboard Automatizado:** Integração com o LibreOffice Calc/Excel através da geração automática de uma planilha de indicadores (`dashboard_indicadores.xlsx`) a cada salvamento.
* **Persistência Segura:** Armazenamento local e em nuvem utilizando banco de dados SQLite.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface Web:** Streamlit
* **Processamento de Dados:** Pandas & OpenPyXL
* **Banco de Dados:** SQLite