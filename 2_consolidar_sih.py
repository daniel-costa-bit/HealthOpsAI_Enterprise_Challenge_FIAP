import pandas as pd
import glob
import os

# 1. O caminho
caminho_dados = r'C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\raw'
padrao_busca = os.path.join(caminho_dados, 'sih_*.csv')
arquivos_sih = sorted(glob.glob(padrao_busca))

print(f"Total de arquivos SIH encontrados para processamento: {len(arquivos_sih)}")

lista_dfs = []

# 2. Processamento direto
for arquivo in arquivos_sih:
    try:
        # O Pandas já lê as 8 colunas separadas perfeitamente por causa do sep=';'
        df_sih = pd.read_csv(arquivo, sep=';', encoding='latin1')

        # O DATASUS traz o código e o nome juntos na coluna "Município" ("350010 ADAMANTINA")
        # Vamos separar isso em duas colunas novas
        df_sih['Cod_IBGE'] = df_sih['Município'].astype(str).str.split(' ', n=1).str[0]
        df_sih['Nome_Municipio'] = df_sih['Município'].astype(str).str.split(' ', n=1).str[1]

        lista_dfs.append(df_sih)
    except Exception as e:
        print(f"Erro ao processar o arquivo {arquivo}: {e}")

# 3. Consolidação e limpeza final
if len(lista_dfs) > 0:
    df_sih_geral = pd.concat(lista_dfs, ignore_index=True)

    # Filtrar apenas o Estado de São Paulo
    df_sih_sp = df_sih_geral[df_sih_geral['Cod_IBGE'].str.startswith('35')].copy()

    # Converter números (trocando vírgula por ponto e tratando os '-' vazios do DATASUS como zero)
    cols_numericas = ['AIH_aprovadas', 'Internações', 'Dias_permanência', 'Óbitos']
    for col in cols_numericas:
        df_sih_sp[col] = pd.to_numeric(
            df_sih_sp[col].astype(str).str.replace(',', '.').str.replace('-', '0').str.strip(),
            errors='coerce'
        ).fillna(0)

    # Renomeando colunas para facilitar lá no Power BI
    df_sih_sp = df_sih_sp.rename(columns={'Internações': 'Internacoes', 'Dias_permanência': 'Dias_permanencia'})

    # Mantendo apenas o que importa
    colunas_finais = ['Cod_IBGE', 'Nome_Municipio', 'AIH_aprovadas', 'Internacoes', 'Dias_permanencia', 'Óbitos', 'Período']
    df_sih_sp = df_sih_sp[colunas_finais]

    print(f"\nTotal de registros de internações de SP consolidados (36 meses): {len(df_sih_sp)}")
    display(df_sih_sp.head())

    # 4. Salva o CSV final
    caminho_saida = os.path.join(caminho_dados, 'sih_sp_consolidado.csv')
    df_sih_sp.to_csv(caminho_saida, index=False, encoding='utf-8-sig')
    print(f"\nBase de internações consolidada salva com sucesso em: {caminho_saida}")
else:
    print("Nenhum arquivo processado. Verifique o caminho.")
