import datetime
import os

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
# st.markdown(unsafe_allow_html=True)

### Setup do session state para poder baixar a planilha

# if 'planilha' not in st.session_state:
#     st.session_state['planilha'] = 'nao_pronta'

### Abrindo o dataframe e tratando os dados

tabela = 'fundos_thales_st.xlsx'

# df = pd.read_excel(tabela, sheet_name='FII', usecols='A:V')
df = pd.read_excel(tabela)
df_completa = df.copy()
df['DY 12M'] = df['DY 12M']
df['DY 12M'] = df['DY 12M'].fillna(0)
df['P/VP'] = df['Preço'] / df['VP']
df['P/VP'] = df['P/VP'].fillna(0)
df['Dividendo'] = df['Dividendo'].replace('-', 0).fillna(0)

# gestora = df['Gestora'].sort_values().unique().tolist()
# setor = df['Setor'].unique().tolist()
div_yield = df['DY 12M'].unique().tolist()

### Desenhando os elementos

### Barra lateral, onde vão ficar os parâmetros de busca

with st.sidebar:
    dy_min = st.number_input('DY Mínimo', min_value=0.0, step=0.5)
    dy_max = st.number_input('DY Máximo', min_value=0.0, value = 10000.0, step=0.5)

    pvp_min = st.number_input('P/VP Mínimo', min_value=-50.0, step=0.1)
    pvp_max = st.number_input('P/VP Máximo', min_value=0.0, value = 2000.0, step=0.1)
    
    cotistas_min = st.number_input('Mínimo cotistas', min_value=0, value = 0, step = 10000)
    cotistas_max = st.number_input('Máximo cotistas', min_value=0, value = 2000000, step=10000)

    nome_fii = st.text_input('Nome do FII', value='', key='nomefii').upper()
    # nome_gestora = st.text_input('Nome da gestora', value='', key='nomegestora')
    # nome_setor = st.text_input('Setor', value='', key='setor')
    
    carteira = st.checkbox('Em carteira?')

### Montando a máscara de filtro do dataframe

# mask = (df['DY 12M'].between(float(dy_min), float(dy_max))) & (df['P/VP'].between(float(pvp_min), float(pvp_max))) & (df['Ticker'].str.contains(nome_fii)) & (df['Gestora'].str.contains(nome_gestora, case=False)) & (df['Setor'].str.contains(nome_setor, case=False))
mask = (df['DY 12M'].between(float(dy_min), float(dy_max))) & (df['P/VP'].between(float(pvp_min), float(pvp_max))) & (df['Ticker'].str.contains(nome_fii)) & (df['Número de Cotistas'].between(float(cotistas_min), float(cotistas_max)))
# mask = (df['DY 12M'].between(float(dy_min), float(dy_max)))
if carteira:
    mask = (df['Ticker'].isin(['BTLG11',
'HGLG11',
'KNIP11',
'RBRF11',
'RBRR11',
'VSHO11']))

num_resultados = df[mask].shape[0]

### Filtrando o dataframe

df2 = df[mask]

### Desenhando o dataframe filtrado na tela

data_modificacao = datetime.datetime.fromtimestamp(os.path.getmtime(tabela))
st.write(f'Data de atualização da planilha: {data_modificacao}')
st.dataframe(df2.drop(columns=['Relatório', 'Setor']).reset_index(drop=True).style.format({'Preço': 'R$ {:,.2f}', 'VP': 'R$ {:,.2f}', 'Dividendo': 'R$ {:,.2f}', 'DY 12M': '{:.2f} %', 'P/VP': '{:.2f}', 'Número de Cotistas': '{:.0f}', 'Caixa': '{:.2f}', 'DY CAGR 3 Anos': '{:.2f}'}), width='stretch')
st.markdown(f'Total de resultados: {num_resultados}')

### Criando caixa de comentários e sugestões
# df_comentarios = pd.read_excel('comentarios.xlsx')

# form = st.form("comment")
# name = form.text_input("Nome")
# comment = form.text_area("Insira seus comentários/sugestões/críticas")
# submit = form.form_submit_button("Enviar")

# if submit:
#         date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#         df_temp = pd.DataFrame([[name, comment, date]], columns=['nome', 'comentario', 'data'])
#         df_comentarios = pd.concat([df_comentarios, df_temp])
#         try:
#             df_comentarios.to_excel('comentarios.xlsx', index=False)
#         except:
#             pass

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
        
        dividendos = float(value['Dividendo'])
        dividendos_12m = float(value['DY 12M']*value['Preço']/12/100)
        delta_dividendos = dividendos - dividendos_12m
        dy = value['DY 12M']
        
        # col1.write(f'**Gestora:** {value.Gestora}')
        # col1.write(f'**Setor:** {value.Setor}')
        col1.write(f'**Preço:** {value["Preço"]}')
        col1.write(f'**VP:** {value.VP}')
        
        col2.metric(label='Ultimo dividendo', value=f'R$ {dividendos:.2f}', delta=f'{delta_dividendos:.2f}', help='Mostra o último dividendo pago, e sua variação em relação a média dos dividendos pagos nos últimos 12 meses.')
        col2.markdown(f'**Div. Yield:** {dy:.2f} % a.a. (Anualizado)')
        
        if not df_completa[df_completa['Ticker'] == value.Ticker]['Relatório'].isna().any():
            col2.write(f"[Relatório]({df_completa[df_completa['Ticker'] == value.Ticker]['Relatório'][index]})")



