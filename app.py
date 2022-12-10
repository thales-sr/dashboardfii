import pandas as pd
import streamlit as st

### Configuração da página

st.set_page_config(layout="wide", page_title='FIIs')

st.header('Fundos Imobiliários')

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

### Setup do session state para poder baixar a planilha

# if 'planilha' not in st.session_state:
#     st.session_state['planilha'] = 'nao_pronta'

### Abrindo o dataframe e tratando os dados

tabela = 'fiis_thales_2022-12-10.xlsx'

df = pd.read_excel(tabela, sheet_name='FII', usecols='A:V')
df_completa = df.copy()
df['Yield\nAnualiz.(%)'] = df['Yield\nAnualiz.(%)']*100
df.drop(labels=['Divid.\nConsiderado', 'Ônus', 'Link', 'Relatório',
                'Preço Calculado', 'Upside'], axis=1, inplace=True)

df['Yield\nAnualiz.(%)'] = df['Yield\nAnualiz.(%)'].fillna(0)
df['P/VP'] = df['P/VP'].fillna(0)
df['Divid.'] = df['Divid.'].replace('-', 0).fillna(0)
df['Divid.\n12m'] = df['Divid.\n12m'].fillna(0)
df['Gestora'] = df['Gestora'].fillna('')

gestora = df['Gestora'].sort_values().unique().tolist()
setor = df['Setor'].unique().tolist()
div_yield = df['Yield\nAnualiz.(%)'].unique().tolist()

### Desenhando os elementos

### Barra lateral, onde vão ficar os parâmetros de busca

with st.sidebar:
    dy_min = st.number_input('DY Mínimo', min_value=0.0, step=0.5)
    dy_max = st.number_input('DY Máximo', min_value=0.0, value = 10000.0, step=0.5)

    pvp_min = st.number_input('P/VP Mínimo', min_value=0.0, step=0.1)
    pvp_max = st.number_input('P/VP Máximo', min_value=0.0, value = 2000.0, step=0.1)

    nome_fii = st.text_input('Nome do FII', value='', key='nomefii').upper()
    nome_gestora = st.text_input('Nome da gestora', value='', key='nomegestora')
    nome_setor = st.text_input('Setor', value='', key='setor')

### Montando a máscara de filtro do dataframe

mask = (df['Yield\nAnualiz.(%)'].between(float(dy_min), float(dy_max))) & (df['P/VP'].between(float(pvp_min), float(pvp_max))) & (df['Ticker'].str.contains(nome_fii)) & (df['Gestora'].str.contains(nome_gestora, case=False)) & (df['Setor'].str.contains(nome_setor, case=False))
num_resultados = df[mask].shape[0]

### Filtrando o dataframe

df2 = df[mask]

### Desenhando o dataframe filtrado na tela

st.dataframe(df2.drop(columns=['Vac.', 'Inad.', 'Preço\nm2', 'Aluguel\nm2']))
st.markdown(f'Total de resultados: {num_resultados}')

### Função para mudar o session state para aparecer o botão de download da planilha

# def planilha_pronta():
#     df2.to_excel('planilha_dados_fii.xlsx', index=False)
#     st.session_state['planilha'] = 'finalizada'

# st.button('Gerar planilha para download', key='gera_planilha', on_click=planilha_pronta)

### Desenhando o botão para baixar a planilha finalizada

# if st.session_state['planilha'] == 'finalizada':
#     with open('planilha_dados_fii.xlsx', 'rb') as file:
#         btn = st.download_button(
#         label='Baixar dados',
#         data=file,
#         file_name='planilha_fiis.xlsx',
#         mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )

### Desenhando as abas com informações dos FIIs

for index, value in df2.iterrows():
    with st.expander(f'**{value.Ticker}**', expanded=False):
        
        col1, col2 = st.columns([1,1])
        
        dividendos = float(value['Divid.'])
        dividendos_12m = float(value['Divid.\n12m'])
        delta_dividendos = dividendos - dividendos_12m/12
        dy = value['Yield\nAnualiz.(%)']
        
        col1.write(f'**Gestora:** {value.Gestora}')
        col1.write(f'**Setor:** {value.Setor}')
        col1.write(f'**Preço:** {value["Preço atual"]}')
        col1.write(f'**VP:** {value.VP}')
        
        col2.metric(label='Ultimo dividendo', value=f'R$ {dividendos:.2f}', delta=f'{delta_dividendos:.2f}', help='Mostra o último dividendo pago, e sua variação em relação a média dos dividendos pagos nos últimos 12 meses.')
        col2.markdown(f'**Div. Yield:** {dy:.2f} % a.a. (Anualizado)')
        
        if not df_completa[df_completa['Ticker'] == value.Ticker]['Relatório'].isna().any():
            col2.write(f"[Relatório]({df_completa[df_completa['Ticker'] == value.Ticker]['Relatório'][index]})")

