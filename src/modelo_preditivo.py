import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import os

# 1. Carregando a Base Analítica Final (Que geramos na etapa 6)
caminho_base = r"C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\processed\healthops_base_analitica_mvp.csv"
df = pd.read_csv(caminho_base, sep=';', encoding='utf-8-sig')

# Como o modelo de ML não entende strings como "01/05/2025", 
# precisamos extrair componentes temporais que ele entenda (Mês e Ano).
# Aqui vamos usar o truque do nome do arquivo, que já tem o ano e o mês limpos: 'sih_2025_05.csv'
df['Ano'] = df['Arquivo_Origem'].str.extract(r'(\d{4})').astype(float)
df['Mes'] = df['Arquivo_Origem'].str.extract(r'_(\d{2})\.csv').astype(float)

# Limpando eventuais NaNs antes de treinar
df = df.dropna(subset=['Ano', 'Mes', 'Total_Internacoes', 'Populacao', 'Quantidade_Leitos'])

# 2. Engenharia de Features (Escolhendo as variáveis que ensinam o modelo)
# Vamos tentar prever as 'Total_Internacoes' baseando-se no tempo e estrutura
features = ['Ano', 'Mes', 'Populacao', 'Quantidade_Leitos']
target = 'Total_Internacoes'

X = df[features]
y = df[target]

# 3. Divisão Treino e Teste (80% para aprender, 20% para validar)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Treinando o Modelo Preditivo (Random Forest)
print("Treinando o modelo de Inteligência Artificial (Random Forest)...")
modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
modelo_rf.fit(X_train, y_train)

# 5. Avaliando a Precisão do Modelo
previsoes = modelo_rf.predict(X_test)
mae = mean_absolute_error(y_test, previsoes)
rmse = np.sqrt(mean_squared_error(y_test, previsoes))

print(f"\n--- AVALIAÇÃO DO MODELO ---")
print(f"Erro Médio Absoluto (MAE): {mae:.2f} internações (Margem de erro)")
print(f"Raiz do Erro Quadrático Médio (RMSE): {rmse:.2f}")

# 6. Gerando o Dataset de Projeção para o Dashboard (Próximos 3 meses)
# Vamos pegar a situação atual dos leitos e população e projetar os próximos meses (ex: Janeiro, Fevereiro, Março de 2026/2027)
print("\nGerando cenário preditivo para o futuro...")
cidades_distintas = df[['IBGE', 'Nome_Municipio', 'Populacao', 'Quantidade_Leitos']].drop_duplicates()

# Projetando para, digamos, Mês 10, 11 e 12 do Ano atual + 1 (Para termos dados para o Power BI)
ano_futuro = df['Ano'].max() + 1
meses_futuros = [1, 2, 3] # Previsão para os primeiros meses do ano que vem

projecoes = []

for mes in meses_futuros:
    # Criamos um DataFrame fake com as mesmas features, mas tempo futuro
    df_futuro = cidades_distintas.copy()
    df_futuro['Ano'] = ano_futuro
    df_futuro['Mes'] = mes
    
    # Previsão!
    X_futuro = df_futuro[['Ano', 'Mes', 'Populacao', 'Quantidade_Leitos']]
    df_futuro['Previsao_Internacoes'] = modelo_rf.predict(X_futuro).round(0).astype(int)
    
    # Adicionamos na lista
    projecoes.append(df_futuro)

df_projecoes = pd.concat(projecoes, ignore_index=True)

# 7. Exportando o output do modelo Preditivo para uso no Dashboard!
caminho_projecoes = r"C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\processed\healthops_projecoes.csv"
df_projecoes.to_csv(caminho_projecoes, index=False, sep=';', encoding='utf-8-sig')

print(f"\nProjeções salvas com sucesso em: {caminho_projecoes}")
print("\n--- AMOSTRA DAS PREVISÕES DA IA ---")
display(df_projecoes.sort_values(by='Previsao_Internacoes', ascending=False).head(5))
