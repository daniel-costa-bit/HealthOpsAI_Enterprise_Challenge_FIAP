import pandas as pd
import os

caminho_dados = r'C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\raw'

# 1. Carregar a Base Analítica original
caminho_base = os.path.join(caminho_dados, 'healthops_base_analitica_mvp.csv')
df_analitica = pd.read_csv(caminho_base, sep=';')

# 2. Carregar e limpar os dados de População do IBGE (pulando a primeira linha de cabeçalho)
caminho_ibge = os.path.join(caminho_dados, 'ibge_populacao_sp.csv')
df_ibge = pd.read_csv(caminho_ibge, skiprows=1, encoding='utf-8', on_bad_lines='skip')

# Criar um DataFrame auxiliar só com Código IBGE e População
df_pop_limpa = pd.DataFrame()
df_pop_limpa['Cod_IBGE'] = df_ibge.iloc[:, 1].astype(str).str[:6]  # Corta para 6 dígitos
df_pop_limpa['Populacao'] = pd.to_numeric(df_ibge.iloc[:, 7], errors='coerce').fillna(0)

# 3. Cruzar (Merge) a População com a Base Analítica
df_analitica['Cod_IBGE'] = df_analitica['Cod_IBGE'].astype(str).str.strip()
df_analitica_enriquecida = pd.merge(
    df_analitica,
    df_pop_limpa,
    on='Cod_IBGE',
    how='left'
)

# 4. Calcular a Taxa de Internação por 100k habitantes
def taxa_por_100k(row):
    if row['Populacao'] > 0:
        return (row['Internacoes'] / row['Populacao']) * 100000
    return 0

df_analitica_enriquecida['Taxa_Internacao_100k'] = df_analitica_enriquecida.apply(taxa_por_100k, axis=1)

# 5. Salvar e substituir a Base Analítica original com os novos dados
df_analitica_enriquecida.to_csv(caminho_base, index=False, encoding='utf-8-sig', sep=';')

print("SUCESSO! População e Taxa por 100k adicionadas à Base Analítica (Histórica).")
print(f"Total de linhas processadas: {len(df_analitica_enriquecida)}")
display(df_analitica_enriquecida[['Nome_Municipio', 'Internacoes', 'Populacao', 'Taxa_Internacao_100k']].head())
