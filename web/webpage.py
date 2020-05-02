import dash
import dash_core_components as dcc
import dash_html_components as html

print(dcc.__version__) # 0.6.0 or above is required

external_stylesheets = ['https://www.w3schools.com/w3css/4/w3.css', "https://fonts.googleapis.com/css?family=Poppins", "styleSheet.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



styleDictMain = {
  # For body, h1-5
  "font-family": "Poppins, sans-serif"
}

styleDictBody = {
  "font-size": "16px"
}


# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div([
    html.Nav([
    html.Br(),
    # Add callback
    html.A("Close Menu", href="javascript:void(0)", className="w3-button w3-hide-large w3-display-topleft", style={"width":"100%","font-size":"22px"}, id="closeMenuLink", n_clicks=0),

    html.Div([
        html.H3("Company Name", className="w3-padding-64", style=styleDictMain),
    ], className="w3-container"),

    html.Div([
        # dcc.Location(id='url', refresh=False),
        dcc.Link("Visuals", href="/page-1", className="w3-bar-item w3-button w3-hover-white", id="visualsLink"),
        dcc.Link("About", href="/page-2", className="w3-bar-item w3-button w3-hover-white", id="aboutLink")
    ], className="w3-bar-block")
    
  ],className="w3-sidebar w3-red w3-collapse w3-top w3-large w3-padding", style={"z-index":"3","width":"300px","font-weight":"bold"}, id="mySidebar"),

    html.Header([
        # Add callback
        html.A("☰", href="javascript:void(0)", className="w3-button w3-red w3-margin-right", id="threeButtons"),
        html.Span("Company Name")
    ], className="w3-container w3-top w3-hide-large w3-red w3-xlarge w3-padding", id="xyz"),

    html.Div(className="w3-overlay w3-hide-large", style={"cursor":"pointer"}, title="close side menu", id="myOverlay")
])

@app.callback(
    [dash.dependencies.Output('mySidebar', 'style'),
    dash.dependencies.Output('myOverlay', 'style')],
    [dash.dependencies.Input('aboutLink', 'n_clicks'),
    dash.dependencies.Input('threeButtons', 'n_clicks')]
)
def w3_edit(type, n_clicks):
    if n_clicks != 0:
        if type == 'aboutLink':
            return ({"display":"none"}, {"display":"none"})
        # elif type == 'threeButtons':
        return ({"display":"block"}, {"display":"block"})
    return ({"display":"block"}, {"display":"block"})
        



page_1_layout = html.Div([
    html.H1('Page 1'),
    dcc.Dropdown(
        id='page-1-dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
])

@app.callback(dash.dependencies.Output('page-1-content', 'children'),
              [dash.dependencies.Input('page-1-dropdown', 'value')])
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)


page_2_layout = html.Div([
    html.H1('Page 2'),
    dcc.RadioItems(
        id='page-2-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])

@app.callback(dash.dependencies.Output('page-2-content', 'children'),
              [dash.dependencies.Input('page-2-radios', 'value')])
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=True)