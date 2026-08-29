import pandas as pd
import os

caminho_dados = r'C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\raw'

# 1. Ler a base do SIH da pasta do OneDrive
df_sih = pd.read_csv(os.path.join(caminho_dados, 'sih_sp_consolidado.csv'))
# Lê a base de leitos da pasta atual do Jupyter (onde salvamos no Passo 1)
df_leitos = pd.read_csv('cnes_leitos_sp_tratado.csv')

# Garantir que o Código IBGE seja texto/string sem espaços para o cruzamento perfeito
df_sih['Cod_IBGE'] = df_sih['Cod_IBGE'].astype(str).str.strip()
df_leitos['Cod_IBGE'] = df_leitos['Cod_IBGE'].astype(str).str.strip()

# 2. Fazer o cruzamento (Merge) das internações com a capacidade de leitos
# Usamos left join para manter todos os históricos de internação intactos
df_final = pd.merge(
    df_sih,
    df_leitos[['Cod_IBGE', 'Quantidade_Leitos']],
    on='Cod_IBGE',
    how='left'
)

# Se algum município não tiver leitos registrados no CNES, preenchemos com 0 para não quebrar a conta
df_final['Quantidade_Leitos'] = df_final['Quantidade_Leitos'].fillna(0)

# 3. Calcular o IPA (Índice de Pressão Assistencial)
# Lógica: (Internações / Leitos) * 100. Adicionamos proteção contra divisão por zero.
def calcular_ipa(row):
    if row['Quantidade_Leitos'] > 0:
        return (row['Internacoes'] / row['Quantidade_Leitos']) * 100
    return 0

df_final['IPA'] = df_final.apply(calcular_ipa, axis=1)

# Definir Status de Risco (Regras de Negócio do seu MVP)
def classifica_risco(ipa):
    if ipa > 100:
        return 'Crítico'
    elif ipa >= 75:
        return 'Alerta'
    else:
        return 'Estável'

df_final['Status_Risco'] = df_final['IPA'].apply(classifica_risco)

# Converter a coluna Período para data (ajuda muito o Power BI a reconhecer meses/anos)
df_final['Período'] = pd.to_datetime(df_final['Período'], format='%d/%m/%Y', errors='coerce')

print(f"Base Analítica Final gerada com sucesso! Total de linhas: {len(df_final)}")
display(df_final.head())

# 4. Salvar o arquivo final consolidado que vai pro Power BI
caminho_final = os.path.join(caminho_dados, 'healthops_base_analitica_mvp.csv')
df_final.to_csv(caminho_final, index=False, encoding='utf-8-sig', sep=';')

print(f"\nArquivo final salvo em: {caminho_final}")
