import pandas as pd
import os

caminho_dados = r'C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\raw'

# 1. Carregar a Base Mestre (com histórico e projeções)
caminho_projecao = os.path.join(caminho_dados, 'healthops_base_completa_com_projecoes.csv')
df_mestre = pd.read_csv(caminho_projecao, sep=';')

# 2. Carregar e Limpar os dados de População do IBGE
# A base do IBGE tem um título na primeira linha, então pulamos ela (skiprows=1)
caminho_ibge = os.path.join(caminho_dados, 'ibge_populacao_sp.csv')
df_ibge = pd.read_csv(caminho_ibge, skiprows=1, encoding='utf-8', on_bad_lines='skip')

# Criando um DataFrame limpo apenas com o que importa do IBGE
df_pop_limpa = pd.DataFrame()

# O IBGE usa código de 7 dígitos (ex: 3500105), mas o DATASUS usa 6 (ex: 350010)
# Vamos cortar o último dígito para que o cruzamento (PROCV) funcione perfeitamente!
df_pop_limpa['Cod_IBGE'] = df_ibge.iloc[:, 1].astype(str).str[:6]

# Pegando a "População estimada [2025]" (que está na 8ª coluna, índice 7 do Pandas)
df_pop_limpa['Populacao'] = pd.to_numeric(df_ibge.iloc[:, 7], errors='coerce').fillna(0)

# 3. Cruzar a População com a Base Mestre
df_mestre['Cod_IBGE'] = df_mestre['Cod_IBGE'].astype(str).str.strip()
df_final_enriquecido = pd.merge(
    df_mestre,
    df_pop_limpa,
    on='Cod_IBGE',
    how='left'
)

# 4. Criar a Métrica de Ouro da Saúde Pública (Internações por 100 mil habitantes)
# Isso nivela municípios grandes e pequenos na mesma régua!
def taxa_por_100k(row):
    if row['Populacao'] > 0:
        return (row['Internacoes'] / row['Populacao']) * 100000
    return 0

df_final_enriquecido['Taxa_Internacao_100k'] = df_final_enriquecido.apply(taxa_por_100k, axis=1)

# 5. Salvar a base hiper-enriquecida
caminho_saida_final = os.path.join(caminho_dados, 'healthops_base_completa_com_projecoes.csv')
df_final_enriquecido.to_csv(caminho_saida_final, index=False, encoding='utf-8-sig', sep=';')

print("SUCESSO! População adicionada à base de dados.")
print(f"Total de linhas processadas: {len(df_final_enriquecido)}")
display(df_final_enriquecido[['Nome_Municipio', 'Tipo_Dado', 'Internacoes', 'Populacao', 'Taxa_Internacao_100k']].head())
