#! /usr/local/bin/python3

import plotly.graph_objects as go # or plotly.express as px
# fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)
# fig.add_trace( ... )
# fig.update_layout( ... )

from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html

import os
import pickle
# os.chdir('web')

def createFigNew(COUNTY):
    os.chdir('data')
    data = []
    with open (COUNTY, 'rb') as fp:
        itemlist = pickle.load(fp)
    os.chdir('..')
    
    fig = go.Figure()

    #Create/Style Traces
    # fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[0][2]+itemlist[0][1][::-1], fill='toself', line_color='pink', showlegend=False, name="uncertainty"))
    
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[0][1], name="Maximum", line=dict(color="pink", width=4, dash="dash")))
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[0][2], name="Minimum", line=dict(color="pink", width=4, dash="dash"), fill="tonexty"))
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[0][0], name="Average", line=dict(color="firebrick", width=4)))
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[3], name="ActualMovingAvg", line=dict(color="yellow", width=4)))
    
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[4], name="Actual", line=dict(color="royalblue", width=4)))
    # fig.add_trace(go.Scatter(x=itemlist[2], y=newCases[3], name="Medians", line=dict(color="goldenrod", width=4)))

    # Edit the layout
    fig.update_layout(title='New Cases by Day (adj) '+ "(R0 = " + str(itemlist[6]) + ")", xaxis_title='Day', yaxis_title='New Cases')

    # fig.add_trace(go.Scatter(x=itemlist[2], y=totalCases[2]+itemlist[1][1][::-1], fill='toself', line_color='pink', showlegend=False, name="uncertainty"))
    # fig.add_trace(go.Scatter(x=itemlist[2], y=totalCases[0], name="Average", line=dict(color="firebrick", width=4)))
    
    return fig

def createFigTotal(COUNTY):
    os.chdir('data')
    data = []
    with open (COUNTY, 'rb') as fp:
        itemlist = pickle.load(fp)
    os.chdir('..')
    
    fig = go.Figure()
    #Create/Style Traces
    # fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[0][2]+itemlist[0][1][::-1], fill='toself', line_color='pink', showlegend=False, name="uncertainty"))
    # fig.add_trace(go.Scatter(x=itemlist[2], y=newCases[3], name="Medians", line=dict(color="goldenrod", width=4)))

    # Edit the layout
    fig.update_layout(title='Total Cases by Day (adj) (R0 = ' + str(itemlist[6]) + ")", xaxis_title='Day', yaxis_title='Total Cases')

    # fig.add_trace(go.Scatter(x=itemlist[2], y=totalCases[2]+itemlist[1][1][::-1], fill='toself', line_color='pink', showlegend=False, name="uncertainty"))
    # fig.add_trace(go.Scatter(x=itemlist[2], y=totalCases[0], name="Average", line=dict(color="firebrick", width=4)))
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[1][1], name="Maximum", line=dict(color="pink", width=4, dash="dash"), fill ="none"))
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[1][2], name="Minimum", line=dict(color="pink", width=4, dash="dash"), fill="none"))
    fig.add_trace(go.Scatter(x=itemlist[2], y=itemlist[1][0], name="Average", line=dict(color="firebrick", width=4)))    
    return fig

# print(createFig("SantaClara"))


messages = [
    '''
    Because county data is extremely variable due to the lack of testing and reporting intervals, 
    a five day moving average (yellow) is utilized to run these calculations in an attempt to smooth the data. 
    Furthermore, case counts are used opposed to deaths because county wise death counts are relatively small compared 
    to the population. 
    
    These calculations first calculate the average R0 value over the last 10 days of data. 
    Then, the resulting R0 estimate is used to predict future outcomes. Due to the small data sets, a large uncertainty
    interval is predicted (pink) in addition to the predicted value (red).

    Currently, the calculations are cut off after 100 days past the first case, so a sudden drop toward the end of graph
    does not necessarily indicate a reduction in case counts.
    '''
]


county = "SantaClara"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("COVID-19 Projections by County for California", style={'text-align': 'center'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
            options=[
                {'label': 'Santa Clara', 'value': 'SantaClara'},
                {'label': 'San Mateo', 'value': 'SanMateo'},
                {'label': 'San Francisco', 'value': 'SanFrancisco'},
                {'label': 'Los Angeles', 'value': 'LosAngeles'}
            ],
            value='SantaClara',
            id="countyDropdown",
            style={'width': '50vw'}),
        ]),
        
        html.Div([
            dcc.Dropdown(
            options=[
                {'label': 'New Cases', 'value': 'new'},
                {'label': 'Total Cases', 'value': 'total'}
            ],
            value='new',
            id="caseTypeDropdown",
            style={'width': '50vw'}),
        ]),
    ],style={'display':'flex', 'justify-content':'space-between'}),

    html.Div([
        dcc.Graph(id="graph", style={'width':'47vw'}),
        html.Div([
            html.H2("Information about the data", style={'text-align': 'center'}),
            dcc.Markdown(messages[0])
        ],
        style={'width':'47vw'})
    ],
    style={"display": "flex", "justify-content": "space-around", 'height':'75vh'})
    
])

@app.callback(
    dash.dependencies.Output("graph", "figure"),
    [dash.dependencies.Input("countyDropdown", "value"),
    dash.dependencies.Input("caseTypeDropdown", "value")]
)
def updateCounty(value, caseType):
    if caseType == "new":
        return createFigNew(value)
    elif caseType == "total":
        return createFigTotal(value)


app.run_server(debug=True) 
