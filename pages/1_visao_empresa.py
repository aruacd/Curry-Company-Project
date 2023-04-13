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

st.set_page_config(page_title='Visão Empresa', page_icon='📈',layout='wide')

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

# 1. Pedidos por dia (Gráfico barras)
def order_metric(df1):    
    df_aux = (df1.loc[:,['ID','Order_Date']]
                .groupby('Order_Date')
                .count()
                .reset_index())

    fig = px.bar(df_aux,x='Order_Date',y='ID')

    return fig

# 2. Essa função cria e exibe o gráfico de setores (pizza) do Volume de pedidos por Tráfego
def traffic_order_share(df1):
    df_aux = (df1.loc[:,['ID','Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())

    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()

    fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')

    return fig

# 3. Essa função cria e exibe o gráfico de bolhas do Volume de pedidos Por Cidade e Tráfego
def traffic_order_city(df1):      
    df_aux = (df1.loc[:,['ID', 'City', 'Road_traffic_density']]
                 .groupby(['City','Road_traffic_density'])
                 .count()
                 .reset_index())

    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

# 4. Essa função cria e exibe o gráfico de linhas da relação Quantidade de Entregas/Semana
def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    df_aux = (df1.loc[:,['ID','week_of_year']]
                .groupby('week_of_year')
                .count()
                .reset_index())

    fig = px.line(df_aux,x='week_of_year',y='ID')
    return fig

# 5. Essa função cria e exibe o gráfico de linhas da relação quantidade de pedidos por semana / quantidade de entregadores por semana
def order_share_by_week(df1):
    df_aux01 = (df1.loc[:,['ID','week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index())
    df_aux02 = (df1.loc[:,['Delivery_person_ID','week_of_year']]
                  .groupby('week_of_year')
                  .nunique()
                  .reset_index())

    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_delivery_person'] = round(df_aux['ID']/df_aux['Delivery_person_ID'],0)

    fig = px.line(df_aux, x = 'week_of_year', y = 'order_by_delivery_person')
    return fig

# 6.Essa função cria e exibe o mapa com as marcações de densidade de tráfego médio por cidade
def country_map(df1):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = (df1.loc[:,cols]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())

    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                     popup=location_info[['City','Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600,)

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

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Aruã Dias')

# filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas,:]

#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

# ================================================================
# Layout do Streamlit
# ================================================================

st.markdown('# Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order metric
        fig = order_metric(df1)
        st.markdown('## Quantidade de Pedidos/Dia')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():   
        st.markdown('## Volume de pedidos')
        col1, col2 = st.columns(2)
        
        with col1:
            # Percentual de pedidos por táfego (Gráfico pizza)
            fig = traffic_order_share(df1)
            st.markdown('### Por Tráfego')
            st.plotly_chart(fig, use_container_width=True)            

        with col2:
            # Volume de pedidos por cidade e por táfego (Gráfico bolhas)
            st.markdown('### Por Cidade e Tráfego')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)               
    
with tab2:
    with st.container():
        st.markdown('## Quantidade de Entregas/Semana')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
          
    with st.container():
        st.markdown('## Quantidade Entrega/Entregador por Semana ')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
    
with tab3:
    st.markdown('## Localização Central de Densidade de Tráfego por cidade')
    country_map(df1)

    



