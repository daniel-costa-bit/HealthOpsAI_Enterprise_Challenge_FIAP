import pandas as pd
import os
from pandas.tseries.offsets import DateOffset

# 1. Caminho e carregamento da base
caminho_dados = r'C:\Users\biama\OneDrive\Documentos\HealthOps-AI\data\raw'
arquivo_base = os.path.join(caminho_dados, 'healthops_base_analitica_mvp.csv')

df = pd.read_csv(arquivo_base, sep=';')
df['Período'] = pd.to_datetime(df['Período'])

# Criar a coluna de classificação para o Power BI
df['Tipo_Dado'] = 'Realizado'

print("Calculando projeções preditivas para os próximos 6 meses...")

# 2. Descobrir o último mês da nossa base (para começar a projetar a partir dali)
ultimo_mes = df['Período'].max()

# 3. Calcular o comportamento recente de cada município (Média Móvel e Últimos Leitos)
resumo_municipios = df.groupby(['Cod_IBGE', 'Nome_Municipio']).agg(
    Media_Internacoes=('Internacoes', lambda x: x.tail(6).mean()),  # Média dos últimos 6 meses
    Leitos_Atuais=('Quantidade_Leitos', 'last')  # Leitos atuais
).reset_index()

# 4. Gerar os dados do futuro (Próximos 6 meses)
projecoes = []

for i in range(1, 7):
    mes_futuro = ultimo_mes + DateOffset(months=i)

    for _, row in resumo_municipios.iterrows():
        # Lógica Preditiva do MVP: Média histórica + tendência de aumento de 2% ao mês
        fator_crescimento = 1 + (0.02 * i)
        internacoes_projetadas = int(row['Media_Internacoes'] * fator_crescimento)

        # Ignorar municípios que não tiveram histórico de internação
        if internacoes_projetadas > 0:
            projecoes.append({
                'Cod_IBGE': row['Cod_IBGE'],
                'Nome_Municipio': row['Nome_Municipio'],
                'AIH_aprovadas': internacoes_projetadas,
                'Internacoes': internacoes_projetadas,
                'Dias_permanencia': internacoes_projetadas * 4,  # Estimativa: 4 dias por paciente
                'Óbitos': int(internacoes_projetadas * 0.05),  # Estimativa: taxa de 5%
                'Período': mes_futuro,
                'Quantidade_Leitos': row['Leitos_Atuais'],
                'Tipo_Dado': 'Projetado'
            })

df_projecoes = pd.DataFrame(projecoes)

# 5. Calcular o IPA e o Status de Risco PREDITIVOS
df_projecoes['IPA'] = df_projecoes.apply(
    lambda r: (r['Internacoes'] / r['Quantidade_Leitos'] * 100) if r['Quantidade_Leitos'] > 0 else 0, axis=1
)

def classifica_risco(ipa):
    if ipa > 100: return 'Crítico'
    elif ipa >= 75: return 'Alerta'
    else: return 'Estável'

df_projecoes['Status_Risco'] = df_projecoes['IPA'].apply(classifica_risco)

# 6. Unir o Passado (Realizado) com o Futuro (Projetado)
df_final_completo = pd.concat([df, df_projecoes], ignore_index=True)

# 7. Salvar a super base mestre
caminho_projecao = os.path.join(caminho_dados, 'healthops_base_completa_com_projecoes.csv')
df_final_completo.to_csv(caminho_projecao, index=False, encoding='utf-8-sig', sep=';')

print(f"\nSucesso! Foram geradas {len(df_projecoes)} linhas de projeções futuras.")
print(f"Base Mestre com IA Preditiva salva em: {caminho_projecao}")
