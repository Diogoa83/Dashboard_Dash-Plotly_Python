import dash
from dash import html, dcc, Input, Output, State, callback, Dash, register_page, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import json
import psycopg2
from psycopg2 import pool

# importando tabelas do indexprincipal.py
from perfomace import tabela_faixa_etaria, tabela_completa, tabela_cobertura_faixa_etaria, tabela_monovalente_completa_cobertura, tabela_monovalente_cobertura_municipios, monovalente_cobertura_faixa_etaria_municipios



register_page(__name__, path='/monovalente')

########################### CONEXAO TABELA IMUNIZAÇÃO ###########################

tabela_faixa_etaria = tabela_faixa_etaria.copy()
tabela_completa = tabela_completa.copy()
tabela_cobertura_faixa_etaria = tabela_cobertura_faixa_etaria.copy()
tabela_monovalente_completa_cobertura = tabela_monovalente_completa_cobertura.copy()
tabela_monovalente_cobertura_municipios = tabela_monovalente_cobertura_municipios.copy()
monovalente_cobertura_faixa_etaria_municipios = monovalente_cobertura_faixa_etaria_municipios.copy()




######################################                ######################################



calcular = tabela_faixa_etaria.rename(columns={
    'regiao_saude': 'Região Saúde',
    'faixa_etaria_2':'Faixa Etária',
    'paciente_enum_sexo_biologico': 'Sexo',
    'contagem_dose' : 'Número de Vacinas',
    'total':'População',
    'dose':'Doses'
})


monovalente_cobertura_faixa_etaria_municipios = monovalente_cobertura_faixa_etaria_municipios.rename(columns={
    'regiao_saude':'Região Saúde',
    'municipio_paciente': 'Município',
    'sexo': 'Sexo',
    'faixa_etaria':'Faixa Etária',
    'dose':'Doses',
    'contagem_dose' : 'Número de Vacinas',
    'pop':'População',
    'porcentagem':'Porcentagem'
})




unir_dose1 = tabela_completa.rename(columns={
    'regiao_saude': 'Região Saúde',
    'total':'População',
    'paciente_enum_sexo_biologico':'Sexo',
    'contagem_dose' : 'Número de Vacinas',
    'porcentagem': '(%) Porcentagem',
    'dose':'Doses'
})

unir_dose3 = tabela_monovalente_completa_cobertura.rename(columns={
    'regiao_saude': 'Região Saúde',
    'pop':'População',
    'sexo':'Sexo',
    'dose': 'Doses',
    'contagem_dose' : 'Número de Vacinas',
    'porcentagem': 'Porcentagem (%)',
    'total':'População Região'
})

tabela_regiao = unir_dose3[(unir_dose3['Doses'] == '1ª DOSE')|(unir_dose3['Doses'] == '1ª REFORÇO')|(unir_dose3['Doses'] == '2ª DOSE') | (unir_dose3['Doses'] == '2ª REFORÇO') | (unir_dose3['Doses'] == '3ª DOSE')]

tabela_regiao = tabela_regiao.rename(columns={
    'População':'População Sexo'
})


agrupamento = monovalente_cobertura_faixa_etaria_municipios.groupby(['Município', 'Doses', 'Sexo']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()

qtd_primeira_dose_filtrada = monovalente_cobertura_faixa_etaria_municipios[monovalente_cobertura_faixa_etaria_municipios['Doses'] == '1ª DOSE']
qtd_segunda_dose_filtrada = monovalente_cobertura_faixa_etaria_municipios[monovalente_cobertura_faixa_etaria_municipios['Doses'] == '2ª DOSE']
qtd_terceira_dose_filtrada = monovalente_cobertura_faixa_etaria_municipios[monovalente_cobertura_faixa_etaria_municipios['Doses'] == '3ª DOSE']   

monovalente_tabela_doses_regioes_sexo_agrupado = tabela_completa.groupby(['regiao_saude', 'dose',  'total'])['contagem_dose'].sum().reset_index()
monovalente_tabela_doses_regioes_sexo_agrupado['Porcentagem (%)'] = round(monovalente_tabela_doses_regioes_sexo_agrupado['contagem_dose'] / monovalente_tabela_doses_regioes_sexo_agrupado['total']*100,2)

monovalente_tabela_doses_regioes_sexo_agrupado = monovalente_tabela_doses_regioes_sexo_agrupado.rename(columns={
    'regiao_saude': 'Região Saúde',
    'total':'População',
    'contagem_dose' : 'Número de Vacinas',
    'dose':'Doses'
})


primeira_dose = unir_dose1[unir_dose1['Doses']=='1ª DOSE']
segunda_dose = unir_dose1[unir_dose1['Doses']=='2ª DOSE']
terceira_dose = unir_dose1[unir_dose1['Doses']=='3ª DOSE']

map_tooltipprimeira_dose = primeira_dose.groupby(['Região Saúde', 'Doses', 'População'], as_index=False).agg({'Número de Vacinas': 'sum'})
map_tooltipprimeira_dose['(%) Porcentagem'] = round(map_tooltipprimeira_dose['Número de Vacinas'] / map_tooltipprimeira_dose['População']*100,2)

map_tooltipsegunda_dose = segunda_dose.groupby(['Região Saúde', 'Doses', 'População'], as_index=False).agg({'Número de Vacinas': 'sum'})
map_tooltipsegunda_dose['(%) Porcentagem'] = round(map_tooltipsegunda_dose['Número de Vacinas'] / map_tooltipsegunda_dose['População']*100,2)

map_tooltipterceira_dose = terceira_dose.groupby(['Região Saúde', 'Doses', 'População'], as_index=False).agg({'Número de Vacinas': 'sum'})
map_tooltipterceira_dose['(%) Porcentagem'] = round(map_tooltipterceira_dose['Número de Vacinas'] / map_tooltipterceira_dose['População']*100,2)

# def formatar_para_exibicao(x):
#     return "{:,.0f}".format(x).replace(',', '.')

map_tooltipprimeira_dose['População '] = map_tooltipprimeira_dose['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
map_tooltipprimeira_dose['Número de Vacinas '] = map_tooltipprimeira_dose['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

map_tooltipsegunda_dose['População '] = map_tooltipsegunda_dose['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
map_tooltipsegunda_dose['Número de Vacinas '] = map_tooltipsegunda_dose['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


map_tooltipterceira_dose['População '] = map_tooltipterceira_dose['População'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
map_tooltipterceira_dose['Número de Vacinas '] = map_tooltipterceira_dose['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


###############################################################################          ###############################################################################


# MEDIDAS PARA GRAFICOS COROPLETICOS DE MUNICÍPIOS
tabela_monovalente_cobertura_municipios = tabela_monovalente_cobertura_municipios[['regiao_saude','municipio_paciente', 'total', 'dose', 'cod_mun','sexo', 'contagem_dose', 'pop']]
tabela_monovalente_cobertura_municipios.groupby(['regiao_saude','municipio_paciente', 'total', 'dose', 'cod_mun', 'sexo', 'pop']).agg({'contagem_dose':'sum'}).reset_index()
tabela_monovalente_cobertura_municipios['porcentagem'] = round(tabela_monovalente_cobertura_municipios['contagem_dose'] / tabela_monovalente_cobertura_municipios['pop']*100,2)




# CRIANDO UMA VARIAVEL EXCLUSIVA PARA OS MAPAS COROPLETICOS
tabelas_coropletico = tabela_monovalente_cobertura_municipios.copy()



tabelas_coropletico = tabelas_coropletico.rename(columns={
    'regiao_saude':'Região Saúde',
    'municipio_paciente': 'Município',
    'total':'População Município',
    'sexo':'Sexo',
    'cod_mun':'Cod_IBGE',
    'dose': 'Doses',
    'contagem_dose' : 'Número de Vacinas',
    'porcentagem': '(%) Porcentagem',
    'pop':'População Sexo'
})




###############################################################################   TABELA MUNICÍPIOS       ###############################################################################

tabela_monovalente_cobertura_municipios_plot = tabela_monovalente_cobertura_municipios.copy()
tabela_monovalente_cobertura_municipios_plot = tabela_monovalente_cobertura_municipios_plot.rename(columns={
    'municipio_paciente': 'Município',
    'total':'População Município',
    'sexo':'Sexo',
    'cod_mun':'Cod_IBGE',
    'dose': 'Doses',
    'contagem_dose' : 'Número de Vacinas',
    'porcentagem': 'Porcentagem (%)',
    'pop':'População Sexo'
})


tabela_monovalente_cobertura_municipios_plot = tabela_monovalente_cobertura_municipios_plot[(tabela_monovalente_cobertura_municipios_plot['Doses'] == '1ª DOSE')|(tabela_monovalente_cobertura_municipios_plot['Doses'] == '1ª REFORÇO')|(tabela_monovalente_cobertura_municipios_plot['Doses'] == '2ª DOSE') | (tabela_monovalente_cobertura_municipios_plot['Doses'] == '2ª REFORÇO') | (tabela_monovalente_cobertura_municipios_plot['Doses'] == '3ª DOSE')]
# ORDENAR AS COLUNAS PARA FICAR IGUAL A TABELA DE REGIAO
tabela_monovalente_cobertura_municipios_plot = tabela_monovalente_cobertura_municipios_plot[['Município', 'Doses', 'Sexo', 'População Sexo', 'Número de Vacinas', 'Porcentagem (%)', 'População Município']]
###############################################################################  TABELAS CRIADAS POR NUMERO DE DOSES PARA CRIAR CARDS DAS QUANT. DOSES APLICADAS        ###############################################################################

#MEDIDAS PARA GRAFICOS DE BARRAS DE MUNICIPICIOS (FAIXA ETÁRIA POR NUMERO DE DOSES)
primeira_dose_porfaixaetaria_municipio = monovalente_cobertura_faixa_etaria_municipios[monovalente_cobertura_faixa_etaria_municipios['Doses']=='1ª DOSE']
segunda_dose_porfaixaetaria_municipio = monovalente_cobertura_faixa_etaria_municipios[monovalente_cobertura_faixa_etaria_municipios['Doses']=='2ª DOSE']
terceira_dose_porfaixaetaria_municipio = monovalente_cobertura_faixa_etaria_municipios[monovalente_cobertura_faixa_etaria_municipios['Doses']=='3ª DOSE']


# usando a tabela plotada no painel de municipios e agrupando e somando as contagens de doses por sexos para adicionar o valor absoluto nos mapas coropleticos
cobertura_doses_municipio_tooltips = tabelas_coropletico.groupby(['Município', 'Doses']).agg({'Número de Vacinas':'sum', 'População Sexo':'sum'}).reset_index()
cobertura_doses_municipio_tooltips['(%) Porcentagem'] = round(cobertura_doses_municipio_tooltips['Número de Vacinas'] / cobertura_doses_municipio_tooltips['População Sexo']*100,2)  

cobertura_doses_municipio_tooltips = cobertura_doses_municipio_tooltips.rename(columns={
    'População Sexo': 'População Município',
})

primeira_dose_municipios = cobertura_doses_municipio_tooltips[cobertura_doses_municipio_tooltips['Doses']=='1ª DOSE'].copy()
segunda_dose_municipios = cobertura_doses_municipio_tooltips[cobertura_doses_municipio_tooltips['Doses']=='2ª DOSE'].copy()
terceira_dose_municipios = cobertura_doses_municipio_tooltips[cobertura_doses_municipio_tooltips['Doses']=='3ª DOSE'].copy()


# Para 'primeira_dose_municipios'
primeira_dose_municipios.loc[:,'População Município '] = primeira_dose_municipios['População Município'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
primeira_dose_municipios.loc[:,'Número de Vacinas '] = primeira_dose_municipios['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

# Para 'segunda_dose_municipios'
segunda_dose_municipios.loc[:,'População Município '] = segunda_dose_municipios['População Município'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
segunda_dose_municipios.loc[:,'Número de Vacinas '] = segunda_dose_municipios['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

# Para 'terceira_dose_municipios'
terceira_dose_municipios.loc[:,'População Município '] = terceira_dose_municipios['População Município'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
terceira_dose_municipios.loc[:,'Número de Vacinas '] = terceira_dose_municipios['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

# Criar uma cópia do DataFrame após filtrar para garantir que estamos modificando uma cópia independente


# Agora modificando o DataFrame copiado de forma segura


# MEDIDAS PARA GRAFICOS DE BARRAS DE REGIOES (FAIXA ETÁRIA POR NUMERO DE DOSES)
primeira_dose_porfaixaetaria = calcular[calcular['Doses']=='1ª DOSE']
segunda_dose_porfaixaetaria = calcular[calcular['Doses']=='2ª DOSE']
terceira_dose_porfaixaetaria = calcular[calcular['Doses']=='3ª DOSE']

###############################################################################   COBERTURA VACINA POR FAIXA ETÁRIA (MUNICÍPIOS)       ###############################################################################



# TABELA CRIADA PARA O GRAFICO DE COBERTURA VACINA POR FAIXA ETÁRIA (MUNICÍPIOS)
tabela_cobertura_faixa_etaria_municipio = monovalente_cobertura_faixa_etaria_municipios.groupby(['Município','Faixa Etária', 'Doses']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
tabela_cobertura_faixa_etaria_municipio['Porcentagem (%)'] = round(tabela_cobertura_faixa_etaria_municipio['Número de Vacinas'] / tabela_cobertura_faixa_etaria_municipio['População']*100,2)  

cobertura_doses_municipio = tabelas_coropletico
cobertura_doses_municipio =  cobertura_doses_municipio[(cobertura_doses_municipio['Doses'] == '1ª DOSE')|(cobertura_doses_municipio['Doses'] == '1ª REFORÇO')|(cobertura_doses_municipio['Doses'] == '2ª DOSE') | (cobertura_doses_municipio['Doses'] == '2ª REFORÇO') | (cobertura_doses_municipio['Doses'] == '3ª DOSE')]
cobertura_doses_municipio = cobertura_doses_municipio.groupby(['Região Saúde','Município', 'Doses']).agg({'Número de Vacinas':'sum', 'População Sexo':'sum'}).reset_index()
cobertura_doses_municipio['Porcentagem (%)'] = round(cobertura_doses_municipio['Número de Vacinas'] / cobertura_doses_municipio['População Sexo']*100,2)  


###############################################################################          ###############################################################################

tabela_cobertura_faixa_etaria = tabela_cobertura_faixa_etaria.rename(columns={
    'regiao_saude': 'Região Saúde',
    'faixa_etaria_2':'Faixa Etária',
    'contagem_dose' : 'Número de Vacinas',
    'pop':'População',
    'dose':'Dose'
})


###############################################################################   FILTROS       ###############################################################################
# filtro_regiao_saude







###############################################################################          ###############################################################################

                                            ################################# GRAFICOS ###########################
# Configuração para ocultar elementos graficos como: desligar zoom, desligar Menus etc...
config_graph={"displayModeBar": False, "showTips": False, 'scrollZoom': False, "showTips": True}

# ============================================================================ # MAPAS REGIOES # =========================================================================== #
#MAPA TERCEIRA DOSE
#Carregar os dados do GeoJSON
# TRANSFORMAÇÃO DO JSON PARA GEOJSON E ADICIONAR INFORMAÇÕES DE TOOLTIPS PARA VISUALIZAR NO MAPA
geojson_path = r"REGIAO_SAUDE_SC_17.geojson"
with open(geojson_path, 'r', encoding='utf-8') as geojson_file:
    geojson_data = json.load(geojson_file)

geojson_df = pd.DataFrame(geojson_data['features'])

geojson_df['GEOCODIGO'] = geojson_df['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df['REGIAO_SAU'] = geojson_df['properties'].apply(lambda x: x.get('REGIAO_SAU'))
geojson_df['coordinates'] = geojson_df['geometry'].apply(lambda x: x.get('coordinates'))


geojson_df['GEOCODIGO'] = geojson_df['GEOCODIGO'].astype(str)


geojson_df = geojson_df.rename(columns={'REGIAO_SAU':'regiao_saude'})

merged_data = pd.merge(left=map_tooltipterceira_dose, right=geojson_df, left_on='Região Saúde', right_on='regiao_saude', how='left')
merged_data.head(5)

gdf_geojson = gpd.GeoDataFrame.from_features(geojson_data['features'])
gdf_geojson.crs = 'EPSG:4326'
gdf_geojson['GEOCODIGO'] = gdf_geojson['GEOCODIGO'].astype(str)
merged_data['GEOCODIGO'] = merged_data['GEOCODIGO'].astype(str)
gdf_geojson = gdf_geojson.merge(merged_data, left_on='GEOCODIGO', right_on='GEOCODIGO', how='left')
gdf_geojson.head(5)
gdf_geojson = gpd.GeoDataFrame(gdf_geojson, geometry='geometry_x', crs='EPSG:4326')
#gdf_geojson['Contagem maior 30'] = gdf_geojson['Contagem maior 30'].astype(float)
geojson_for_plot = json.loads(gdf_geojson.to_json())


# MAPA SEGUNDA DOSE
geojson_path1 = r"REGIAO_SAUDE_SC_17.geojson"
with open(geojson_path1, 'r', encoding='utf-8') as geojson_file1:
    geojson_data1 = json.load(geojson_file1)

geojson_df1 = pd.DataFrame(geojson_data1['features'])
geojson_df1['GEOCODIGO'] = geojson_df1['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df1['REGIAO_SAU'] = geojson_df1['properties'].apply(lambda x: x.get('REGIAO_SAU'))
geojson_df1['coordinates'] = geojson_df1['geometry'].apply(lambda x: x.get('coordinates'))
geojson_df1['GEOCODIGO'] = geojson_df1['GEOCODIGO'].astype(str)
geojson_df1 = geojson_df1.rename(columns={'REGIAO_SAU':'regiao_saude'})

merged_data1 = pd.merge(left=map_tooltipsegunda_dose, right=geojson_df1, left_on='Região Saúde', right_on='regiao_saude', how='left')
geojson_df1.head(5)

gdf_geojson1 = gpd.GeoDataFrame.from_features(geojson_data1['features'])
gdf_geojson1.crs = 'EPSG:4326'
gdf_geojson1['GEOCODIGO'] = gdf_geojson1['GEOCODIGO'].astype(str)
merged_data1['GEOCODIGO'] = merged_data1['GEOCODIGO'].astype(str)
gdf_geojson1 = gdf_geojson1.merge(merged_data1, left_on='GEOCODIGO', right_on='GEOCODIGO', how='left')
gdf_geojson1.head(5)
gdf_geojson1 = gpd.GeoDataFrame(gdf_geojson1, geometry='geometry_x', crs='EPSG:4326')
#gdf_geojson1['Contagem maior 30'] = gdf_geojson1['Contagem maior 30'].astype(float)
geojson_for_plot1 = json.loads(gdf_geojson1.to_json())


# MAPA PRIMEIRA DOSE
geojson_path2 = r"REGIAO_SAUDE_SC_17.geojson"
with open(geojson_path2, 'r', encoding='utf-8') as geojson_file2:
    geojson_data2 = json.load(geojson_file2)

geojson_df2 = pd.DataFrame(geojson_data2['features'])

geojson_df2['GEOCODIGO'] = geojson_df2['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df2['REGIAO_SAU'] = geojson_df2['properties'].apply(lambda x: x.get('REGIAO_SAU'))
geojson_df2['coordinates'] = geojson_df2['geometry'].apply(lambda x: x.get('coordinates'))
geojson_df2['GEOCODIGO'] = geojson_df2['GEOCODIGO'].astype(str)
geojson_df2 = geojson_df2.rename(columns={'REGIAO_SAU':'regiao_saude'})

merged_data2 = pd.merge(left=map_tooltipprimeira_dose, right=geojson_df2, left_on='Região Saúde', right_on='regiao_saude', how='left')
geojson_df2.head(5)

gdf_geojson2 = gpd.GeoDataFrame.from_features(geojson_data2['features'])
gdf_geojson2.crs = 'EPSG:4326'
gdf_geojson2['GEOCODIGO'] = gdf_geojson2['GEOCODIGO'].astype(str)
merged_data2['GEOCODIGO'] = merged_data2['GEOCODIGO'].astype(str)
gdf_geojson2 = gdf_geojson2.merge(merged_data2, left_on='GEOCODIGO', right_on='GEOCODIGO', how='left')
gdf_geojson2.head(5)
gdf_geojson2 = gpd.GeoDataFrame(gdf_geojson2, geometry='geometry_x', crs='EPSG:4326')
geojson_for_plot2 = json.loads(gdf_geojson2.to_json())

# ============================================================================ # MAPAS MUNICÍPIOS # =========================================================================== #

# PRIMEIRA DOSE MUNICÍPIOS
geojson_path3 = r"SC2.json"
with open(geojson_path3, 'r', encoding='utf-8') as geojson_file3:
    geojson_data3 = json.load(geojson_file3)
geojson_df3 = pd.DataFrame(geojson_data3['features'])
geojson_df3['GEOCODIGO'] = geojson_df3['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df3['Município'] = geojson_df3['properties'].apply(lambda x: x.get('Município'))
geojson_df3['Município'] = geojson_df3['Município'].str.upper()
merged_data3 = pd.merge(primeira_dose_municipios, geojson_df3, left_on='Município', right_on='Município', how='left')
gdf_geojson3 = gpd.GeoDataFrame.from_features(geojson_data3['features'])
gdf_geojson3.crs = 'EPSG:4326'
gdf_geojson3['Município'] = gdf_geojson3['Município'].str.upper()
gdf_geojson3 = gdf_geojson3.merge(merged_data3, left_on='Município', right_on='Município', how='left')
gdf_geojson3 = gpd.GeoDataFrame(gdf_geojson3, geometry='geometry_x', crs='EPSG:4326')
geojson_for_plot3 = json.loads(gdf_geojson3.to_json())



# SEGUNDA DOSE MUNICÍPIOS
geojson_path4 = r"SC2.json"
with open(geojson_path4, 'r', encoding='utf-8') as geojson_file4:
    geojson_data4 = json.load(geojson_file4)
geojson_df4 = pd.DataFrame(geojson_data4['features'])
geojson_df4['GEOCODIGO'] = geojson_df4['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df4['Município'] = geojson_df4['properties'].apply(lambda x: x.get('Município'))
geojson_df4['Município'] = geojson_df4['Município'].str.upper()
merged_data4 = pd.merge(segunda_dose_municipios, geojson_df4, left_on='Município', right_on='Município', how='left')
gdf_geojson4 = gpd.GeoDataFrame.from_features(geojson_data4['features'])
gdf_geojson4.crs = 'EPSG:4326'
gdf_geojson4['Município'] = gdf_geojson4['Município'].str.upper()
gdf_geojson4 = gdf_geojson4.merge(merged_data4, left_on='Município', right_on='Município', how='left')
gdf_geojson4 = gpd.GeoDataFrame(gdf_geojson4, geometry='geometry_x', crs='EPSG:4326')
geojson_for_plot4 = json.loads(gdf_geojson4.to_json())



# TERCEIRA DOSE MUNICÍPIOS
geojson_path5 = r"SC2.json"
with open(geojson_path5, 'r', encoding='utf-8') as geojson_file5:
    geojson_data5 = json.load(geojson_file5)
geojson_df5 = pd.DataFrame(geojson_data5['features'])
geojson_df5['GEOCODIGO'] = geojson_df5['properties'].apply(lambda x: x.get('GEOCODIGO'))
geojson_df5['Município'] = geojson_df5['properties'].apply(lambda x: x.get('Município'))
geojson_df5['Município'] = geojson_df5['Município'].str.upper()
merged_data5 = pd.merge(terceira_dose_municipios, geojson_df5, left_on='Município', right_on='Município', how='left')
gdf_geojson5 = gpd.GeoDataFrame.from_features(geojson_data5['features'])
gdf_geojson5.crs = 'EPSG:4326'
gdf_geojson5['Município'] = gdf_geojson5['Município'].str.upper()
gdf_geojson5 = gdf_geojson5.merge(merged_data5, left_on='Município', right_on='Município', how='left')
gdf_geojson5 = gpd.GeoDataFrame(gdf_geojson5, geometry='geometry_x', crs='EPSG:4326')
geojson_for_plot5 = json.loads(gdf_geojson5.to_json())



# ========================================================================== PLOTAGEM DOS DADOS  ========================================================================== #







# ========================================================================== MAPAS REGIÕES ========================================================================== #

# CRIAÇÃO DE MAPAS COROPLETICOS
# PRIMEIRA DOSE
figure1 = px.choropleth_mapbox(
    gdf_geojson2, # Use the GeoDataFrame
    geojson=geojson_for_plot2,  # Use the GeoJSON for plotting
    locations='Região Saúde',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.REGIAO_SAU",  # Corresponding key in the GeoJSON
    color='(%) Porcentagem',  # Column in gdf_geojson to define the color
    hover_data=['População ', '(%) Porcentagem', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.5954, "lon": -51.024735},
    opacity=1,
    color_continuous_scale="Teal"
    )
figure1.update_layout(
        width=900,
        height=300,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="(%) Porcentagem",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DA 1ª DOSE APLICADA POR REGIÃO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)

#SEGUNDA DOSE
figure2 = px.choropleth_mapbox(
    gdf_geojson1, # Use the GeoDataFrame
    geojson=geojson_for_plot1,  # Use the GeoJSON for plotting
    locations='Região Saúde',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.REGIAO_SAU",  # Corresponding key in the GeoJSON
    color='(%) Porcentagem',  # Column in gdf_geojson to define the color
    hover_data=['População ', '(%) Porcentagem', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.5954, "lon": -51.024735},
    opacity=1,
    color_continuous_scale="Blues"
)
figure2.update_layout(
        width=900,
        height=300,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="(%) Porcentagem",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DA 2ª DOSE APLICADA POR REGIÃO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)

# TERCEIRA DOSE
figure3 = px.choropleth_mapbox(
    gdf_geojson, # Use the GeoDataFrame
    geojson=geojson_for_plot,  # Use the GeoJSON for plotting
    locations='Região Saúde',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.REGIAO_SAU",  # Corresponding key in the GeoJSON
    color='(%) Porcentagem',  # Column in gdf_geojson to define the color
    hover_data=['População ', '(%) Porcentagem', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.5954, "lon": -51.024735},
    opacity=1,
    color_continuous_scale="Brwnyl"
)
figure3.update_layout(
        width=900,
        height=300,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="(%) Porcentagem",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DA 3ª DOSE APLICADA POR REGIÃO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)

# ================================================================================== # MAPAS MUNICÍPIOS # ================================================================================== #

# PRIMEIRA DOSE MUNICIPIO
figure4 = px.choropleth_mapbox(
    gdf_geojson3, # Use the GeoDataFrame
    geojson=geojson_for_plot3,  # Use the GeoJSON for plotting
    locations='Município',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.Município",  # Corresponding key in the GeoJSON
    color='(%) Porcentagem',  # Column in gdf_geojson to define the color
    hover_data=['Município', 'População Município ', '(%) Porcentagem', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.5954, "lon": -51.024735},
    opacity=1,
    color_continuous_scale="Teal",
    color_continuous_midpoint=True
    )
figure4.update_layout(
        width=900,
        height=300,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="(%) Porcentagem",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DA 1ª DOSE APLICADA POR MUNICÍPIO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)

# SEGUNDA DOSE MUNICIPIO
figure5 = px.choropleth_mapbox(
    gdf_geojson4, # Use the GeoDataFrame
    geojson=geojson_for_plot4,  # Use the GeoJSON for plotting
    locations='Município',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.Município",  # Corresponding key in the GeoJSON
    color='(%) Porcentagem',  # Column in gdf_geojson to define the color
    hover_data=['Município', 'População Município ', '(%) Porcentagem', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.5954, "lon": -51.024735},
    opacity=1,
    color_continuous_scale="Blues",
    color_continuous_midpoint=True
    )
figure5.update_layout(
        width=900,
        height=300,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="(%) Porcentagem",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DA 2ª DOSE APLICADA POR MUNICÍPIO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)

# TERCEIRA DOSE MUNICIPIO
figure6 = px.choropleth_mapbox(
    gdf_geojson5, # Use the GeoDataFrame
    geojson=geojson_for_plot5,  # Use the GeoJSON for plotting
    locations='Município',  # Column in gdf_geojson with the location identifiers
    featureidkey="properties.Município",  # Corresponding key in the GeoJSON
    color='(%) Porcentagem',  # Column in gdf_geojson to define the color
    hover_data=['Município', 'População Município ', '(%) Porcentagem', 'Número de Vacinas '],
    mapbox_style="white-bg",
    zoom=5.9,
    center={"lat": -27.5954, "lon": -51.024735},
    opacity=1,
    color_continuous_scale="Brwnyl", 
    color_continuous_midpoint=True
    )
figure6.update_layout(
        width=900,
        height=300,
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="(%) Porcentagem",
        yanchor="bottom",
        len=0.5,
        y=0.05,
        xanchor="left",
        x=0.05
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_text='(%) COBERTURA DA 3ª DOSE APLICADA POR MUNICÍPIO',  # Text of the title
    title_x=0.5,  # Center the title horizontally
    title_font=dict(  # Configuration for the title font
        family="Arial",  # Specifies the font family, using 'Arial Black' for bold
        size=20,  # Specifies the font size
        color='black'  # Specifies the font color
    )
)





# # # =============================================================== # SELECT BOX (FILTROS) # =============================================================== #

# Criar a lista de opções para o Dropdown
regiao_options = [{'label': regiao, 'value': regiao} for regiao in unir_dose3['Região Saúde'].unique()]
dropdown_regiao = dcc.Dropdown(
    id='select-regiao',
    options=regiao_options,
    clearable=True,
    placeholder="Selecione uma Região"
  
)

selecao_sexo = [{'label': sexo, 'value': sexo} for sexo in calcular['Sexo'].unique()]
dropdown_sexo = dcc.Dropdown(
    id='select-dose-sex',
    options=selecao_sexo,
    clearable=True,
    placeholder="Selecione um Sexo"
  
)

select_municipio = [{'label': municipio, 'value': municipio} for municipio in sorted(monovalente_cobertura_faixa_etaria_municipios['Município'].unique())]
dropdown_municipio = dcc.Dropdown(
    id='select-municipio-monovalente',
    options=select_municipio,
    clearable=True,
    placeholder="Selecione um Município"
  
)

limpar_filtro = dbc.Button("Limpar Filtro", id='limpar-filtro-btn-regiao', n_clicks=0, size='sm',color="success")

# ========================================================================== # CARDS # ========================================================================== #


def update_card_porcentagem(value, title):
    titulo = f"<span style='font-size:14px; font-weight:bold'><b>{title}</b></span>"
    valores = f"{titulo}<br><span style='font-size:27px'>{value:.2f}%</span>"

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


# ========================================================================== # CALLBACKS # ========================================================================== #




@callback(
    [#Output('select-dose', 'value'),
     Output('select-municipio-monovalente', 'value'),
     Output('select-regiao', 'value'),
     Output('select-dose-sex', 'value')],
    [Input('limpar-filtro-btn-regiao', 'n_clicks')],
    [State('select-regiao', 'value'),
     State('select-dose-sex', 'value'),
     #State('select-dose', 'value'),
     State('select-municipio-monovalente', 'value')])

def limpar_filtros(n_clicks, regiao_dropdown, sexo, municipio_dropdown):
    # Reseta os valores dos dropdowns quando o botão é clicado
    
    if n_clicks > 0:
        return [None, None, None]
    return [regiao_dropdown, sexo, municipio_dropdown]

@callback(
    [
        Output('tabela-regiao1', 'data'),
        Output('tabela-regiao2', 'data'),
        Output('bar-chart-primeira-dose-regiao', 'figure'),
        Output('bar-chart-segunda-dose-regiao', 'figure'),
        Output('bar-chart-regiao3', 'figure'),
        Output('bar-chart-regiao2', 'figure'),
        Output('bar-chart-terceira-dose-regiao', 'figure'),
        Output("bar-chart-primeira-dose-municipio", "figure"),
        Output("bar-chart-segunda-dose-municipio", "figure"),
        Output("bar-chart-terceira-dose-municipio", "figure"),
        Output('bar-chart-municipio1', 'figure'),
        Output('bar-chart-municipio2', 'figure'),
        Output('card1-regiao', 'figure'),
        Output('card2-regiao', 'figure'),
        Output('card3-regiao', 'figure'),
        Output('card4-regiao', 'figure'),
        Output('card5-regiao', 'figure'),
        Output('card6-regiao', 'figure'),
        Output('card7-regiao', 'figure'),
    ],
    [
        Input('map-choropleth-monovalente-terceira-dose-regiao', 'clickData'),
        Input('map-choropleth-monovalente-segunda-dose-regiao', 'clickData'),
        Input('map-choropleth-monovalente-primeira-dose-regiao', 'clickData'),
        Input('map-choropleth-monovalente-municipio-primeira-dose', 'clickData'),
        Input('map-choropleth-monovalente-municipio-segunda-dose', 'clickData'),
        Input('map-choropleth-monovalente-municipio-terceira-dose', 'clickData'),
        #Input('select-dose', 'value'),
        Input('select-dose-sex', 'value'),
        Input('select-regiao', 'value'),
        Input('limpar-filtro-btn-regiao', 'n_clicks'),
        Input('select-municipio-monovalente', 'value')
    ]
)


def update_bar_chart_and_table(choropleth_clickData, monovalente_clickData, monovalente_primeira, choropleth_municipio_primeira, choropleth_municipio_segunda, choropleth_municipio_terceira, sexo, regiao_dropdown, n_clicks_limpar, municipio_dropdown):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    selected_regiao = regiao_dropdown
    select_municipio = municipio_dropdown

    if trigger_id == 'limpar-filtro-btn-regiao' and n_clicks_limpar > 0:
        selected_regiao = None
        sexo = None
        select_municipio = None
    elif trigger_id in ['map-choropleth-monovalente-terceira-dose-regiao']:
        selected_regiao = choropleth_clickData['points'][0]['location'] if choropleth_clickData else regiao_dropdown

    elif trigger_id in ['map-choropleth-monovalente-segunda-dose-regiao']:
        selected_regiao = monovalente_clickData['points'][0]['location'] if monovalente_clickData else regiao_dropdown
    elif trigger_id in ['map-choropleth-monovalente-primeira-dose-regiao']:
        selected_regiao = monovalente_primeira['points'][0]['location'] if monovalente_primeira else regiao_dropdown
    elif trigger_id == 'select-regiao':
        selected_regiao = regiao_dropdown
    elif trigger_id == 'select-municipio-monovalente':
        select_municipio = municipio_dropdown
    elif trigger_id in ['map-choropleth-monovalente-municipio-primeira-dose']:
        select_municipio = choropleth_municipio_primeira['points'][0]['location'] if choropleth_municipio_primeira else municipio_dropdown
    elif trigger_id in ['map-choropleth-monovalente-municipio-segunda-dose']:
        select_municipio = choropleth_municipio_segunda['points'][0]['location'] if choropleth_municipio_segunda else municipio_dropdown
    elif trigger_id in ['map-choropleth-monovalente-municipio-terceira-dose']:
        select_municipio = choropleth_municipio_terceira['points'][0]['location'] if choropleth_municipio_terceira else municipio_dropdown
    elif trigger_id == 'select-dose-sex':
        sexo = sexo

 
    if select_municipio:
        ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### VALORES DE REGIOES REPLICADOS ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### 

        table_data = tabela_regiao.to_dict('records')
        filtro_cobertura_doses = monovalente_tabela_doses_regioes_sexo_agrupado
        filtro_cobertura_doses_municipio = cobertura_doses_municipio        

        cada_populacao_regiao = unir_dose3[(unir_dose3['Sexo'] == "Masculino") & (unir_dose3['Doses'] == '1ª DOSE')]['População Região'].sum()

        qtd_primeira_dose = unir_dose3[unir_dose3['Doses'] == '1ª DOSE']['Número de Vacinas'].sum()
        qtd_segunda_dose = unir_dose3[unir_dose3['Doses'] == '2ª DOSE']['Número de Vacinas'].sum()
        qtd_terceira_dose = unir_dose3[unir_dose3['Doses'] == '3ª DOSE']['Número de Vacinas'].sum()

        # variavel para calcular cada nivel de quantidade de doses aplicadas
        porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
        porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
        porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100

        # FILTROS GRAFICO BARRAS POR REGIAO/FAIXA ETÁRIA/NUMERO DE DOSES
        df_filtered_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        agrupado_sc_faixaetaria22 = tabela_cobertura_faixa_etaria.groupby(['Faixa Etária', 'Dose']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
        agrupado_sc_faixaetaria22['porcentagem'] = round(agrupado_sc_faixaetaria22['Número de Vacinas'] / agrupado_sc_faixaetaria22['População']*100,2)
        filtro_cobertura_faixa_etaria = agrupado_sc_faixaetaria22.groupby(['Faixa Etária', 'Dose']).sum().reset_index()
        ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### VALORES DE REGIOES REPLICADOS ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### 


        filtro_cobertura_faixa_etaria_municipio = tabela_cobertura_faixa_etaria_municipio[tabela_cobertura_faixa_etaria_municipio['Município'] == select_municipio].groupby(['Faixa Etária', 'Doses', 'Porcentagem (%)']).sum().reset_index()

        table_data_filtrada_municipio = tabela_monovalente_cobertura_municipios_plot[tabela_monovalente_cobertura_municipios_plot['Município']==select_municipio]
        # FILTROS GRAFICO BARRAS POR MUNICIPIO/FAIXA ETÁRIA/NUMERO DE DOSES
        filtro_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Município'] == select_municipio]
        filtro_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio[segunda_dose_porfaixaetaria_municipio['Município'] == select_municipio]
        filtro_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio[terceira_dose_porfaixaetaria_municipio['Município'] == select_municipio]

        cada_populacao_regiao = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Município'] == select_municipio]['População'].sum()

        filtro_cobertura_doses_municipio = cobertura_doses_municipio[cobertura_doses_municipio['Município'] == select_municipio]

        # quantidade de doses aplicadas filtradas.
        qtd_primeira_dose = filtro_faixa_etaria_primeira_dose_municipio['Número de Vacinas'].sum()
        qtd_segunda_dose = filtro_faixa_etaria_segunda_dose_municipio['Número de Vacinas'].sum()
        qtd_terceira_dose = filtro_faixa_etaria_terceira_dose_municipio['Número de Vacinas'].sum()

        # variavel para calcular cada nivel de quantidade de doses aplicadas
        porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
        porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
        porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100

        # Aplica filtro por sexo se estiver selecionado
        if sexo:

            table_data_municipio = table_data_filtrada_municipio[table_data_filtrada_municipio['Sexo'] == sexo].to_dict('records')

            # FILTROS GRAFICO BARRAS POR MUNICIPIO/FAIXA ETÁRIA/NUMERO DE DOSES
            df_filtered_faixa_etaria_primeira_dose_municipio = filtro_faixa_etaria_primeira_dose_municipio[filtro_faixa_etaria_primeira_dose_municipio['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_segunda_dose_municipio = filtro_faixa_etaria_segunda_dose_municipio[filtro_faixa_etaria_segunda_dose_municipio['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_terceira_dose_municipio = filtro_faixa_etaria_terceira_dose_municipio[filtro_faixa_etaria_terceira_dose_municipio['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            
            cada_populacao_regiao = filtro_faixa_etaria_primeira_dose_municipio[filtro_faixa_etaria_primeira_dose_municipio['Sexo'] == sexo]['População'].sum()

            qtd_primeira_dose = filtro_faixa_etaria_primeira_dose_municipio[filtro_faixa_etaria_primeira_dose_municipio['Sexo'] == sexo]['Número de Vacinas'].sum()
            qtd_segunda_dose = filtro_faixa_etaria_segunda_dose_municipio[filtro_faixa_etaria_segunda_dose_municipio['Sexo'] == sexo]['Número de Vacinas'].sum()
            qtd_terceira_dose = filtro_faixa_etaria_terceira_dose_municipio[filtro_faixa_etaria_terceira_dose_municipio['Sexo'] == sexo]['Número de Vacinas'].sum()

            porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
            porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
            porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100
        else:
            table_data_municipio = table_data_filtrada_municipio.to_dict('records')
            # FILTROS GRAFICO BARRAS POR MUNICIPIO/FAIXA ETÁRIA/NUMERO DE DOSES
            df_filtered_faixa_etaria_primeira_dose_municipio = filtro_faixa_etaria_primeira_dose_municipio
            df_filtered_faixa_etaria_segunda_dose_municipio = filtro_faixa_etaria_segunda_dose_municipio
            df_filtered_faixa_etaria_terceira_dose_municipio = filtro_faixa_etaria_terceira_dose_municipio

            porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
            porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
            porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100
            
    elif selected_regiao:
        ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### VALORES DE MUNICÍPIOS REPLICADOS ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### 
        filtro_cobertura_doses_municipio = cobertura_doses_municipio        
        agrupado_sc_faixaetaria2 = tabela_cobertura_faixa_etaria_municipio.groupby(['Faixa Etária', 'Doses']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
        agrupado_sc_faixaetaria2['Porcentagem (%)'] = round(agrupado_sc_faixaetaria2['Número de Vacinas'] / agrupado_sc_faixaetaria2['População']*100,2)        
        filtro_cobertura_faixa_etaria_municipio = agrupado_sc_faixaetaria2.groupby(['Faixa Etária', 'Doses']).sum().reset_index()

        table_data_municipio = tabela_monovalente_cobertura_municipios_plot.to_dict('records')
        # FILTROS GRAFICO BARRAS POR MUNICIPIO/FAIXA ETÁRIA/NUMERO DE DOSES
        df_filtered_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        cada_populacao_regiao = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Doses'] == '1ª DOSE']['População'].sum()

        qtd_primeira_dose = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Doses'] == '1ª DOSE']['Número de Vacinas'].sum()
        qtd_segunda_dose = segunda_dose_porfaixaetaria_municipio[segunda_dose_porfaixaetaria_municipio['Doses'] == '2ª DOSE']['Número de Vacinas'].sum()
        qtd_terceira_dose = terceira_dose_porfaixaetaria_municipio[terceira_dose_porfaixaetaria_municipio['Doses'] == '3ª DOSE']['Número de Vacinas'].sum()

        ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### VALORES DE MUNICÍPIOS REPLICADOS ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### ##### ====== ##### 
        
        unir_dose3_selected_1 = qtd_primeira_dose_filtrada[qtd_primeira_dose_filtrada['Região Saúde'] == selected_regiao]
        unir_dose3_selected_2 = qtd_segunda_dose_filtrada[qtd_segunda_dose_filtrada['Região Saúde'] == selected_regiao]
        unir_dose3_selected_3 = qtd_terceira_dose_filtrada[qtd_terceira_dose_filtrada['Região Saúde'] == selected_regiao]

        filtro_cobertura_doses_municipio = cobertura_doses_municipio[cobertura_doses_municipio['Região Saúde'] == selected_regiao].groupby(['Município', 'Doses']).sum().reset_index()

        table_data_filtrada = tabela_regiao[tabela_regiao['Região Saúde']==selected_regiao]
        # calculo para a população total filtrada
        cada_populacao_regiao = unir_dose3[(unir_dose3['Região Saúde'] == selected_regiao) & (unir_dose3['Doses'] == '1ª DOSE')]['População'].sum()

        # quantidade de doses aplicadas filtradas.
        qtd_primeira_dose = unir_dose3_selected_1[unir_dose3_selected_1['Doses'] == '1ª DOSE']['Número de Vacinas'].sum()
        qtd_segunda_dose = unir_dose3_selected_2[unir_dose3_selected_2['Doses'] == '2ª DOSE']['Número de Vacinas'].sum()
        qtd_terceira_dose = unir_dose3_selected_3[unir_dose3_selected_3['Doses'] == '3ª DOSE']['Número de Vacinas'].sum()

        # variavel para calcular cada nivel de quantidade de doses aplicadas
        porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
        porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
        porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100

        # FILTROS GRAFICO BARRAS POR REGIÃO/FAIXA ETÁRIA/NUMERO DE DOSES
        filtro_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria[primeira_dose_porfaixaetaria['Região Saúde'] == selected_regiao]
        filtro_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria[segunda_dose_porfaixaetaria['Região Saúde'] == selected_regiao]
        filtro_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria[terceira_dose_porfaixaetaria['Região Saúde'] == selected_regiao]

        filtro_cobertura_doses = monovalente_tabela_doses_regioes_sexo_agrupado[monovalente_tabela_doses_regioes_sexo_agrupado['Região Saúde'] == selected_regiao]


        filtro_cobertura_faixa_etaria = tabela_cobertura_faixa_etaria[tabela_cobertura_faixa_etaria['Região Saúde'] == selected_regiao].groupby(['Faixa Etária', 'Dose']).sum().reset_index()

        # Aplica filtro por sexo se estiver selecionado
        if sexo:
            table_data = table_data_filtrada[table_data_filtrada['Sexo'] == sexo].to_dict('records')
            cada_populacao_regiao = unir_dose3_selected_1[unir_dose3_selected_1['Sexo'] == sexo]['População'].sum()
            qtd_primeira_dose = unir_dose3_selected_1[unir_dose3_selected_1['Sexo'] == sexo]['Número de Vacinas'].sum()
            qtd_segunda_dose = unir_dose3_selected_2[unir_dose3_selected_2['Sexo'] == sexo]['Número de Vacinas'].sum()
            qtd_terceira_dose = unir_dose3_selected_3[unir_dose3_selected_3['Sexo'] == sexo]['Número de Vacinas'].sum()

            porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
            porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
            porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100

            # FILTROS GRAFICO BARRAS POR REGIÃO/FAIXA ETÁRIA/NUMERO DE DOSES
            df_filtered_faixa_etaria_primeira_dose = filtro_faixa_etaria_primeira_dose[filtro_faixa_etaria_primeira_dose['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_segunda_dose = filtro_faixa_etaria_segunda_dose[filtro_faixa_etaria_segunda_dose['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_terceira_dose = filtro_faixa_etaria_terceira_dose[filtro_faixa_etaria_terceira_dose['Sexo'] == sexo].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        else:
            table_data = table_data_filtrada.to_dict('records')
            # FILTROS GRAFICO BARRAS POR REGIAO/FAIXA ETÁRIA/NUMERO DE DOSES
            df_filtered_faixa_etaria_primeira_dose = filtro_faixa_etaria_primeira_dose
            df_filtered_faixa_etaria_segunda_dose = filtro_faixa_etaria_segunda_dose
            df_filtered_faixa_etaria_terceira_dose = filtro_faixa_etaria_terceira_dose

            porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
            porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
            porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100
    else:
        table_data_municipio = tabela_monovalente_cobertura_municipios_plot.to_dict('records')
        # FILTROS GRAFICO BARRAS POR MUNICIPIO/FAIXA ETÁRIA/NUMERO DE DOSES
        df_filtered_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        qtd_primeira_dose = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Doses'] == '1ª DOSE']['Número de Vacinas'].sum()
        qtd_segunda_dose = segunda_dose_porfaixaetaria_municipio[segunda_dose_porfaixaetaria_municipio['Doses'] == '2ª DOSE']['Número de Vacinas'].sum()
        qtd_terceira_dose = terceira_dose_porfaixaetaria_municipio[terceira_dose_porfaixaetaria_municipio['Doses'] == '3ª DOSE']['Número de Vacinas'].sum()

        table_data = tabela_regiao.to_dict('records')

        filtro_cobertura_doses = monovalente_tabela_doses_regioes_sexo_agrupado.groupby(['Região Saúde', 'Doses']).sum().reset_index()
        filtro_cobertura_doses_municipio = cobertura_doses_municipio

        cada_populacao_regiao = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Doses'] == '1ª DOSE']['População'].sum()
        cada_populacao_regiao = unir_dose3[(unir_dose3['Sexo'] == "Masculino") & (unir_dose3['Doses'] == '1ª DOSE')]['População Região'].sum()

        porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
        porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
        porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100
        
        # FILTROS GRAFICO BARRAS POR REGIAO/FAIXA ETÁRIA/NUMERO DE DOSES
        df_filtered_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
        df_filtered_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria.groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

        agrupado_sc_faixaetaria22 = tabela_cobertura_faixa_etaria.groupby(['Faixa Etária', 'Dose']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
        agrupado_sc_faixaetaria22['porcentagem'] = round(agrupado_sc_faixaetaria22['Número de Vacinas'] / agrupado_sc_faixaetaria22['População']*100,2)
        filtro_cobertura_faixa_etaria = agrupado_sc_faixaetaria22.groupby(['Faixa Etária', 'Dose']).sum().reset_index()

        agrupado_sc_faixaetaria2 = tabela_cobertura_faixa_etaria_municipio.groupby(['Faixa Etária', 'Doses']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
        agrupado_sc_faixaetaria2['Porcentagem (%)'] = round(agrupado_sc_faixaetaria2['Número de Vacinas'] / agrupado_sc_faixaetaria2['População']*100,2)        
        filtro_cobertura_faixa_etaria_municipio = agrupado_sc_faixaetaria2.groupby(['Faixa Etária', 'Doses']).sum().reset_index()


        if sexo:
            table_data = tabela_regiao[tabela_regiao['Sexo'] == sexo].to_dict('records')
            cada_populacao_regiao = unir_dose3[(unir_dose3['Sexo'] == sexo) & (unir_dose3['Doses'] == '1ª DOSE')]['População'].sum()
            
            qtd_primeira_dose = unir_dose3[(unir_dose3['Sexo'] == sexo) & (unir_dose3['Doses'] == '1ª DOSE')]['Número de Vacinas'].sum()
            qtd_segunda_dose = unir_dose3[(unir_dose3['Sexo'] == sexo) & (unir_dose3['Doses'] == '2ª DOSE')]['Número de Vacinas'].sum()
            qtd_terceira_dose = unir_dose3[(unir_dose3['Sexo'] == sexo) & (unir_dose3['Doses'] == '3ª DOSE')]['Número de Vacinas'].sum()


            # FILTROS GRAFICO BARRAS POR REGIAO/FAIXA ETÁRIA/NUMERO DE DOSES
            df_filtered_faixa_etaria_primeira_dose = df_filtered_faixa_etaria_primeira_dose[(df_filtered_faixa_etaria_primeira_dose['Sexo'] == sexo)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_segunda_dose = df_filtered_faixa_etaria_segunda_dose[(df_filtered_faixa_etaria_segunda_dose['Sexo'] == sexo)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_terceira_dose = df_filtered_faixa_etaria_terceira_dose[(df_filtered_faixa_etaria_terceira_dose['Sexo'] == sexo)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            cada_populacao_regiao = primeira_dose_porfaixaetaria_municipio[(primeira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (primeira_dose_porfaixaetaria_municipio['Doses'] == '1ª DOSE')]['População'].sum()

            porcentagem_primeiradose = (qtd_primeira_dose / cada_populacao_regiao) * 100
            porcentagem_segundadose = (qtd_segunda_dose / cada_populacao_regiao) * 100
            porcentagem_terceiradose = (qtd_terceira_dose / cada_populacao_regiao) * 100


            table_data_municipio = tabela_monovalente_cobertura_municipios_plot[tabela_monovalente_cobertura_municipios_plot['Sexo'] == sexo].to_dict('records')
            # FILTROS GRAFICO BARRAS POR MUNICIPIO/FAIXA ETÁRIA/NUMERO DE DOSES
            df_filtered_faixa_etaria_primeira_dose_municipio = df_filtered_faixa_etaria_primeira_dose_municipio[(df_filtered_faixa_etaria_primeira_dose_municipio['Sexo'] == sexo)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_segunda_dose_municipio = df_filtered_faixa_etaria_segunda_dose_municipio[(df_filtered_faixa_etaria_segunda_dose_municipio['Sexo'] == sexo)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
            df_filtered_faixa_etaria_terceira_dose_municipio = df_filtered_faixa_etaria_terceira_dose_municipio[(df_filtered_faixa_etaria_terceira_dose_municipio['Sexo'] == sexo)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

            qtd_primeira_dose = primeira_dose_porfaixaetaria_municipio[(primeira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (primeira_dose_porfaixaetaria_municipio['Doses'] == '1ª DOSE')]['Número de Vacinas'].sum()
            qtd_segunda_dose = segunda_dose_porfaixaetaria_municipio[(segunda_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (segunda_dose_porfaixaetaria_municipio['Doses'] == '2ª DOSE')]['Número de Vacinas'].sum()
            qtd_terceira_dose = terceira_dose_porfaixaetaria_municipio[(terceira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (terceira_dose_porfaixaetaria_municipio['Doses'] == '3ª DOSE')]['Número de Vacinas'].sum()



   # ======================================================================================= # FAIXA ETÁRIA REGIOES # ======================================================================================= #


#     if faixa_etaria:
#         if selected_regiao:
#             # Filtrar quando selecionarem o campo região saúde e faixa etária simultaneamente
#             filtro_cobertura_faixa_etaria = tabela_cobertura_faixa_etaria[(tabela_cobertura_faixa_etaria['Faixa Etária'] == faixa_etaria) & (tabela_cobertura_faixa_etaria['Região Saúde'] == selected_regiao)].groupby(['Faixa Etária', 'Dose', 'porcentagem']).sum().reset_index()
#             df_filtered_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria[(primeira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria) & (primeira_dose_porfaixaetaria['Região Saúde'] == selected_regiao)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria[(segunda_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria) & (segunda_dose_porfaixaetaria['Região Saúde'] == selected_regiao)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria[(terceira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria) & (terceira_dose_porfaixaetaria['Região Saúde'] == selected_regiao)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             if sexo:
#                 df_filtered_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria[(primeira_dose_porfaixaetaria['Sexo'] == sexo) & (primeira_dose_porfaixaetaria['Região Saúde'] == selected_regiao) & (primeira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria[(segunda_dose_porfaixaetaria['Sexo'] == sexo) & (segunda_dose_porfaixaetaria['Região Saúde'] == selected_regiao) & (segunda_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria[(terceira_dose_porfaixaetaria['Sexo'] == sexo) & (terceira_dose_porfaixaetaria['Região Saúde'] == selected_regiao) & (terceira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

#         else:
#             # Filtrar somente a faixa etária
#             agrupado_sc_faixaetaria22 = tabela_cobertura_faixa_etaria.groupby(['Faixa Etária', 'Dose']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
#             agrupado_sc_faixaetaria22['Porcentagem (%)'] = round(agrupado_sc_faixaetaria22['Número de Vacinas'] / agrupado_sc_faixaetaria22['População'] * 100, 2)
#             filtro_cobertura_faixa_etaria = agrupado_sc_faixaetaria22[agrupado_sc_faixaetaria22['Faixa Etária'] == faixa_etaria] 

#             df_filtered_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria[primeira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria[segunda_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria[terceira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

#             if sexo:
#                 df_filtered_faixa_etaria_primeira_dose = primeira_dose_porfaixaetaria[(primeira_dose_porfaixaetaria['Sexo'] == sexo) & (primeira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_segunda_dose = segunda_dose_porfaixaetaria[(segunda_dose_porfaixaetaria['Sexo'] == sexo) & (segunda_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_terceira_dose = terceira_dose_porfaixaetaria[(terceira_dose_porfaixaetaria['Sexo'] == sexo) & (terceira_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()


#    # ======================================================================================= # FAIXA ETÁRIA MUNICÍPIOS # ======================================================================================= #
#     if faixa_etaria:
#         if select_municipio:
#             # Filtrar quando selecionarem o campo região saúde e faixa etária simultaneamente
#             df_filtered_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio[(primeira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria) & (primeira_dose_porfaixaetaria_municipio['Município'] == select_municipio)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio[(segunda_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria) & (segunda_dose_porfaixaetaria_municipio['Município'] == select_municipio)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio[(terceira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria) & (terceira_dose_porfaixaetaria_municipio['Município'] == select_municipio)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

#             filtro_cobertura_faixa_etaria_municipio = tabela_cobertura_faixa_etaria_municipio[(tabela_cobertura_faixa_etaria_municipio['Faixa Etária'] == faixa_etaria) & (tabela_cobertura_faixa_etaria_municipio['Município'] == select_municipio)].groupby(['Faixa Etária', 'Doses', 'Porcentagem']).sum().reset_index()
            
#             if sexo:
#                 df_filtered_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio[(primeira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (primeira_dose_porfaixaetaria_municipio['Município'] == select_municipio) & (primeira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio[(segunda_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (segunda_dose_porfaixaetaria_municipio['Município'] == select_municipio) & (segunda_dose_porfaixaetaria['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio[(terceira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (terceira_dose_porfaixaetaria_municipio['Município'] == select_municipio) & (terceira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#         else:
#             df_filtered_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio[primeira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio[segunda_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#             df_filtered_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio[terceira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()


#             agrupado_sc_faixaetaria2 = tabela_cobertura_faixa_etaria_municipio.groupby(['Município','Faixa Etária', 'Doses']).agg({'Número de Vacinas':'sum', 'População':'sum'}).reset_index()
#             agrupado_sc_faixaetaria2 = agrupado_sc_faixaetaria2.groupby(['Faixa Etária', 'Doses']).sum().reset_index()
#             agrupado_sc_faixaetaria2['Porcentagem (%)'] = round(agrupado_sc_faixaetaria2['Número de Vacinas'] / agrupado_sc_faixaetaria2['População']*100,2)
#             filtro_cobertura_faixa_etaria_municipio = agrupado_sc_faixaetaria2[agrupado_sc_faixaetaria2['Faixa Etária'] == faixa_etaria].groupby(['Faixa Etária', 'Doses', 'Porcentagem']).sum().reset_index()


#             if sexo:
#                 df_filtered_faixa_etaria_primeira_dose_municipio = primeira_dose_porfaixaetaria_municipio[(primeira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (primeira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_segunda_dose_municipio = segunda_dose_porfaixaetaria_municipio[(segunda_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (segunda_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()
#                 df_filtered_faixa_etaria_terceira_dose_municipio = terceira_dose_porfaixaetaria_municipio[(terceira_dose_porfaixaetaria_municipio['Sexo'] == sexo) & (terceira_dose_porfaixaetaria_municipio['Faixa Etária'] == faixa_etaria)].groupby(['Faixa Etária', 'Sexo']).sum().reset_index()

    ###############################################
    
    df_filtered_faixa_etaria_primeira_dose['Número de Vacinas Num'] = df_filtered_faixa_etaria_primeira_dose['Número de Vacinas']

    # Aplicando a formatação e substituindo o separador
    df_filtered_faixa_etaria_primeira_dose.loc[:,'Número de Vacinas '] = df_filtered_faixa_etaria_primeira_dose['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

    # Definindo o mapeamento de cores para a coluna 'Doses' das barras
    color_map = {
        "1ª DOSE": '#f3ddb3',  
        "1ª REFORÇO": '#c1cd97',
        "2ª DOSE": '#f5c9bf',
        "2ª REFORÇO": '#8ac0de',
        "3ª DOSE": '#ecad8f'

    }

    bar_chart_figure1 = px.bar(
        df_filtered_faixa_etaria_primeira_dose,
        x='Faixa Etária',
        y='Número de Vacinas Num',  # Usar a coluna numérica para o eixo y
        text='Número de Vacinas ',  # Exibir os valores formatados como texto nas barras  
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},
        width=900,
        height=400,
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Contagem de Doses'},  # Ajuste nos labels
        title=f'QUANT. DE 1ª DOSE APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal
    )

    bar_chart_figure1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. DE 1ª DOSE APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
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
        bargap=0.05  # Aumentar o espaço entre as barras para parecer que há zoom
    )
    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure1.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )



    df_filtered_faixa_etaria_segunda_dose['Número de Vacinas Num'] = df_filtered_faixa_etaria_segunda_dose['Número de Vacinas']
    df_filtered_faixa_etaria_segunda_dose.loc[:,'Número de Vacinas '] = df_filtered_faixa_etaria_segunda_dose['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


    bar_chart_figure2 = px.bar(
        df_filtered_faixa_etaria_segunda_dose,
        x='Faixa Etária',
        y='Número de Vacinas Num',  # Usar a coluna numérica para o eixo y
        text='Número de Vacinas ',  # Exibir os valores formatados como texto nas barras  
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},  
        width=900,
        height=400,
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  
        title=f'QUANT. DE 2ª DOSE APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  
    )
    bar_chart_figure2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. DE 2ª DOSE APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
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
        bargap=0.1  # Aumentar o espaço entre as barras para parecer que há zoom
    )
    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure2.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )






    df_filtered_faixa_etaria_terceira_dose['Número de Vacinas Num'] = df_filtered_faixa_etaria_terceira_dose['Número de Vacinas']
    df_filtered_faixa_etaria_terceira_dose.loc[:,'Número de Vacinas '] = df_filtered_faixa_etaria_terceira_dose['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


    bar_chart_figure5 = px.bar(
        df_filtered_faixa_etaria_terceira_dose,
        x='Faixa Etária',
        y='Número de Vacinas Num',  # Usar a coluna numérica para o eixo y
        text='Número de Vacinas ',  # Exibir os valores formatados como texto nas barras  
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},  
        width=900,
        height=400,
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  
        title=f'QUANT. DE 3ª DOSE APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'} 
    )
    bar_chart_figure5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. DE 3ª DOSE APLICADAS POR FAIXA ETÁRIA EM {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
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
    bar_chart_figure5.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )

    ############################################### COBERTURA DE DOSES POR REGIAO ###############################################

    #Define o número máximo de informações a serem exibidas por vez
    max_info = 144

    #Filtra os dados para exibir apenas as primeiras 'max_info' informações
    filtro_cobertura_doses = filtro_cobertura_doses.head(max_info)

    bar_chart_figure3 = px.bar(
        filtro_cobertura_doses,
        x='Região Saúde',
        y='Porcentagem (%)',
        color='Doses',
        text='Porcentagem (%)',  # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        width=1900,
        height=650,
        title=f'COBERTURA DE DOSES POR REGIÃO (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        barmode='group',
        labels={'Região Saúde', 'Porcentagem'},
        color_discrete_map=color_map  # Correção no valor hexadecimal

    )   
    bar_chart_figure3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>COBERTURA DE DOSES POR REGIÃO (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}</b>',
            'font': {'size': 17, 'family': 'Arial'}  # Tamanho da fonte
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
        bargap=0.001  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure3.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )

    ############################################### COBERTURA DE DOSES POR FAIXA ETÁRIA (%) REGIAO ###############################################

    bar_chart_figure4 = px.bar(
        filtro_cobertura_faixa_etaria,
        x='Faixa Etária',
        y='porcentagem',  # Corrigido para corresponder ao nome correto da coluna
        color='Dose',
        text='porcentagem',  # Corrigido para corresponder ao nome correto da coluna
        width=1900,
        height=650,
        title=f'COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {selected_regiao if selected_regiao else "TODAS AS REGIÕES"}',
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'porcentagem': 'Porcentagem (%)'},  # Corrigido para ser um dicionário
        color_discrete_map=color_map  # Assume que color_map é definido corretamente em outro lugar
    )

    bar_chart_figure4.update_layout(
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
        bargap=0.001  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto dentro das barras
    bar_chart_figure4.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )


    ############################################### COBERTURA DE DOSES POR FAIXA ETÁRIA (%) MUNICIPIO ###############################################


    bar_chart_figure9 = px.bar(
        filtro_cobertura_faixa_etaria_municipio,
        x='Faixa Etária',
        y='Porcentagem (%)',
        color='Doses',
        text='Porcentagem (%)',  # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        width=1900,
        height=650,
        title=f'COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {select_municipio if select_municipio else "TODAS OS MUNICÍPIOS"}',
        barmode='group',
        labels={'Faixa Etária', 'Porcentagem (%)'},  # Ajuste no label para manter a consistência
        color_discrete_map=color_map  # Correção no valor hexadecimal

    )
    bar_chart_figure9.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>COBERTURA DE DOSES POR FAIXA ETÁRIA (%) {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}</b>',
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
        bargap=0.001  # Aumentar o espaço entre as barras para parecer que há zoom
    )

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure9.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )


    ############################################### COBERTURA DE DOSES POR FAIXA ETÁRIA (%) MUNICIPIO ###############################################

    # ideal é 144 colunas, para melhorar o zoom foi diminuido
    max_info2 = 120

    # Filtra os dados para exibir apenas as primeiras 'max_info2' informações
    filtro_cobertura_doses_municipio = filtro_cobertura_doses_municipio.head(max_info2)



    # # Criando o gráfico de barras
    bar_chart_figure10 = px.bar(
        filtro_cobertura_doses_municipio,
        x='Município',
        y='Porcentagem (%)',
        color='Doses',
        text='Porcentagem (%)',  # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
        width=1900,
        height=650,
        title=f'(%) COBERTURA DE DOSES POR {select_municipio if select_municipio else "MUNICÍPIO"}',
        barmode='group',
        labels={'Município', 'Porcentagem (%)'},
        color_discrete_map=color_map  # Aplica o mapeamento de cores
    )

    bar_chart_figure10.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>(%) COBERTURA DE DOSES POR {select_municipio if select_municipio else "MUNICÍPIO"}</b>',
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
        bargap=0.001  # Aumentar o espaço entre as barras para parecer que há zoom
    ),



    # Atualiza todas as trilhas para exibir os rótulos de texto dentro das barras
    bar_chart_figure10.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )

    # Criar o gráfico de barras
    # # Criando o gráfico de barras

    # bar_chart_figure10 = px.bar(
    #     filtro_cobertura_doses_municipio,
    #     x='Município',
    #     y='Porcentagem (%)',
    #     color='Doses',
    #     text='Porcentagem (%)',  # Adiciona os rótulos de texto com os valores da coluna 'Porcentagem'
    #     width=80850,
    #      height=450,
    #     title='COBERTURA DE DOSES POR MUNICIPIO',
    #     barmode='group'
    # )

    # # Atualizar o layout para melhorar a visualização
    # bar_chart_figure10.update_layout(
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     legend=dict(
    #         orientation="v",  
    #         yanchor="top",
    #         y=1.1,
    #         xanchor="center",

    #         x=-0.12
    #     ),
    #     title={
    #         'text': '<b>COBERTURA DE DOSES POR MUNICIPIO</b>',
    #         'font': {'size': 20, 'family': 'Arial'}
    #     },
    #     xaxis={
    #         'title': 'Município',
    #         'automargin': True,
    #         'tickangle': -45  # Rotacionar os rótulos do eixo x para melhor visualização
    #     },
    #     yaxis={
    #         'title': 'Contagem de Doses',
    #         'automargin': True
    #     },
    #     bargap=0.01  # Aumentar o espaço entre as barras para parecer que há zoom
    # )
    # # Converter o gráfico para HTML
    # html_chart = bar_chart_figure10.to_html(full_html=False)

    # # Salvar o HTML em um arquivo temporário e abrir no navegador
    # with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
    #     f.write(f'<div style="overflow-x: auto; width: 100%;">{html_chart}</div>')
    #     temp_file_path = f.name

    # webbrowser.open(f'file://{temp_file_path}')


    # ======================================================================================== # GRAFICO BARRAS FAIXA ETÁRIA/CONTAGEM DOSES/ MUNICÍPIOS     # ============
 
    df_filtered_faixa_etaria_primeira_dose_municipio['Número de Vacinas Num'] = df_filtered_faixa_etaria_primeira_dose_municipio['Número de Vacinas']
    df_filtered_faixa_etaria_primeira_dose_municipio.loc[:,'Número de Vacinas '] = df_filtered_faixa_etaria_primeira_dose_municipio['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))

    
    # PRIMEIRA DOSE POR FAIXA ETÁRIA / CONTAGEM DOSES / MUNICÍPIOS
    bar_chart_figure6 = px.bar(
        df_filtered_faixa_etaria_primeira_dose_municipio,
        x='Faixa Etária',
        y='Número de Vacinas Num',  # Usar a coluna numérica para o eixo y
        text='Número de Vacinas ',  # Exibir os valores formatados como texto nas barras  
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},  
        width=900,
        height=400,
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  # As labels ajustadas para remover os nomes dos eixos
        title=f'QUANT. 1ª DOSE APLICADAS POR FAIXA ETÁRIA EM {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}',
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal
    )

    bar_chart_figure6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. 1ª DOSE APLICADAS POR FAIXA ETÁRIA EM {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}</b>',
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
        bargap=0.01  # Aumentar o espaço entre as barras para parecer que há zoom
    ),

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure6.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )





    df_filtered_faixa_etaria_segunda_dose_municipio['Número de Vacinas Num'] = df_filtered_faixa_etaria_segunda_dose_municipio['Número de Vacinas']
    df_filtered_faixa_etaria_segunda_dose_municipio.loc[:,'Número de Vacinas '] = df_filtered_faixa_etaria_segunda_dose_municipio['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
    

    # SEGUNDA DOSE POR FAIXA ETÁRIA / CONTAGEM DOSES / MUNICÍPIOS
    bar_chart_figure7 = px.bar(
        df_filtered_faixa_etaria_segunda_dose_municipio,
        x='Faixa Etária',
        y='Número de Vacinas Num',  # Usar a coluna numérica para o eixo y
        text='Número de Vacinas ',  # Exibir os valores formatados como texto nas barras  
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},  
        width=900,
        height=400,
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  # As labels ajustadas para remover os nomes dos eixos
        title=f'QUANT. 2ª DOSE APLICADAS POR FAIXA ETÁRIA EM {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}',
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal
    )

    bar_chart_figure7.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. 2ª DOSE APLICADAS POR FAIXA ETÁRIA EM {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}</b>',
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
    ),

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure7.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )

    df_filtered_faixa_etaria_terceira_dose_municipio['Número de Vacinas Num'] = df_filtered_faixa_etaria_terceira_dose_municipio['Número de Vacinas']
    df_filtered_faixa_etaria_terceira_dose_municipio.loc[:,'Número de Vacinas '] = df_filtered_faixa_etaria_terceira_dose_municipio['Número de Vacinas Num'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
 


    # TERCEIRA DOSE POR FAIXA ETÁRIA / CONTAGEM DOSES / MUNICÍPIOS
    bar_chart_figure8 = px.bar(
        df_filtered_faixa_etaria_terceira_dose_municipio,
        x='Faixa Etária',
        y='Número de Vacinas Num',  # Usar a coluna numérica para o eixo y
        text='Número de Vacinas ',  # Exibir os valores formatados como texto nas barras  
        color='Sexo',
        hover_data={'Número de Vacinas ': True, 'Número de Vacinas Num': False},  
        width=900,
        height=400,
        barmode='group',
        labels={'Faixa Etária': 'Faixa Etária', 'Número de Vacinas': 'Número de Vacinas'},  # As labels ajustadas para remover os nomes dos eixos
        title=f'QUANT. 3ª DOSE APLICADAS POR FAIXA ETÁRIA EM {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}',
        color_discrete_map={'Masculino': '#8ac0de', 'Feminino': '#f5c9bf'}  # Correção no valor hexadecimal
    )

    bar_chart_figure8.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text': f'<b>QUANT. 3ª DOSE APLICADAS POR FAIXA ETÁRIA EM {select_municipio if select_municipio else "TODOS OS MUNICÍPIOS"}</b>',
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
    ),

    # Atualiza todas as trilhas para exibir os rótulos de texto fora das barras
    bar_chart_figure8.update_traces(
        textposition='inside',
        textfont={'size': 20}  # Aumentar o tamanho do texto dos rótulos
    )



    cada_populacao_regiao = 0 if cada_populacao_regiao is None or pd.isna(cada_populacao_regiao) else cada_populacao_regiao
    qtd_primeira_dose = 0 if qtd_primeira_dose is None or pd.isna(qtd_primeira_dose) else qtd_primeira_dose
    qtd_segunda_dose = 0 if qtd_segunda_dose is None or pd.isna(qtd_segunda_dose) else qtd_segunda_dose
    qtd_terceira_dose = 0 if qtd_terceira_dose is None or pd.isna(qtd_terceira_dose) else qtd_terceira_dose
    porcentagem_primeiradose = 0 if porcentagem_primeiradose is None or pd.isna(porcentagem_primeiradose) else porcentagem_primeiradose
    porcentagem_segundadose = 0 if porcentagem_segundadose is None or pd.isna(porcentagem_segundadose) else porcentagem_segundadose
    porcentagem_terceiradose = 0 if porcentagem_terceiradose is None or pd.isna(porcentagem_terceiradose) else porcentagem_terceiradose


    # Formatar os valores
    cada_populacao_regiao = f"{cada_populacao_regiao:,.0f}".replace(',', '.')
    qtd_primeira_dose = f"{qtd_primeira_dose:,.0f}".replace(',', '.')
    qtd_segunda_dose = f"{qtd_segunda_dose:,.0f}".replace(',', '.')
    qtd_terceira_dose = f"{qtd_terceira_dose:,.0f}".replace(',', '.')


    # Atualizar os valores nos cartões
    new_figure_card1 = update_card_string(cada_populacao_regiao, "POPULAÇÃO <br> TOTAL")
    new_figure_card2 = update_card_string(qtd_primeira_dose, "QUANT. 1ª DOSES")
    new_figure_card3 = update_card_porcentagem(porcentagem_primeiradose, "COBERTURA <br> 1ª DOSE")
    new_figure_card4 = update_card_string(qtd_segunda_dose, "QUANT. 2ª DOSES")
    new_figure_card5 = update_card_porcentagem(porcentagem_segundadose, "COBERTURA <br> 2ª DOSE")
    new_figure_card6 = update_card_string(qtd_terceira_dose, "QUANT. 3ª DOSES")
    new_figure_card7 = update_card_porcentagem(porcentagem_terceiradose, "COBERTURA <br> 3ª DOSE")


    return table_data, table_data_municipio, bar_chart_figure1, bar_chart_figure2, bar_chart_figure3, bar_chart_figure4, bar_chart_figure5, bar_chart_figure6, bar_chart_figure7, bar_chart_figure8, bar_chart_figure9, bar_chart_figure10, new_figure_card1, new_figure_card2, new_figure_card3, new_figure_card4, new_figure_card5, new_figure_card6, new_figure_card7

@callback(
    [
        Output("bar-chart-terceira-dose-regiao", "style"),
        Output("map-choropleth-monovalente-terceira-dose-regiao", "style"),
        Output("bar-chart-terceira-dose-municipio", "style"),
        Output("map-choropleth-monovalente-municipio-terceira-dose", "style"),

        Output("bar-chart-segunda-dose-regiao", "style"),
        Output("map-choropleth-monovalente-segunda-dose-regiao", "style"),
        Output("bar-chart-segunda-dose-municipio", "style"),
        Output("map-choropleth-monovalente-municipio-segunda-dose", "style"),

        Output("bar-chart-primeira-dose-regiao", "style"),
        Output("map-choropleth-monovalente-primeira-dose-regiao", "style"),
        Output("bar-chart-primeira-dose-municipio", "style"),
        Output("map-choropleth-monovalente-municipio-primeira-dose", "style")
    ],
    [
        Input("btn-segunda-dose", "n_clicks"),
        Input("btn-primeira-dose", "n_clicks"),
        Input("btn-terceira-dose", "n_clicks")
    ]
)
def toggle_visualization(btn_segunda_dose, btn_terceira_dose, btn_primeira_dose):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "btn-primeira-dose"  # Definir o botão 1º DOSE como padrão
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Pegar o estilo ativo e o estilo padrão do botão "btn-primeira-dose"
    active_style = {"display": "block", 'width': '900px', 'height': '450px'}
    default_style = {"display": "none",'width': '900px', 'height': '450px'}

    styles = [default_style] * 12  # 12 saídas correspondendo a 3 doses * 4 estilos

    # Atualiza os estilos com base no botão clicado
    if button_id == "btn-primeira-dose":
        styles[8] = styles[9] = styles[10] = styles[11] = active_style  # Primeira dose região e município
    elif button_id == "btn-segunda-dose":
        styles[4] = styles[5] = styles[6] = styles[7] = active_style  # Segunda dose região e município
    elif button_id == "btn-terceira-dose":
        styles[0] = styles[1] = styles[2] = styles[3] = active_style  # Terceira dose região e município

    return styles

@callback(
    [
        Output("btn-primeira-dose", "outline"),
        Output("btn-segunda-dose", "outline"),
        Output("btn-terceira-dose", "outline")
    ],
    [
        Input("btn-primeira-dose", "n_clicks"),
        Input("btn-segunda-dose", "n_clicks"),
        Input("btn-terceira-dose", "n_clicks")
    ]
)

def update_button_style(n1, n2, n3):
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == "btn-primeira-dose":
        return False, True, True
    elif triggered_id == "btn-segunda-dose":
        return True, False, True
    elif triggered_id == "btn-terceira-dose":
        return True, True, False
    return True, True, True
    
# =========  Layout  =========== #


tabela_monovalente_cobertura_municipios_plot['População Município '] = tabela_monovalente_cobertura_municipios_plot['População Município'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_monovalente_cobertura_municipios_plot['Número de Vacinas '] = tabela_monovalente_cobertura_municipios_plot['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_monovalente_cobertura_municipios_plot['População Sexo '] = tabela_monovalente_cobertura_municipios_plot['População Sexo'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


tabela_regiao['População Região '] = tabela_regiao['População Região'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_regiao['Número de Vacinas '] = tabela_regiao['Número de Vacinas'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))
tabela_regiao['População Sexo '] = tabela_regiao['População Sexo'].astype(str).apply(lambda x: f"{int(float(x)):,.0f}".replace(',', '.'))


# ===================================================================== # CALLBACKS PARA GERAR TABELA DE EXCEL # ===================================================================== #

@callback(
    Output('download-excel-regiao', 'data'),
    Input('csv-export-button-regiao', 'n_clicks'),
    State('tabela-regiao1', 'columns'),
    State('tabela-regiao1', 'derived_virtual_data'),
    prevent_initial_call=True
)
def export_excel_regiao(n_clicks, columns, filtered_data):
    if n_clicks:
        df = pd.DataFrame(filtered_data)
        visible_columns = [col['id'] for col in columns]
        df_export = df[visible_columns]
        return dcc.send_data_frame(df_export.to_excel, "tabela_monovalente_regiao.xlsx", index=False)


@callback(
    Output('download-excel', 'data'),
    Input('csv-export-button', 'n_clicks'),
    State('tabela-regiao2', 'columns'),
    State('tabela-regiao2', 'derived_virtual_data'),
    prevent_initial_call=True
)
def export_excel_municipio(n_clicks, columns, filtered_data):
    if n_clicks:
        df = pd.DataFrame(filtered_data)
        visible_columns = [col['id'] for col in columns]
        df_export = df[visible_columns]
        return dcc.send_data_frame(df_export.to_excel, "tabela_monovalente_municipio.xlsx", index=False)

# ===================================================================== # CALLBACKS PAR DE EXCEL # ===================================================================== #



cores_matriz2 = {
    'Masculino': '#ff9999',
    'Feminino': '#66b3ff',
}

# markdown_text = '''
# Exemplo para aplicar Markdown no painel.

# '''

# # Callback para abrir e fechar o modal
# @callback(
#     dash.dependencies.Output("modal-monovalente", "is_open"),
#     [dash.dependencies.Input("open-monovalente", "n_clicks"),
#      dash.dependencies.Input("close-monovalente", "n_clicks")],
#     [dash.dependencies.State("modal-monovalente", "is_open")],
# )
# def toggle_modal(open_clicks, close_clicks, is_open):
#     if open_clicks or close_clicks:
#         return not is_open
#     return is_open



layout = html.Div([

    dbc.Row([
        dbc.Col(width=4),  # Espaço extra à esquerda, se necessário
        dbc.Col([
            html.Div([
                html.Img(src="/vacinometro-dev/assets/syringe-solid.svg", style={
                    'height': '50px',  # Altura do ícone
                    'marginRight': '5px'  # Espaço à direita do ícone
                }),
                html.H1('PAINEL COBERTURA VACINAL MONOVALENTE', style={
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

    dbc.Row([ # COGELAR A PRIMEIRA LINHA PARA ACOMPANHAR O ROLLSCROLL DA PAGINA
        dbc.Col([  # Outer container
            dbc.Col([  # Inner container for image
                html.Img(
                    src="https://www.saude.sc.gov.br/images/stories/website/2023_marca_ses.png",
                    alt="Logotipo da Saúde SC",
                    style={'width': '70%', 'height': '70%', 'margin-top': '10px'}
                )
            ], style={'text-align': 'center'}),  # Add text-align: center
        ], sm=2, lg=2),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        dropdown_municipio
                    ])
                ]),
                style={'border': 0}
            )
        ],sm=2, lg=2),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        dropdown_sexo
                    ])
                ]),
                style={'border': 0}
            )
        ],sm=2, lg=2), 

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        #html.P("SELECIONE UM MUNICIPIO", style={'font-size': '10px'}),  
                        dropdown_regiao              
                    ]),
                ]),
                style={'border': 0}
            )
        ],sm=2, lg=2),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        limpar_filtro
                    ])
                ]),
                style={'border': 0}
            )
        ],sm=2, lg=2),
        
        # dbc.Col(
        #     dbc.Card(
        #         dbc.CardBody([
        #             dbc.Button("Informações", id="open-monovalente", color='success'),
                
        #             # Modal que contém as informações em Markdown
        #             dbc.Modal(
        #                 [
        #                     dbc.ModalHeader("Informações Adicionais"),
        #                     dbc.ModalBody(dcc.Markdown(children=markdown_text)),
        #                     dbc.ModalFooter(
        #                         dbc.Button("Fechar", id="close-monovalente", className="ml-auto")
        #                     ),
        #                 ],
        #                 id="modal-monovalente",
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
                dbc.CardBody(
                    dcc.Graph(id='card2-regiao', config={"displayModeBar": False}),
                ),
            style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),

        # SEGUNDA DOSE
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card4-regiao', config={"displayModeBar": False}),
                ),
            style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
        # TERCEIRA DOSE

        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card6-regiao', config={"displayModeBar": False}),
                ),
            style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
        # POPULAÇÃO
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card1-regiao', config={"displayModeBar": False}),
                ),
            style={'backgroundColor': '#f8f9fa'}  # Defina a cor de fundo do card inteiro
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
        ),

    ]),


    dbc.Row([

        dbc.Col([
            dbc.Card(
                dbc.CardBody([

                ]),
                style={'border': 0}
            )
        ],sm=2, lg=2),

        # COBERTURA (%) PRIMEIRA DOSE
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card3-regiao', config={"displayModeBar": False}),
                    style={'backgroundColor': '#f8f9fa'}
                ),
            style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),
        # COBERTURA (%) SEGUNDA DOSE

        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card5-regiao', config={"displayModeBar": False}),
                ),
            style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mb-4"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),

        # COBERTURA (%) TERCEIRA DOSE

        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id='card7-regiao', config={"displayModeBar": False}),
                ),
            style={'backgroundColor': '#f8f9fa'}
            ),
            xs=12, sm=6, md=4, lg=2, xl=2,
            className="mt-1"  # Adiciona um espaçamento na parte inferior quando os cards empilham
        ),

    ]),

    dbc.Row([
        dbc.Col([], width=5),
        dbc.Col([
            dbc.Button("1ª DOSE", id="btn-primeira-dose", color="success", outline=True, className="mr-2 text-center", n_clicks=0, style={'margin-right': '5px'}),
            dbc.Button("2ª DOSE", id="btn-segunda-dose", color="success", outline=True, className="mr-2 text-center", n_clicks=0, style={'margin-right': '5px'}),
            dbc.Button("3ª DOSE", id="btn-terceira-dose", color="success", outline=True, className="mr-2 text-center", n_clicks=0, style={'margin-right': '5px'}),
        ], width=4),
        dbc.Col([], width=3)
    ], style={'height': 'calc(100% - 100px)', 'width': '100%'}, className='mt-2'),

    # quero que cada mapa coropletico respeito o tamanhao 900px largura por 350px  de altura
    #map-choropleth-monovalente-municipio-primeira-dose

    # No seu layout, você pode definir um estilo específico para cada gráfico de mapa choropleth
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='map-choropleth-monovalente-primeira-dose-regiao',
                        className='dbc',
                        config=config_graph,
                        figure=figure1,
                        #style={'width': '500px', 'height': '350px'},
                        responsive=True
                    ),
                    dcc.Graph(
                        id='map-choropleth-monovalente-segunda-dose-regiao',
                        className='dbc',
                        config=config_graph,
                        figure=figure2,
                        #style={'width': '500px', 'height': '350px'},
                        responsive=True
                    ),
                    dcc.Graph(
                        id='map-choropleth-monovalente-terceira-dose-regiao',
                        className='dbc',
                        config=config_graph,
                        figure=figure3,
                        #style={'width': '500px', 'height': '350px'},
                        responsive=True
                    ),
                ]),
            ],style={'border':0})
        ], sm=6, md=6, lg=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='map-choropleth-monovalente-municipio-primeira-dose',
                        className='dbc',
                        config=config_graph,
                        figure=figure4,
                        #style={'width': '500px', 'height': '350px'},
                        responsive=True
                    ),
                    dcc.Graph(
                        id='map-choropleth-monovalente-municipio-segunda-dose',
                        className='dbc',
                        config=config_graph,
                        figure=figure5,
                        #style={'width': '500px', 'height': '350px'},
                        responsive=True
                    ),
                    dcc.Graph(
                        id='map-choropleth-monovalente-municipio-terceira-dose',
                        className='dbc',
                        config=config_graph,
                        figure=figure6,
                        #style={'width': '500px', 'height': '350px'},
                        responsive=True
                    ),
                ]),
            ],style={'border':0})
        ], sm=6, md=6, lg=6),
    ], style={'width': '100%', 'height': '100%'}),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                        dcc.Graph(
                            id='bar-chart-primeira-dose-regiao',
                            className='dbc',
                            config=config_graph,
                            #style={'width': '90%', 'height': '350px'},  # Ajuste para usar largura responsiva
                            responsive=True
                        ),
                        dcc.Graph(
                            id='bar-chart-segunda-dose-regiao',
                            className='dbc',
                            config=config_graph,
                            #style={'width': '90%', 'height': '350px'},  # Ajuste para usar largura responsiva
                            responsive=True
                        ),
                        dcc.Graph(
                            id='bar-chart-terceira-dose-regiao',
                            className='dbc',
                            config=config_graph,
                            #style={'width': '90%', 'height': '350px'},  # Ajuste para usar largura responsiva
                            responsive=True
                        )  
                ],style={'padding': '10px'}),  # Adjust padding as needed)
            ],style={'border':0})
        ], sm=6, md=6, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                        dcc.Graph(
                            id='bar-chart-primeira-dose-municipio',
                            className='dbc',
                            config=config_graph,
                            #style={'width': '90%', 'height': '350px'},  # Ajuste para usar largura responsiva
                            responsive=True
                        ),
                        dcc.Graph(
                            id='bar-chart-segunda-dose-municipio',
                            className='dbc',
                            config=config_graph,
                            #style={'width': '90%', 'height': '350px'},  # Ajuste para usar largura responsiva
                            responsive=True
                        ),
                        dcc.Graph(
                            id='bar-chart-terceira-dose-municipio',
                            className='dbc',
                            config=config_graph,
                            #style={'width': '90%', 'height': '350px'},  # Ajuste para usar largura responsiva
                            responsive=True
                        )
                ],style={'padding': '10px'}),  # Adjust padding as needed)
            ],style={'border':0})
        ], sm=6, md=6, lg=6),
    ], style={'width': '100%', 'height': '100%'}),




    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='bar-chart-regiao2',
                        className='dbc',
                        config=config_graph,
                        responsive=True  # Certifique-se de que responsive esteja configurado corretamente se deseja que o gráfico se ajuste ao tamanho do contêiner
                    )
                ], style={'padding': '10px'})  # Ajuste o padding conforme necessário
            ], style={'border': 0, 'overflowX': 'auto'})  # Adicione overflowX: 'auto' para a barra de rolagem horizontal
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'height': '100%'}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='bar-chart-regiao3',
                        className='dbc',
                        config=config_graph,
                        responsive=True  # Certifique-se de que responsive esteja configurado corretamente se deseja que o gráfico se ajuste ao tamanho do contêiner
                    )
                ], style={'padding': '10px', 'overflowX': 'auto'})  # Ajuste o padding e adicione overflowX: 'auto' para a barra de rolagem horizontal
            ], style={'border': 0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'height': '100%'}),



    dbc.Row([
        dbc.Col([
            dbc.Card([
                     dbc.CardBody([
                            #html.H5('COBERTURA DE DOSES POR FAIXA ETÁRIA (%)'),
                                dcc.Graph(id='bar-chart-municipio1', className='dbc', config=config_graph, responsive=True) # VARIAVEL DO GRAFICO BARRAS
            ], style={'border':0, 'overflow-x':'auto'})
            ],style={'border':0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'height': '100%'}),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                    dcc.Graph(
                        id='bar-chart-municipio2',
                        className='dbc',
                        config=config_graph,
                        responsive=True
                    )
            ], style={'border':0, 'overflow-x':'auto'})
            ], style={'border': 0})
        ], sm=12, md=12, lg=12),
    ], style={'width': '100%', 'height': '100%'}),


    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('TABELA DE COBERTURA VACINAL POR REGIÃO, SEXO E DOSE'),
                    html.Button("Exportar Excel", id="csv-export-button-regiao", className="mb-2"),
                    html.Div(
                        dash_table.DataTable(
                            id='tabela-regiao1',
                            sort_action='native',
                            sort_mode='multi',
                            columns=[
                                {"name": "Região Saúde", "id": "Região Saúde"},
                                {"name": "Doses", "id": "Doses"},
                                {"name": "Sexo", "id": "Sexo"},
                                {"name": "Porcentagem (%)", "id": "Porcentagem (%)"},
                                {"name": "População Região ", "id": "População Região "},
                                {"name": "Número de Vacinas ", "id": "Número de Vacinas "},
                                {"name": "População Sexo ", "id": "População Sexo "}
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
    dcc.Download(id='download-excel-regiao'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('TABELA DE COBERTURA VACINAL POR MUNICÍPIO, SEXO E DOSE'),
                    html.Button("Exportar Excel", id="csv-export-button", className="mb-2"),
                    html.Div(
                        dash_table.DataTable(
                            id='tabela-regiao2',
                            sort_action='native',
                            sort_mode='multi',
                            columns=[
                                {"name": "Município", "id": "Município"},
                                {"name": "Doses", "id": "Doses"},
                                {"name": "Sexo", "id": "Sexo"},
                                {"name": "Porcentagem (%)", "id": "Porcentagem (%)"},
                                {"name": "População Município ", "id": "População Município "},
                                {"name": "Número de Vacinas ", "id": "Número de Vacinas "},
                                {"name": "População Sexo ", "id": "População Sexo "}
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
    dcc.Download(id='download-excel')


], style={'width': '100%', 'height': '100%'})

