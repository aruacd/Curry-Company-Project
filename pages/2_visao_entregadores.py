# ================================================
# Libraries
# ================================================
import pandas as pd
import re
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵',layout='wide')


# ================================================
# Functions
# ================================================




def clean_code(df1):
    #####     Esta função tem a responsabilidade de limpeza do dataframe
    
    
#     Tipos de limpeza:
#     1. Remoção dos dados NaN
#     2. Mudança do tipo da coluna de dados
#     3. Remoção dos espaços das variáveis de texto
#     4. Formatação da coluna de datas
#     5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
    
#     Input: Dataframe
#     Output: Dataframe
       
    # 1. Remover espaco das strings
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()

    # 2. Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    # 3. Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 4. Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 5. Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # 6. Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 7. Remove as linhas da culuna Road_traffic_density que tenham o 
    # conteudo igual a 'NaN'
    linhas_nvazias = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_nvazias,:]

    # 8.Remove as linhas da culuna City que tenham o 
    # conteudo igual a 'NaN'
    linhas_nvazias = df['City'] != 'NaN'
    df1 = df1.loc[linhas_nvazias,:]

    # 9.Remove as linhas da culuna Festival que tenham o 
    # conteudo igual a 'NaN'
    linhas_nvazias = df1['Festival'] != 'NaN'
    df1 = df1.loc[linhas_nvazias,:]

    # 10. Comandos para remover o texto '(min) da coluna Time_taken(min) e transformar em int
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1


##### Estas Funções são responsáveis pela construção e exibição dos Gráficos

# Top entregadores mais lentos
def top_delivers(df1, top_asc):
    df2 =    round((df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]   
                       .groupby(['City','Delivery_person_ID'])
                       .mean()
                       .sort_values(['City','Time_taken(min)'],ascending=top_asc)
                       .reset_index()),0)

    df_aux01 = df2.loc[df2['City']=='Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City']=='Urban',:].head(10)
    df_aux03 = df2.loc[df2['City']=='Semi-Urban',:].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index()
    df3 = df3.drop(columns=['index'])

    return df3

# ================================= Início da Estrutura Lógica do Código =========================

# =================================
# Import dataset
# =================================
df = pd.read_csv('dataset/train.csv')

# =================================
# Limpando os dados
# =================================
df1 = clean_code(df)

# ================================================================
# Barra Lateral
# ================================================================

#image_path = 'logo2.png'
image = Image.open('logo2.png')
st.sidebar.image( image, width=120)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low','Medium','High', 'Jam'],
    default=['Low','Medium','High', 'Jam'])

# wheater_options = st.sidebar.multiselect(
#     'Quais as condições climáticas?',
#     ['Cloudy','Fog','Sandstorms', 'Stormy', 'Sunny', 'Windy'],
#     default=['Cloudy','Fog','Sandstorms', 'Stormy', 'Sunny', 'Windy'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Aruã Dias')

# filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas,:]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

# # filtro condição climática
# linhas_selecionadas = df1['Weatherconditions'].isin(wheater_options)
# df1 = df1.loc[linhas_selecionadas,:]

# ================================================================
# Layout do Streamlit
# ================================================================

st.markdown('# Marketplace - Visão entregadores')
st.markdown('''___''')

#tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_', '_'])

#with tab1:
with st.container():
    st.markdown('## Métricas de Idade e Condição de Veículo')
    col1, col2, col3, col4 = st.columns( 4, gap='large' )
    with col1:
        # maior idade dos entregadores
        maior = df1.loc[:,'Delivery_person_Age'].max()

        print(f'O entregador de maior idade é {maior}')
        col1.metric('Maior idade', maior)

    with col2:
        # menor idade dos entregadores
        menor = df1.loc[:,'Delivery_person_Age'].min()

        print(f'O entregador de menor idade é {menor}')
        col2.metric('Menor idade', menor)

    with col3:
        # melhor condição de veículo
        melhor = df1.loc[:,'Vehicle_condition'].max()

        print(f'A melhor condição de veículo é {melhor}')
        col3.metric('Melhor condição', melhor)

    with col4:
        # pior condição de veículo
        pior = df1.loc[:,'Vehicle_condition'].min()

        print(f'A pior condição de veículo é {pior}')
        col4.metric('Pior condição', pior)

with st.container():
    st.markdown('''---''')
    st.markdown('## Avaliações')

    col1, col2 = st.columns(2)

    with col1:
        ## Avaliação média por entregador
        st.markdown('##### Médias por Entregador')

        df_aux = (df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                     .groupby('Delivery_person_ID')
                     .mean()
                     .sort_values('Delivery_person_Ratings',ascending=False)
                     .reset_index() )        
        df_aux.rename(columns={'Delivery_person_Ratings':'Average_rating'}, inplace=True)

        st.dataframe(df_aux)

    with col2:
        ## Avaliação média por trânsito
        st.markdown('##### Médias por Trânsito')

        cols = ['Delivery_person_Ratings','Road_traffic_density']

        # agrupando com as 2 colunas (mean e std) no mesmo dataframe, usando a função de agregação .agg
        df_avg_std_ratings_by_traffic = (df1.loc[:,cols].groupby('Road_traffic_density')
                                                        .agg({'Delivery_person_Ratings':['mean','std']}))

        # mudança de nome das colunas
        df_avg_std_ratings_by_traffic.columns = ['delivery_mean','delivery_std']

        # reset do index (para ajeitar o df)
        df_avg_std_ratings_by_traffic = df_avg_std_ratings_by_traffic.reset_index()

        st.dataframe(df_avg_std_ratings_by_traffic)            

        ## Avaliação média por clima
        st.markdown('##### Médias por Clima')

        cols = ['Delivery_person_Ratings','Weatherconditions']

        # agrupando com as 2 colunas (mean e std) no mesmo dataframe, usando a função de agregação .agg
        df_avg_std_rating_by_weathercond =   (df1.loc[:,cols]
                                                .groupby('Weatherconditions')
                                                .agg({'Delivery_person_Ratings':['mean','std']}))

        # mudança de nome das colunas
        df_avg_std_rating_by_weathercond.columns = ['delivery_mean','delivery_std']

        # reset do index (para ajeitar o df)
        df_avg_std_rating_by_weathercond = df_avg_std_rating_by_weathercond.reset_index()

        st.dataframe(df_avg_std_rating_by_weathercond)

with st.container():
    st.markdown('''---''')
    st.markdown('## Velocidade de Entrega')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('##### Top entregadores mais rápidos por cidade')
        df3 = top_delivers (df1, top_asc=True)
        st.dataframe(df3)


    with col2:
        st.markdown('##### Top entregadores mais lentos por cidade')
        df3 = top_delivers (df1, top_asc=False)
        st.dataframe(df3)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
            
            
            
            
