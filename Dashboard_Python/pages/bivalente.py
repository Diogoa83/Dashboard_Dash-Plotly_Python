import dash
from dash import html, dcc, Input, Output, State, callback, Dash, register_page, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import json


# importando tabelas do indexprincipal.py
from perfomace import df_municipio, df_regiao, df_tabela_populacao_municipio, populacao_total_bivalente



register_page(__name__, path='/')

########################### CONEXAO TABELA IMUNIZAÇÃO ###########################

df_municipio = df_municipio.copy()
df_regiao = df_regiao.copy()
df_tabela_populacao_municipio = df_tabela_populacao_municipio.copy()
populacao_total_bivalente = populacao_total_bivalente.copy()


# calculo população regional por sexo e total
#tabela_populacao_regiao = df_tabela_populacao_regiao[df_tabela_populacao_regiao['dose']=='1ª DOSE']
#tabela_populacao_regiao = tabela_populacao_regiao[['regiao_saude', 'sexo', 'pop', 'total']]

# calculo população municipios por sexo e total
tabela_populacao_municipio = df_tabela_populacao_municipio[['regiao_saude','municipio_paciente', 'sexo', 'dose', 'pop', 'total']]


tabela_populacao_municipio = tabela_populacao_municipio.rename(columns={
    'regiao_saude':'Região Saúde',
    'municipio_paciente':'Município',
    'dose':'Dose',
    'sexo':'Sexo',
    'pop':'População Sexo',
    'total':'População'
})

# remover as acentuações dos municipios para que fique compativel com as outras colunas de Município que não tem acentuações nos nomes


df_municipio = df_municipio.rename(columns={'regiao_saude':'Região Saúde','municipio':'Município', 'sexo':'Sexo', 'pop':'População', 'contagem_dose':'Número de Vacinas', 'porcentagem':'Porcentagem (%)', 'faixa_etaria':'Faixa Etária'})

#df_regiao = df_regiao.rename (columns={'regiao_saude':'Região Saúde', 'sexo':'Sexo', 'pop':'População', 'contagem_dose':'Número de Vacinas', 'porcentagem':'Porcentagem (%)', 'faixa_etaria':'Faixa Etária'})


df_regiao = df_municipio.groupby(['Região Saúde', 'Faixa Etária', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
df_regiao['Porcentagem (%)'] = round(df_regiao['Número de Vacinas']/ df_regiao['População']*100,2)



tooltip_mapa_regiao2 = df_municipio.groupby(['Região Saúde']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
tooltip_mapa_regiao2['Porcentagem (%)'] = round(tooltip_mapa_regiao2['Número de Vacinas']/ tooltip_mapa_regiao2['População']*100,2)


tabela_regiao_ = df_municipio.groupby(['Região Saúde', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
tabela_regiao_['Porcentagem (%)'] = round(tabela_regiao_['Número de Vacinas']/ tabela_regiao_['População']*100,2)



tooltip_mapa_regiao2.loc[:,'Número de Vacinas '] = tooltip_mapa_regiao2['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tooltip_mapa_regiao2.loc[:,'População '] = tooltip_mapa_regiao2['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

tabela_municipio = df_municipio[['Município', 'Sexo', 'Faixa Etária' ,'População', 'Número de Vacinas','Porcentagem (%)']]

tabela_para_municipio = df_municipio[['Município', 'Sexo', 'Faixa Etária' ,'População', 'Número de Vacinas','Porcentagem (%)']].copy()
tabela_para_regiao = df_regiao.copy()

tooltip_regiao_contagemdoses = df_regiao.groupby(['Região Saúde'])['Número de Vacinas'].sum().reset_index()

tabela_mapa = df_municipio.groupby(['Município']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
tabela_mapa['Porcentagem (%)'] = round(tabela_mapa['Número de Vacinas']/tabela_mapa['População']*100,2)

tabela_ = df_municipio.groupby(['Município', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
tabela_['Porcentagem (%)'] = round(tabela_['Número de Vacinas']/tabela_['População']*100,2)


tabela_mapa.loc[:,'População '] = tabela_mapa['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_mapa.loc[:,'Número de Vacinas '] = tabela_mapa['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


cobertura = df_regiao.groupby(['Faixa Etária', 'Sexo']).agg({'População':'sum','Número de Vacinas':'sum'}).reset_index()
cobertura['Porcentagem (%)'] = round(cobertura['Número de Vacinas']/cobertura['População']*100,2)

cobertura2 = cobertura.groupby(['Faixa Etária', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
cobertura2['Porcentagem (%)'] = round(cobertura2['Número de Vacinas']/ cobertura2['População']*100,2)

cobertura3 = df_regiao.groupby(['Região Saúde', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
cobertura3['Porcentagem (%)'] = round(cobertura3['Número de Vacinas']/ cobertura3['População']*100,2)
cobertura3 = cobertura3[['Região Saúde', 'Sexo', 'Porcentagem (%)']]




# toda SC
cobertura7 = df_municipio.groupby(['Faixa Etária', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
cobertura7['Porcentagem (%)'] = round(cobertura7['Número de Vacinas']/ cobertura7['População']*100,2)

# por municipio
cobertura8 = df_municipio.groupby(['Região Saúde','Município', 'Sexo']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
cobertura8['Porcentagem (%)'] = round(cobertura8['Número de Vacinas']/ cobertura8['População']*100,2)
cobertura8 = cobertura8[['Região Saúde','Município', 'Sexo', 'Porcentagem (%)']]

# toda SC
cobertura9 = df_municipio.groupby(['Município','Sexo', 'Faixa Etária']).agg({'População':'sum', 'Número de Vacinas':'sum'}).reset_index()
cobertura9['Porcentagem (%)'] = round(cobertura9['Número de Vacinas']/ cobertura9['População']*100,2)


populacao_total_bivalente['pop'] = populacao_total_bivalente['pop'].astype(int)

                                            ################################# GRAFICOS ###########################
                                            ################################# GRAFICOS ###########################
                                            ################################# GRAFICOS ###########################
                                            ################################# GRAFICOS ###########################


# ========== Styles ============ #
tab_card = {'height': '100%'}



config_graph={"displayModeBar": False, "showTips": False, 'scrollZoom': False, "showTips": True}

# ========== TRATAMENTO DOS DADOS  ============ #
 

# transformação json para municipio
# Carregar os dados do GeoJSON
geojson_path = r"SC2.json"
with open(geojson_path, 'r', encoding='utf-8') as geojson_file:
    geojson_data = json.load(geojson_file)
geojson_df = pd.DataFrame(geojson_data['features'])
# Extrair as propriedades e converter para maiúsculas mantendo acentos
geojson_df['properties'] = geojson_df['properties'].apply(lambda prop: {k: v.upper() if isinstance(v, str) else v for k, v in prop.items()})
geojson_df['GEOCODIGO'] = geojson_df['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df['Município'] = geojson_df['properties'].apply(lambda x: x.get('Município'))
geojson_df
merged_data = pd.merge(tabela_mapa, geojson_df, left_on='Município', right_on='Município', how='left')


gdf_geojson = gpd.GeoDataFrame.from_features(geojson_data['features'])
gdf_geojson.crs = 'EPSG:4326'
gdf_geojson['Município'] = gdf_geojson['Município'].str.upper()
gdf_geojson = gdf_geojson.merge(merged_data, left_on='Município', right_on='Município', how='left')
gdf_geojson
gdf_geojson = gpd.GeoDataFrame(gdf_geojson, geometry='geometry_x', crs='EPSG:4326')
geojson_for_plot = json.loads(gdf_geojson.to_json())




# transformação json para regiao
geojson_path2 = r"REGIAO_SAUDE_SC_17.geojson"
with open(geojson_path2, 'r', encoding='utf-8') as geojson_file2:
    geojson_data2 = json.load(geojson_file2)
geojson_df2 = pd.DataFrame(geojson_data2['features'])
geojson_df2['GEOCODIGO'] = geojson_df2['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df2['REGIAO_SAU'] = geojson_df2['properties'].apply(lambda x: x.get('REGIAO_SAU'))
geojson_df2['coordinates'] = geojson_df2['geometry'].apply(lambda x: x.get('coordinates'))
geojson_df2['GEOCODIGO'] = geojson_df2['GEOCODIGO'].astype(str)
geojson_df2 = geojson_df2.rename(columns={'REGIAO_SAU':'Região Saúde'})

merged_data2 = pd.merge(left=tooltip_mapa_regiao2, right=geojson_df2, left_on='Região Saúde', right_on='Região Saúde', how='left')
gdf_geojson2 = gpd.GeoDataFrame.from_features(geojson_data2['features'])
gdf_geojson2.crs = 'EPSG:4326'
gdf_geojson2['GEOCODIGO'] = gdf_geojson2['GEOCODIGO'].astype(str)
merged_data2['GEOCODIGO'] = merged_data2['GEOCODIGO'].astype(str)
gdf_geojson2 = gdf_geojson2.merge(merged_data2, left_on='GEOCODIGO', right_on='GEOCODIGO', how='left')
gdf_geojson2 = gpd.GeoDataFrame(gdf_geojson2, geometry='geometry_x', crs='EPSG:4326')
geojson_for_plot2 = json.loads(gdf_geojson2.to_json())
gdf_geojson2
# # # =============================================================== # SELECT BOX # =============================================================== #

# Criar a lista de opções para o Dropdown
municipio_options = [{'label': municipio, 'value': municipio} for municipio in sorted(tabela_municipio['Município'].unique())]
dropdown_municipios = dcc.Dropdown(
    id='select-municipio-bivalente',
    options=municipio_options,    #value=municipio_options[0]['value'],  # Define um valor inicial do select box
    clearable=True,
    placeholder="Selecione um Município"  
)

# Criar a lista de opções para o Dropdown
regiao_options = [{'label': regiao, 'value': regiao} for regiao in df_regiao['Região Saúde'].unique()]
dropdown_regiao = dcc.Dropdown(
    id='select-dropdown',
    options=regiao_options,    #value=municipio_options[0]['value'],  # Define um valor inicial do select box
    clearable=True,
    placeholder="Selecione uma Região"
  
)

options_sexo = [{'label': sexo, 'value': sexo} for sexo in tabela_municipio['Sexo'].unique()]
dropdown_sexo = dcc.Dropdown(
    id='select-sexo-municipio',
    options=options_sexo,
    clearable=True,
    placeholder="Selecione um Sexo"
    )


limpar_filtro = dbc.Button("Limpar Filtro", id='limpar-filtro-btn', n_clicks=0, size="sm", color="success")

# ========================================================================== PLOTAGEM DOS DADOS  ========================================================================== #




# GRAFICO DEMOGRAFICO MUNICÍPIOS
figure1 = px.choropleth_mapbox(
    gdf_geojson,  # Use the GeoDataFrame
    geojson=geojson_for_plot,  # Use the GeoJSON for plotting
    locations='Município',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.Município",  # Corresponding key in the GeoJSON
    color='Porcentagem (%)',  # Column in gdf_geojson to define the color
    hover_data=['Município', 'População ', 'Porcentagem (%)', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.4180342, "lon": -51.7706038},
    opacity=1,
    color_continuous_scale="Teal"
)
figure1.update_layout(
    width=900,
    height=400,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="Porcentagem (%)",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DE DOSES BIVALENTE APLICADAS POR MUNICÍPIO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)







# GRAFICO DEMOGRAFICO REGIAO
figure2 = px.choropleth_mapbox(
    gdf_geojson2, # Use the GeoDataFrame
    geojson=geojson_for_plot2,  # Use the GeoJSON for plotting
    locations='Região Saúde',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.REGIAO_SAU",  # Corresponding key in the GeoJSON
    color='Porcentagem (%)',  # Column in gdf_geojson to define the color
    hover_data=['População ', 'Porcentagem (%)', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    title='(%) COBERTURA DE DOSES BIVALENTE APLICADAS POR REGIÃO',
    center={"lat": -27.4180342, "lon": -51.7706038},
    opacity=1,
    color_continuous_scale="Teal"
    )
figure2.update_layout(
    width=900,
    height=400,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="Porcentagem (%)",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DE DOSES BIVALENTE APLICADAS POR REGIÃO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)
# ========================================================================== # CARDS # ========================================================================== #

def update_card_string(value, title):
    titulo = f"<span style='font-size:14px; font-weight:bold'><b>{title}</b></span>"
    valores = f"{titulo}<br><span style='font-size:27px'>{value}</span>"

    card_layout = go.Layout(
        title="",  # Remova o título do indicador
        paper_bgcolor="#f8f9fa",  # Define a cor de fundo do interior do card como transparente
        plot_bgcolor="#f8f9fa",  # Define a cor de fundo do gráfico como transparente
        margin={'l': 1, 't': 1, 'b': 2, 'r': 1},
        height=85,
        xaxis={'visible': False},  # Remove a escala numérica do eixo x
        yaxis={'visible': False},   # Remove a escala numérica do eixo y
        annotations=[{
            'x': 0.5,  # Define a posição horizontal do texto no cartão (no meio)
            'y': 0.5,  # Define a posição vertical do texto no cartão (no meio)
            'xref': 'paper',
            'yref': 'paper',
            'text': valores,  # Adiciona o texto combinado como anotação
            'showarrow': False,  # Não mostra a seta de indicação
            'font': {'size': 19},  # Define o tamanho da fonte da anotação para os valores
            'align': 'center',  # Alinha o texto ao centro
        }]
    )

    return go.Figure(layout=card_layout)




def update_card_porcentagem(value, title):
    # Adjusting the HTML formatting within Python string
    titulo = f"<span style='font-size:14px; font-weight:bold;'>{title}</span>"
    valores = f"{titulo}<br><span style='font-size:27px;'>{value:.2f}%</span>"

    # Layout configuration
    card_layout = go.Layout(
        title="",  # Removing the title of the indicator
        paper_bgcolor="#f8f9fa",  # Set the background color of the interior of the card as transparent
        plot_bgcolor="#f8f9fa",  # Set the background color of the chart as transparent
        margin={'l': 1, 't': 1, 'b': 2, 'r': 1},  # Margin adjustment
        height=85,
        xaxis={'visible': False},  # Hide the numerical scale on the x-axis
        yaxis={'visible': False},  # Hide the numerical scale on the y-axis
        annotations=[{
            'x': 0.5,  # Horizontally center the text in the card
            'y': 0.5,  # Vertically center the text in the card
            'xref': 'paper',
            'yref': 'paper',
            'text': valores,  # Add the combined text as an annotation
            'showarrow': False,  # Do not show an arrow pointing to the text
            'font': {'size': 19},  # Set the font size for the annotation
            'align': 'center'  # Center-align the text
        }]
    )

    # Return a Plotly Figure with the specified layout
    return go.Figure(layout=card_layout)



# ========================================================================== # CALLBACKS # ========================================================================== #

# cache = Cache(config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
# })


# timeout = 20

# @cache.memoize(timeout=timeout)  # in seconds
# def render(value):
#     current_time = datetime.datetime.now().strftime('%H:%M:%S')
#     return f'Selected "{value}" at "{current_time}"'

@callback(
    [Output('select-municipio-bivalente', 'value'),
     Output('select-dropdown', 'value'),
     Output('select-sexo-municipio', 'value')],
    [Input('limpar-filtro-btn', 'n_clicks')],
    [State('select-municipio-bivalente', 'value'),
     State('select-dropdown', 'value'),
     State('select-sexo-municipio', 'value')]
)


def limpar_filtros(n_clicks, municipio_value, regiao_value, sexo_value):
    # Reseta os valores dos dropdowns quando o botão é clicado
    if n_clicks > 0:
        return [None, None, None]
    return [municipio_value, regiao_value, sexo_value]


@callback(
    [Output('bar-chart-municipio', 'figure'),
     Output('bar-chart-regiao', 'figure'),
     Output('bar-chart-municipio5', 'figure'),
     Output('bar-chart-regiao5', 'figure'),
     Output('bar-chart-regiao6', 'figure'),
     Output('bar-chart-municipio7', 'figure'),
     Output('tabela-municipio', 'data'),
     Output('tabela-regiao', 'data'),
     Output('card1-municipio', 'figure'),
     Output('card2-municipio', 'figure'),
     Output('card3-municipio', 'figure'),
     Output('card4-municipio', 'figure')],
    [Input('map-choropleth-municipio', 'clickData'),
     Input('map-choropleth-regiao', 'clickData'),
     Input('select-municipio-bivalente', 'value'),
     Input('select-dropdown', 'value'),
     Input('select-sexo-municipio', 'value'),
     Input('limpar-filtro-btn', 'n_clicks')],
    [State('select-municipio-bivalente', 'value'),
     State('select-dropdown', 'value')]
)

def update_bar_chart_and_table(clickData, clickDataregiao, municipio_dropdown, regiao_dropdown, sexo, n_clicks_limpar, municipio_state, regiao_state):
    ctx = dash.callback_context
    # Verifica qual input foi acionado
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    selected_municipio = municipio_dropdown
    selected_regiao = regiao_dropdown

    if trigger_id == 'limpar-filtro-btn' and n_clicks_limpar > 0:
        selected_municipio = None
        selected_regiao = None
        sexo = None

    elif trigger_id == 'map-choropleth-municipio' and clickData:
        selected_municipio = clickData['points'][0]['location'] if clickData else municipio_dropdown

    elif trigger_id == 'map-choropleth-regiao' and clickDataregiao:
        selected_regiao = clickDataregiao['points'][0]['location'] if clickDataregiao else regiao_dropdown

    elif trigger_id == 'select-municipio-bivalente':
        selected_municipio = municipio_dropdown

    elif trigger_id == 'select-municipio-bivalente':
        selected_municipio = municipio_dropdown

    elif trigger_id == 'select-dropdown':
        selected_regiao = regiao_dropdown

    else:
        selected_municipio = municipio_state
        selected_regiao = regiao_state




    if selected_regiao:
        ## ============================================== ##   MUNICIPIO  ## ============================================== ##
         # CARDS
        table_data = tabela_.to_dict('records')
        cada_populacao_municipio = df_municipio['População'].sum()

        #cada_populacao_municipio = df_municipio['População'].sum()
        total_doses_aplicadas = df_municipio['Número de Vacinas'].sum()
        porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100
        populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Dose'] == '1ª DOSE') & (tabela_populacao_municipio['Sexo'] == 'Feminino')]['População'].sum()

        # FILTROS
        df_filtered = tabela_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered5 = cobertura8.groupby(['Município', 'Sexo']).sum().reset_index()
        df_filtered6 = cobertura7.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        ## ============================================== ##   REGIAO  ## ============================================== ##
        #CARDS
        cada_populacao_municipio = df_regiao[df_regiao['Região Saúde'] == selected_regiao]['População'].sum()
        total_doses_aplicadas = df_regiao[df_regiao['Região Saúde'] == selected_regiao]['Número de Vacinas'].sum()
        populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Região Saúde'] == selected_regiao) & (tabela_populacao_municipio['Dose'] == '1ª DOSE') & (tabela_populacao_municipio['Sexo'] == 'Feminino')]['População'].sum()
        porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100

        #FILTROS
        df_filtered_regiao = tabela_regiao_[tabela_regiao_['Região Saúde'] == selected_regiao]
        df_agrupado_filtrado = df_regiao[df_regiao['Região Saúde'] == selected_regiao]

        df_agrupado_filtrado2 = cobertura3[cobertura3['Região Saúde'] == selected_regiao].groupby(['Região Saúde', 'Sexo']).sum().reset_index()

        # medidas para trazem os municipios das regiões filtradas
        df_agrupado_filtrado3 = cobertura8[cobertura8['Região Saúde'] == selected_regiao].groupby(['Município', 'Sexo']).sum().reset_index()

        filtro_cobertura_faixa_etaria_regiao = df_regiao[df_regiao['Região Saúde'] == selected_regiao]


        # Aplica filtro por sexo se estiver selecionado
        if sexo:
                        # ==================================================== #   MUNICIPIO     # ==================================================== #

            populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Sexo'] == sexo) & (tabela_populacao_municipio['Dose']=='1ª DOSE') & (tabela_populacao_municipio['Região Saúde']==selected_regiao)]['População Sexo'].sum()

            df_filtered2 = filtro_cobertura_faixa_etaria_regiao[filtro_cobertura_faixa_etaria_regiao['Sexo'] == sexo]
            df_filtered3 = filtro_cobertura_faixa_etaria_regiao[filtro_cobertura_faixa_etaria_regiao['Sexo'] == sexo]

            df_filtered4 = df_agrupado_filtrado2[df_agrupado_filtrado2['Sexo'] == sexo]

            df_filtered5 = df_agrupado_filtrado3[df_agrupado_filtrado3['Sexo'] == sexo]

            table_data_regiao = df_filtered_regiao[df_filtered_regiao['Sexo'] == sexo].to_dict('records')
            total_doses_aplicadas = df_agrupado_filtrado[df_agrupado_filtrado['Sexo'] == sexo]['Número de Vacinas'].sum()
            cada_populacao_municipio = df_agrupado_filtrado[df_agrupado_filtrado['Sexo'] == sexo]['População'].sum()
            porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100

                        # ==================================================== #   REGIAO     # ==================================================== #


        else:
            df_filtered2 = filtro_cobertura_faixa_etaria_regiao
            df_filtered3 = filtro_cobertura_faixa_etaria_regiao
            df_filtered4 = df_agrupado_filtrado2
            df_filtered5 = df_agrupado_filtrado3
            table_data_regiao = df_filtered_regiao.to_dict('records')
            total_doses_aplicadas = df_agrupado_filtrado['Número de Vacinas'].sum()
            porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100

    # Filtros por município
    elif selected_municipio:
        ## ============================================== ##   REGIAO  ## ============================================== ##
        table_data_regiao = tabela_regiao_.to_dict('records')
        cada_populacao_municipio = tabela_para_regiao['População'].sum()
        total_doses_aplicadas = tabela_para_regiao['Número de Vacinas'].sum()
        porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100
        populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Dose'] == '1ª DOSE') & (tabela_populacao_municipio['Sexo'] == 'Feminino')]['População'].sum()
        # FILTROS
        df_filtered2 = tabela_para_regiao.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()


        df_filtered3 = cobertura2.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        df_filtered4 = cobertura3.groupby(['Região Saúde', 'Sexo']).sum().reset_index()


        ## ============================================== ##   MUNICIPIO  ## ============================================== ##
        # #CARDS
        cada_populacao_municipio = df_municipio[df_municipio['Município'] == selected_municipio]['População'].sum()
        total_doses_aplicadas = df_municipio[df_municipio['Município'] == selected_municipio]['Número de Vacinas'].sum()
        populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Município'] == selected_municipio) & (tabela_populacao_municipio['Dose'] == '1ª DOSE') & (tabela_populacao_municipio['Sexo'] == 'Feminino')]['População'].sum()
        porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100

        #FILTROS
        df_filtered_municipio = tabela_municipio[tabela_municipio['Município'] == selected_municipio]
        df_agrupado_filtrado = tabela_[tabela_['Município'] == selected_municipio]

        df_agrupado_filtrado3 = cobertura8[cobertura8['Município'] == selected_municipio].groupby(['Município', 'Sexo']).sum().reset_index()

        filtro_cobertura_faixa_etaria_municipio = cobertura9[cobertura9['Município'] == selected_municipio].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()


        # Aplica filtro por sexo se estiver selecionado
        if sexo:
            df_filtered = df_filtered_municipio[df_filtered_municipio['Sexo'] == sexo]

            df_filtered5 = df_agrupado_filtrado3[df_agrupado_filtrado3['Sexo'] == sexo]

            df_filtered6 = filtro_cobertura_faixa_etaria_municipio[filtro_cobertura_faixa_etaria_municipio['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Sexo'] == sexo) & (tabela_populacao_municipio['Dose']=='1ª DOSE')& (tabela_populacao_municipio['Município']==selected_municipio)]['População Sexo'].sum()



            table_data = df_agrupado_filtrado[df_agrupado_filtrado['Sexo'] == sexo].to_dict('records')
            total_doses_aplicadas = df_filtered_municipio[df_filtered_municipio['Sexo'] == sexo]['Número de Vacinas'].sum()
            cada_populacao_municipio = df_filtered_municipio[df_filtered_municipio['Sexo'] == sexo]['População'].sum()
            porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100

        else:
            df_filtered = df_filtered_municipio
            df_filtered5 = df_agrupado_filtrado3
            df_filtered6 = filtro_cobertura_faixa_etaria_municipio


            table_data = df_agrupado_filtrado.to_dict('records')
            total_doses_aplicadas = df_filtered_municipio['Número de Vacinas'].sum()
            porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100


    else:
         # CARDS
        table_data_regiao = tabela_regiao_.to_dict('records')
        #cada_populacao_municipio = populacao_total_bivalente['pop'].sum()
        #total_doses_aplicadas = df_regiao['Número de Vacinas'].sum()
        #porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100
        populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Dose'] == '1ª DOSE') & (tabela_populacao_municipio['Sexo'] == 'Feminino')]['População'].sum()
        # FILTROS
        df_filtered2 = df_regiao.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered3 = cobertura2.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered4 = cobertura3.groupby(['Região Saúde', 'Sexo']).sum().reset_index()

         # CARDS
        table_data = tabela_.to_dict('records')
        cada_populacao_municipio = populacao_total_bivalente['pop'].sum()

        #cada_populacao_municipio = df_municipio['População'].sum()
        total_doses_aplicadas = df_municipio['Número de Vacinas'].sum()
        porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100

        # FILTROS
        df_filtered = tabela_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered5 = cobertura8.groupby(['Município', 'Sexo']).sum().reset_index()
        df_filtered6 = cobertura7.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        if sexo:
            df_filtered2 = df_regiao[df_regiao['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered3 = cobertura2[cobertura2['Sexo'] == sexo]
            df_filtered4 = cobertura3[cobertura3['Sexo'] == sexo].groupby(['Região Saúde', 'Sexo']).sum().reset_index()

            table_data_regiao = tabela_regiao_[tabela_regiao_['Sexo'] == sexo].to_dict('records')
            populacaototal_municipio_sc = tabela_populacao_municipio[(tabela_populacao_municipio['Sexo']==sexo) & (tabela_populacao_municipio['Dose']=='1ª DOSE')]['População Sexo'].sum()
            total_doses_aplicadas = df_regiao[df_regiao['Sexo'] == sexo]['Número de Vacinas'].sum()
            cada_populacao_municipio = df_regiao[df_regiao['Sexo']== sexo]['População'].sum()
            porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100



            df_filtered = tabela_municipio[tabela_municipio['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered5 = cobertura8[cobertura8['Sexo'] == sexo].groupby(['Município', 'Sexo']).sum().reset_index()
            df_filtered6 = cobertura7[cobertura7['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

            table_data = tabela_[tabela_['Sexo'] == sexo].to_dict('records')
            #populacaototal_municipio_sc = municipio_populacao_total['total'].sum()
            total_doses_aplicadas = df_municipio[df_municipio['Sexo'] == sexo]['Número de Vacinas'].sum()
            cada_populacao_municipio = df_municipio[df_municipio['Sexo']== sexo]['População'].sum()
            porcentagem_aplicada = (total_doses_aplicadas / cada_populacao_municipio) * 100
        else:
            # Dados globais sem filtro de sexo
            total_doses_aplicadas = df_regiao['Número de Vacinas'].sum()
            
            total_doses_aplicadas = df_municipio['Número de Vacinas'].sum()




    df_filtered['Número de Vacinas Num'] = df_filtered['Número de Vacinas']
    df_filtered.loc[:, 'Número de Vacinas '] = df_filtered['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

    bar_chart_figure = px.bar(
        df_filtered,
        x='Faixa Etária',
        y='Número de Vacinas Num',
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},
        text='Número de Vacinas ',  # Adds text labels with the values from 'Número de Vacinas'
        width=900,
        height=350,
        title=f'QUANT. DE DOSES APLICADAS POR FAIXA ETÁRIA EM {selected_municipio if selected_municipio else "TODOS OS MUNICÍPIOS"}',
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  # Correct the dictionary syntax here
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}
    )
    bar_chart_figure.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. DE DOSES APLICADAS POR FAIXA ETÁRIA EM {selected_municipio if selected_municipio else "TODOS OS MUNICÍPIOS"}</b>',
            'font': {'size': 17, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left"
        ),
        xaxis={
            'title': 'Faixa Etária',
            'automargin': True,
            'tickangle': -45,  # Rotacionar os rótulos do eixo x para melhor visualização
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo x
        },
        yaxis={
            'title': 'Número de Vacinas',
            'automargin': True,
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo y (opcional)
        },
        bargap=0.2  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure.update_traces(
        textposition='inside'
    )


    df_filtered2['Número de Vacinas Num'] = df_filtered2['Número de Vacinas']
    df_filtered2.loc[:, 'Número de Vacinas '] = df_filtered2['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


    bar_chart_figure2 = px.bar(
        df_filtered2,
        x='Faixa Etária',
        y='Número de Vacinas Num',
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},
        text='Número de Vacinas ',  # Adds text labels with the values from 'Número de Vacinas'
        width=900,
        height=350,
        title=f'QUANT. DE DOSES APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  # Corrected to use a dictionary for labels
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}
    )
    bar_chart_figure2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. DE DOSES APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
            'font': {'size': 17, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left"
        ),
        xaxis={
            'title': 'Faixa Etária',
            'automargin': True,
            'tickangle': -45,  # Rotacionar os rótulos do eixo x para melhor visualização
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo x
        },
        yaxis={
            'title': 'Número de Vacinas',
            'automargin': True,
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo y (opcional)
        },
        bargap=0.2  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure2.update_traces(
        textposition='inside'
    )


    bar_chart_figure3 = px.bar(
        df_filtered3,
        x='Faixa Etária',
        y='Porcentagem (%)',
        text='Porcentagem (%)', # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        color='Sexo',
        width=1850,
        height=350,
        title=f'COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        barmode='group',
        labels={'Faixa Etária', 'Porcentagem (%)'},  # Ajuste no label para manter a consistência
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal

    )
    bar_chart_figure3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
            'font': {'size': 17, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left"
        ),
        xaxis={
            'title': 'Faixa Etária',
            'automargin': True,
            'tickangle': -45,  # Rotacionar os rótulos do eixo x para melhor visualização
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo x
        },
        yaxis={
            'title': 'Porcentagem (%)',
            'automargin': True,
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo y (opcional)
        },
        bargap=0.2  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure3.update_traces(
        textposition='inside'
    )


    bar_chart_figure4 = px.bar(
        df_filtered4,
        x='Região Saúde',
        y='Porcentagem (%)',
        text='Porcentagem (%)', # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        color='Sexo',
        width=1850,
        height=350,
        title=f'COBERTURA DE DOSES POR REGIÃO (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        barmode='group',
        labels={'Faixa Etária', 'Porcentagem (%)'},  # Ajuste no label para manter a consistência
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal

    )
    bar_chart_figure4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>COBERTURA DE DOSES POR REGIÃO (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
            'font': {'size': 17, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left"
        ),
        xaxis={
            'title': 'Região Saúde',
            'automargin': True,
            'tickangle': -45,  # Rotacionar os rótulos do eixo x para melhor visualização
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo x
        },
        yaxis={
            'title': 'Porcentagem (%)',
            'automargin': True,
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo y (opcional)
        },
        bargap=0.2  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure4.update_traces(
        textposition='inside'
    )



    max_info = 40

    df_filtered5 = df_filtered5.head(max_info)

    bar_chart_figure5 = px.bar(
        df_filtered5,
        x='Município',
        y='Porcentagem (%)',
        text='Porcentagem (%)', # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        color='Sexo',
        width=1850,
        height=350,
        title=f'(%) COBERTURA DE DOSES POR {selected_municipio if selected_municipio else "MUNICÍPIO"}',
        barmode='group',
        labels={'Município': 'Município', 'Porcentagem (%)': 'Porcentagem (%)'},  # Correção do dicionário de labels
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal
    )

    bar_chart_figure5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>(%) COBERTURA DE DOSES POR {selected_municipio if selected_municipio else "MUNICÍPIO"}</b>',
            'font': {'size': 17, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left"
        ),
        xaxis={
            'title': 'Município',
            'automargin': True,
            'tickangle': -45,  # Rotacionar os rótulos do eixo x para melhor visualização
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo x
        },
        yaxis={
            'title': 'Porcentagem (%)',
            'automargin': True,
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo y (opcional)
        },
        bargap=0.2  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    bar_chart_figure5.update_traces(
        textposition='inside',
        texttemplate='%{text:.2s}'  # Formato dos rótulos para evitar sobreposição ou texto muito longo
    )



    bar_chart_figure6 = px.bar(
        df_filtered6,
        x='Faixa Etária',
        y='Porcentagem (%)',
        text='Porcentagem (%)', # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        color='Sexo',
        width=1850,
        height=350,
        title=f'COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {selected_municipio if selected_municipio else "TODOS OS MUNICÍPIOS"}',
        barmode='group',
        labels={'Faixa Etária', 'Porcentagem (%)'},  # Ajuste no label para manter a consistência
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal

    )
    bar_chart_figure6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {selected_municipio if selected_municipio else "TODOS OS MUNICÍPIOS"}</b>',
            'font': {'size': 17, 'family': 'Arial'}
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left"
        ),
        xaxis={
            'title': 'Faixa Etária',
            'automargin': True,
            'tickangle': -45,  # Rotacionar os rótulos do eixo x para melhor visualização
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo x
        },
        yaxis={
            'title': 'Porcentagem (%)',
            'automargin': True,
            'tickfont': {'size': 9}  # Diminuir a fonte dos rótulos do eixo y (opcional)
        },
        bargap=0.2  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure6.update_traces(
        textposition='inside'
    )


    cada_populacao_municipio = f"{cada_populacao_municipio:,.0f}".replace(',', '.')
    total_doses_aplicadas = f"{total_doses_aplicadas:,.0f}".replace(',', '.')
    populacaototal_municipio_sc = f"{populacaototal_municipio_sc:,.0f}".replace(',', '.')


    new_figure_card1 = update_card_string(cada_populacao_municipio, "POP. VACINÁVEL<br>(>= 12 ANOS)")
    new_figure_card2 = update_card_string(total_doses_aplicadas, "TOTAL DOSES <br> APLICADAS")
    new_figure_card3 = update_card_porcentagem(porcentagem_aplicada, "COBERTURA (%)")
    new_figure_card4 = update_card_string(populacaototal_municipio_sc, "POPULAÇÃO <br> TOTAL")

    return bar_chart_figure, bar_chart_figure2, bar_chart_figure3, bar_chart_figure4, bar_chart_figure5, bar_chart_figure6, table_data, table_data_regiao, new_figure_card1, new_figure_card2, new_figure_card3, new_figure_card4




# Para 'tabela_para_regiao'
# Cria uma nova coluna para os valores formatados, mantendo a original para cálculos
tabela_regiao_['População '] = tabela_regiao_['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_regiao_['Número de Vacinas '] = tabela_regiao_['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

# Para 'tabela_para_municipio'
tabela_['População '] = tabela_['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_['Número de Vacinas '] = tabela_['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


@callback(
    Output('download-excel-bivalente-regiao', 'data'),
    Input('csv-export-button-regiao2', 'n_clicks'),
    State('tabela-regiao', 'columns'),
    State('tabela-regiao', 'derived_virtual_data'),
    prevent_initial_call=True
)
def export_excel_regiao(n_clicks, columns, filtered_data):
    if n_clicks:
        df = pd.DataFrame(filtered_data)
        visible_columns = [col['id'] for col in columns]
        df_export = df[visible_columns]
        return dcc.send_data_frame(df_export.to_excel, "tabela_bivalente_regiao.xlsx", index=False)


@callback(
    Output('download-excel-bivalente-municipio', 'data'),
    Input('csv-export-button', 'n_clicks'),
    State('tabela-municipio', 'columns'),
    State('tabela-municipio', 'derived_virtual_data'),
    prevent_initial_call=True
)
def export_excel_municipio(n_clicks, columns, filtered_data):
    if n_clicks:
        df = pd.DataFrame(filtered_data)
        visible_columns = [col['id'] for col in columns]
        df_export = df[visible_columns]
        return dcc.send_data_frame(df_export.to_excel, "tabela_bivalente_municipio.xlsx", index=False)



# markdown_text = '''
# Exemplo para aplicar Markdown no painel.

# '''

# # Callback para abrir e fechar o modal
# @callback(
#     dash.dependencies.Output("modal", "is_open"),
#     [dash.dependencies.Input("open", "n_clicks"),
#      dash.dependencies.Input("close", "n_clicks")],
#     [dash.dependencies.State("modal", "is_open")],
# )
# def toggle_modal(open_clicks, close_clicks, is_open):
#     if open_clicks or close_clicks:
#         return not is_open
#     return is_open



# =========  Layout  =========== #
layout = html.Div([
    dbc.Row([
        dbc.Col(width=4),  # Espaço extra à esquerda, se necessário
        dbc.Col([
            html.Div([
                html.Img(src="/vacinometro-dev/assets/syringe-solid.svg", style={
                    'height': '50px',  # Altura do ícone
                    'marginRight': '5px'  # Espaço à direita do ícone
                }),
                html.H1('PAINEL COBERTURA VACINAL BIVALENTE', style={
                    'color': '#000000',  # Cor do texto
                    'fontSize': '23px',  # Tamanho do texto
                    'fontFamily': 'Arial, sans-serif',  # Família de fontes
                    'padding': '5px',  # Espaço interno
                    'margin': '0',  # Removido margem para alinhamento vertical
                    'textAlign': 'center'  # Centraliza o texto
                }),
            ], style={
                'display': 'flex',  # Usa flexbox para layout
                'alignItems': 'center',  # Centraliza verticalmente o ícone e o texto
                'height': '100%'  # Altura total do container
            }),
        ], width=4),
        dbc.Col(width=4),  # Espaço extra à esquerda, se necessário
    ], style={'width': '100%'}, className='mt-2'),  # Removido cálculo da altura

    dbc.Row([
        dbc.Col([  # Outer container
            dbc.Col([  # Inner container for image
                html.Img(
                    src="https://www.saude.sc.gov.br/images/stories/website/2023_marca_ses.png",
                    alt="Logotipo da Saúde SC",
                    style={'width': '70%', 'height': '70%', 'margin-top': '10px'}
                )
            ], style={'text-align': 'center'}),  # Add text-align: center
        ], sm=2, lg=2),


        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        dropdown_municipios
                    ]),
                ]),
                style={'border': 0}
            ),
            sm=9,
            lg=2
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        dropdown_sexo
                    ]),
                ]),
                style={'border': 0}
            ),
            sm=9,
            lg=2
        ),

        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        dropdown_regiao
                    ]),
                ]),
                style={'border': 0}
            ),
            sm=9,
            lg=2
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        limpar_filtro
                    ])
                ]),
                style={'border': 0}
            ),
            sm=9,
            lg=2
        ),
        # dbc.Col(
        #     dbc.Card(
        #         dbc.CardBody([
        #             dbc.Button("Informações", id="open", color='success'),
                
        #             # Modal que contém as informações em Markdown
        #             dbc.Modal(
        #                 [
        #                     dbc.ModalHeader("Informações Adicionais"),
        #                     dbc.ModalBody(dcc.Markdown(children=markdown_text)),
        #                     dbc.ModalFooter(
        #                         dbc.Button("Fechar", id="close", className="ml-auto")
        #                     ),
        #                 ],
        #                 id="modal",
        #                 size="lg"  # Define o tamanho do modal (sm, md, lg, xl)
        #                 #centered=True  # Centraliza o modal na tela
        #             ),
        #         ]),
        #         style={'border': 0}
        #     ),
        #     sm=9,
        #     lg=2
        # ),
    ], style={'margin-bottom': '0px', 'background-color': 'white'}, className='sticky-top'),


    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([

                ]),
                style={'border': 0}
            )
        ],sm=2, lg=2),

        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id='card1-municipio', config={"displayModeBar": False}),
                ]),
                style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card2-municipio', config={"displayModeBar": False}),
                ),
                style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card3-municipio', config={"displayModeBar": False}),
                ),
                style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card4-municipio', config={"displayModeBar": False}),
                ),
                style={'backgroundColor': '#f8f9fa'}  # Defina a cor de fundo do card inteiro
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
    ], style={'margin-bottom': '0px'}),  # Remover a altura fixa

    dbc.Row([
        dbc.Col([
            dbc.Card([
                #html.H5('(%) COBERTURA DE DOSES BIVALENTE APLICADAS POR REGIÕES'),
                dcc.Graph(id='map-choropleth-regiao', className='dbc', config=config_graph, figure=figure2)  # VARIAVEL DO GRÁFICO MAPA DEMOGRÁFICO
            ], style={'border': 0})
        ], sm=12, md=6, lg=6),
        dbc.Col([
            dbc.Card([
                #html.H5('(%) COBERTURA DE DOSES BIVALENTE APLICADAS POR MUNICIPIO'),
                dcc.Graph(id='map-choropleth-municipio', className='dbc', config=config_graph, figure=figure1)  # VARIAVEL DO GRÁFICO MAPA DEMOGRÁFICO
            ], style={'border': 0})
        ], sm=6, md=6, lg=6)
    ], style={'width': '100%', 'margin-bottom': '0px'}),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='bar-chart-regiao', className='dbc', config=config_graph)
                ], style={'padding': '10px'})  # Adjust padding as needed
            ],style={'border': 0})
        ], sm=6, md=6, lg=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='bar-chart-municipio', className='dbc', config=config_graph)
                ], style={'padding': '10px'})  # Adjust padding as needed
            ],style={'border': 0})
        ], sm=6, md=6, lg=6)
    ], style={'width': '100%', 'margin-bottom': '0px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                     dbc.CardBody([
                            #html.H5('COBERTURA DE DOSES POR FAIXA ETÁRIA (%)'),
                                dcc.Graph(id='bar-chart-municipio5', className='dbc', config=config_graph, responsive=True) # VARIAVEL DO GRAFICO BARRAS
                        ], style={'border':0, 'overflow-x':'auto', 'weidth':'90%'})
            ],style={'border':0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'margin-bottom': '0px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                     dbc.CardBody([
                            #html.H5('COBERTURA DE DOSES POR FAIXA ETÁRIA (%)'),
                                dcc.Graph(id='bar-chart-regiao5', className='dbc', config=config_graph, responsive=True) # VARIAVEL DO GRAFICO BARRAS
            ], style={'border':0, 'overflow-x':'auto', 'weidth':450})
            ],style={'border':0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'margin-bottom': '0px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                     dbc.CardBody([
                            #html.H5('COBERTURA DE DOSES POR FAIXA ETÁRIA (%)'),
                                dcc.Graph(id='bar-chart-municipio7', className='dbc', config=config_graph, responsive=True) # VARIAVEL DO GRAFICO BARRAS
            ], style={'border':0, 'overflow-x':'auto', 'weidth':500})
            ],style={'border':0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'margin-bottom': '0px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                     dbc.CardBody([
                            #html.H5('COBERTURA DE DOSES POR FAIXA ETÁRIA (%)'),
                                dcc.Graph(id='bar-chart-regiao6', className='dbc', config=config_graph, responsive=True) # VARIAVEL DO GRAFICO BARRAS
            ], style={'border':0, 'overflow-x':'auto', 'weidth':500})
            ],style={'border':0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'margin-bottom': '0px'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('TABELA DE COBERTURA VACINAL POR REGIÃO, SEXO E DOSE'),
                    html.Button("Exportar Excel", id="csv-export-button-regiao2", className="mb-2"),
                    html.Div(
                        dash_table.DataTable(
                            id='tabela-regiao',
                            sort_action='native',
                            sort_mode='multi',
                            columns=[
                                {"name": "Região Saúde", "id": "Região Saúde"},
                                {"name": "Sexo", "id": "Sexo"},
                                {"name": "População ", "id": "População "},
                                {"name": "Número de Vacinas ", "id": "Número de Vacinas "},
                                {"name": "Porcentagem (%)", "id": "Porcentagem (%)"}
                            ],
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                'whiteSpace': 'normal'
                            },
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            page_size=10
                        ),
                        style={'overflowY': 'scroll', 'maxHeight': '600px'}
                    )
                ], style={'border': 0}),
            ], style={'border': 0}),
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'height': '100%'}),
    dcc.Download(id='download-excel-bivalente-regiao'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('TABELA DE COBERTURA VACINAL POR MUNICIPIO, SEXO E DOSE'),
                    html.Button("Exportar Excel", id="csv-export-button", className="mb-2"),
                    html.Div(
                        dash_table.DataTable(
                            id='tabela-municipio',
                            sort_action='native',
                            sort_mode='multi',
                            columns=[
                                {"name": "Município", "id": "Município"},
                                {"name": "Sexo", "id": "Sexo"},
                                {"name": "População ", "id": "População "},
                                {"name": "Número de Vacinas ", "id": "Número de Vacinas "},
                                {"name": "Porcentagem (%)", "id": "Porcentagem (%)"},
                            ],
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                'whiteSpace': 'normal'
                            },
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            page_size=10
                        ),
                        style={'overflowY': 'scroll', 'maxHeight': '600px'}
                    )
                ], style={'border': 0}),
            ], style={'border': 0}),
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'height': '100%'}),
    dcc.Download(id='download-excel-bivalente-municipio')



], style={'width': '100%', 'height': '100%'})


