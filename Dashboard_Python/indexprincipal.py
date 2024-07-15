import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output

# Configurando a aplicação Dash com suppress_callback_exceptions=True
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, requests_pathname_prefix='/vacinometro-dev/')

app.layout = html.Div([
    dbc.Container([
        html.Div([
            dbc.Button(
                "Bivalente",
                href="/vacinometro-dev/",
                color="success",
                className="me-1 btn-sm",
                external_link=True,
                style={'textDecoration': 'none', 'marginTop': '10px'}
            ),
            dbc.Button(
                "Monovalente",
                href="/vacinometro-dev/monovalente",
                color="success",
                className="me-1 btn-sm",
                external_link=True,
                style={'textDecoration': 'none', 'marginTop': '10px'}
            ),
        ], className="d-flex flex-wrap justify-content-center"),
        html.Hr(),
    ]),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
], style={'height': '100%', 'width': "100%"})

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == "/vacinometro-dev/monovalente":
        import pages.monovalente as monovalente
        return monovalente.layout
    else:
        pathname == "/vacinometro-dev/"
        import pages.bivalente as bivalente
        return bivalente.layout

# adicionando 'debug=False' não havera o icone no canto infeior direito na tela.
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)



