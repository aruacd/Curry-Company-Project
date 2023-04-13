# ================================================
# Libraries
# ================================================
import pandas as pd
import numpy as np
import re
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️',layout='wide')

# ================================================
# Functions
# ================================================


#####     Esta função tem a responsabilidade de limpeza do dataframe
    
    
#     Tipos de limpeza:
#     1. Remoção dos dados NaN
#     2. Mudança do tipo da coluna de dados
#     3. Remoção dos espaços das variáveis de texto
#     4. Formatação da coluna de datas
#     5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
    
#     Input: Dataframe
#     Output: Dataframe

def clean_code(df1):
       
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

# 
def distance(df1, fig):
    if fig == False:    
        cols = ['Restaurant_latitude','Restaurant_longitude',
             'Delivery_location_latitude','Delivery_location_longitude']

        df1['distance'] = (df1.loc[:,cols]
                          .apply(lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),                                                                                     (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1))

        avg_distance = round(df1['distance'].mean(),2)
        return avg_distance
    
    else:
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']

        df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),           (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)

        avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['distance'],pull=[0,0.1,0])])
        
        return fig        

#
def avg_std_time_delivery(df1, festival, op):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
        Input:
            - df: Dataframe com os dados necessário para o cálculo 
            - op: Tipo de operação precisa ser calculado
                'avg_time': Calcula o tempo médio.
                'sdt_time': Calcula o desvio padrão do tempo. 
        Output: 
            - df: Dataframe com 2 colunas e 1 linha. 
    """       
    df_aux = (df1.loc[:,['Time_taken(min)','Festival']]
             .groupby('Festival')
             .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    df_aux = round(df_aux.loc[df_aux['Festival'] == festival, op],2)


    return df_aux

#
def avg_std_time_graph(df1):
    df_aux=df1.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time(min)','std_time(min)']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time(min)'],error_y=dict(type='data',array=df_aux['std_time(min)'])))
    fig.update_layout(barmode='group')

    return fig

    fig = avg_std_time_graph(df1)
    
#
def avg_std_time_on_traffic(df1):        
    df_aux = (df1.loc[:,['City','Time_taken(min)','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['avg_time','std_time']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig
    

   




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

st.markdown('# Marketplace - Visão Restaurantes')
st.markdown('''___''')

#tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_', '_'])

#with tab1:

# Métricas gerais - Container 1
with st.container():
    st.markdown('## Métricas Gerais')

    col1, col2 = st.columns(2)
    
    with col1:
        delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
        col1.metric('Entregadores únicos',delivery_unique)

    with col2:
        avg_distance = distance(df1, fig=False)
        col2.metric('Distância média Restaurante-Entrega (km)',avg_distance)
 
    # Métricas gerais - Container 2 
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
        col1.metric('Tempo médio de entrega c/ festival (min)',df_aux)
        
    
    with col2:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
        col2.metric('Desvio Padrão de entrega c/ festival (min)',df_aux)  

# Métricas gerais - Container 3
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
        col1.metric('Tempo médio de entrega s/ festival (min)',df_aux)
        
    with col2:
        df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
        col2.metric('Desvio Padrão de entrega s/ festival (min)',df_aux) 
 
    # Container 4
with st.container():
    st.markdown('''___''')
    st.markdown('## Distribução de tempo')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Por cidade')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig,use_container_width=True)
        

    with col2:
        st.markdown('##### Por tipo de entrega')

        df_aux = round(df1.loc[:,['Time_taken(min)','City','Type_of_order']]
                          .groupby(['City','Type_of_order'])
                          .agg({'Time_taken(min)':['mean','std']}),1)
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux,use_container_width=True)

# Container 5
with st.container():
    st.markdown('''___''')

    st.markdown('## Distribuição do tempo de entrega')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('##### Por cidade')
        fig = distance(df1, fig=True)       
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.markdown('##### Por cidade e por tráfego')
        fig = avg_std_time_on_traffic(df1)
        st.plotly_chart(fig,use_container_width=True)
        
        
        
        
