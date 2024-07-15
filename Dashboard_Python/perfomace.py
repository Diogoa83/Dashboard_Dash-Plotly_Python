import pandas as pd
import psycopg2
from psycopg2 import pool

# Configuração da conexão
conexao_info = {
    'database': "******",
    'host': "******",
    'user': "******",
    'password': "******",
    'port': "****"
}

# Criação do pool de conexões
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **conexao_info)

def executar_consulta(query):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
        return pd.DataFrame(resultados, columns=colunas)
    finally:
        connection_pool.putconn(conn)

# ---------------------------------------------- # BIVALENTE # ---------------------------------------------- #
query1 = "SELECT * FROM painel_python.tabela_bivalente_cobertura_municipios"
query2 = "SELECT * FROM painel_python.tabela_bivalente_cobertura_doses_faixa_etaria_regiao"
query3 = "SELECT * FROM painel_python.tabela_monovalente_cobertura_municipios"
query4 = "SELECT * FROM ibge.ibge_com_faixa_etaria_ano WHERE ano = '2022' and idade >= '12'"
# --------------------------------------------- # MONOVALENTE # --------------------------------------------- #
query5 = "SELECT * FROM painel_python.tabela_monovalente_doses_faixaetaria_regioes"
query6 = "SELECT * FROM painel_python.tabela_monovalente_tabela_doses_regioes"
query7 = "SELECT * FROM painel_python.tabela_monovalente_cobertura_faixa_etaria_pop"
query8 = "SELECT * FROM painel_python.tabela_monovalente_completa_cobertura"
query9 = "SELECT * FROM painel_python.tabela_monovalente_cobertura_municipios"
query10 = "SELECT * FROM painel_python.tabela_monovalente_cobertura_doses_faixa_etaria_municipios"

# ---------------------------------------------- # BIVALENTE # ---------------------------------------------- #
df_municipio = executar_consulta(query1)
df_regiao = executar_consulta(query2)
df_tabela_populacao_municipio = executar_consulta(query3)
populacao_total_bivalente = executar_consulta(query4)
# --------------------------------------------- # MONOVALENTE # --------------------------------------------- #
tabela_faixa_etaria = executar_consulta(query5)
tabela_completa = executar_consulta(query6)
tabela_cobertura_faixa_etaria = executar_consulta(query7)
tabela_monovalente_completa_cobertura = executar_consulta(query8)
tabela_monovalente_cobertura_municipios = executar_consulta(query9)
monovalente_cobertura_faixa_etaria_municipios = executar_consulta(query10)