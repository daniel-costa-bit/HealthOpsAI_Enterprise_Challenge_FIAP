# HealthOps AI - Sprint 2 (MVP) 🏥💡

Bem-vindo ao repositório do MVP do **HealthOps AI**, um centro inteligente de monitoramento da capacidade hospitalar desenvolvido para o Challenge FIAP/Oracle.

## 🚀 Sobre o Projeto
O HealthOps AI resolve o problema da superlotação hospitalar atuando de forma preditiva. Em vez de painéis reativos, nossa solução cruza dados abertos do DATASUS (SIH e CNES) e aplica inteligência artificial (Machine Learning) para classificar o risco de colapso de cada região através de um indicador próprio: o **Índice de Pressão Assistencial (IPA)**.

## ⚙️ Arquitetura e Pipeline de Dados implementados:
1. **Extração:** 36 meses de série histórica do SIH (Internações), IBGE e CNES (Leitos).
2. **Transformação (ETL):** Scripts em Python e Pandas que unificam mais de 11.000 registros, higienizam os dados e preparam as features.
3. **Modelagem de IA:** Utilizamos `RandomForestRegressor` (Scikit-Learn) para prever a tendência de internações futuras, atingindo um MAE (Erro Médio) excelente.
4. **Visualização:** Os CSVs finais da pasta `processed` alimentam nossos Dashboards analíticos.

## 📂 Estrutura das Pastas
* `/data/raw`: Os microdados brutos e intocados direto das fontes oficiais (CNES, IBGE e DATASUS).
* `/data/processed`: Arquivos higienizados (Base Mestra) e o output do modelo preditivo prontos para consumo do BI.
* `/src`: Os scripts Python de ETL e o modelo preditivo (`modelo_preditivo.py`).
* `/PowerBI`: O próprio dashboard com os scripts de criação e ajustes. 

## 💻 Como executar
1. Instale as dependências com `pip install -r requirements.txt`.
2. Rode os scripts na pasta `/src` em sequência.

*Equipe HealthOps AI: Beatriz, Daniel, Geovanna, Isabela e Karina.*
