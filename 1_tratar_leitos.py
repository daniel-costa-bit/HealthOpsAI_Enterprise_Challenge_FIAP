import pandas as pd

# 1. Carregar a base de leitos
caminho = r'C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\raw\cnes_leitos_sp.csv'
df_leitos = pd.read_csv(caminho, sep=';', encoding='latin1')

# 2. Separar o código do IBGE e o nome do município
df_leitos['Cod_IBGE'] = df_leitos['Município'].astype(str).str.split(' ').str[0]
df_leitos['Nome_Municipio'] = df_leitos['Município'].astype(str).str.split(' ', n=1).str[1]
df_leitos['Quantidade_Leitos'] = pd.to_numeric(df_leitos['Quantidade_existente'], errors='coerce').fillna(0)

# 3. Filtrar APENAS os municípios de São Paulo (código IBGE começa com '35')
df_leitos_sp = df_leitos[df_leitos['Cod_IBGE'].str.startswith('35')].copy()
df_leitos_sp = df_leitos_sp[['Cod_IBGE', 'Nome_Municipio', 'Quantidade_Leitos']]

print(f"Total de municípios de SP encontrados: {len(df_leitos_sp)}")
print("Soma total de leitos em SP:", df_leitos_sp['Quantidade_Leitos'].sum())

# 4. Salvar o arquivo limpo
df_leitos_sp.to_csv('cnes_leitos_sp_tratado.csv', index=False, encoding='utf-8-sig')
print("\nBase tratada salva com sucesso como 'cnes_leitos_sp_tratado.csv'!")
