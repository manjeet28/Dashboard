import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly
import flask
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly import tools
import pandas as pd
import numpy as np
import random
import plotly.graph_objs as go
from collections import deque

athlete_events_df = pd.read_csv('athlete_events.csv')
noc_regions_df = pd.read_csv('noc_regions.csv')

merged = pd.merge(athlete_events_df, noc_regions_df, on='NOC', how='left')

def missing_data(data):
    total = data.isnull().sum().sort_values(ascending = False)
    percent = (data.isnull().sum()/data.isnull().count()*100).sort_values(ascending = False)
    return pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
missing_data(athlete_events_df)

def generate_table(dataframe, max_rows=3):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


    
tmp = athlete_events_df.groupby(['Year', 'City'])['Season'].value_counts()
df = pd.DataFrame(data={'Athlets': tmp.values}, index=tmp.index).reset_index()

olympics_df = athlete_events_df.merge(noc_regions_df)

olympics_df=olympics_df.rename(columns = {'region':'Country'})

tmp1 = olympics_df.groupby(['Country'])['Year'].nunique()
df1 = pd.DataFrame(data={'Editions': tmp1.values}, index=tmp1.index).reset_index()
df1.head(2)

tmp2 = olympics_df.groupby(['Country', 'Medal'])['ID'].agg('count').dropna()
df3 = pd.DataFrame(tmp2).reset_index()

dfG = df3[df3['Medal']=='Gold']
dfS = df3[df3['Medal']=='Silver']
dfB = df3[df3['Medal']=='Bronze']

tmp = athlete_events_df.groupby(['Season'])['Sport'].value_counts()
df5 = pd.DataFrame(data={'Athlets': tmp.values}, index=tmp.index).reset_index()
df_S = df5[df5['Season']=='Summer']

trace = go.Choropleth(
                locations = df3['Country'],
                locationmode='country names',
                z = df3['ID'],
                text = ['Country'],
                autocolorscale =False,
                reversescale = True,
                colorscale = 'rainbow',
                marker = dict(
                    line = dict(
                        color = 'rgb(0,0,0)',
                        width = 0.5)
                ),
                colorbar = dict(
                    tickprefix = '')
            )

app = dash.Dash()

dfS = df[df['Season']=='Summer']; dfW = df[df['Season']=='Winter']

traceS = go.Scatter(
    x = dfS['Year'],y = dfS['Athlets'],
    name="Summer Games",
    marker=dict(color="Red"),
    mode = "markers+lines"
)
traceW = go.Scatter(
    x = dfW['Year'],y = dfW['Athlets'],
    name="Winter Games",
    marker=dict(color="Blue"),
    mode = "markers+lines"
)

tmp = olympics_df.groupby(['Sport', 'Medal'])['ID'].agg('count').dropna()
df4 = pd.DataFrame(tmp).reset_index()
dfG1 = df4[df4['Medal']=='Gold']
dfS1 = df4[df4['Medal']=='Silver']
dfB1 = df4[df4['Medal']=='Bronze']

traceGold = go.Bar(
    x = dfG1['Sport'],y = dfG1['ID'],
    name="Gold",
     marker=dict(
                color='gold',
                line=dict(
                    color='black',
                    width=1),
                opacity=0.5,
            ),
    text = dfG1['Sport'],
    #orientation = 'h'
)
traceSilver = go.Bar(
    x = dfS1['Sport'],y = dfS1['ID'],
    name="Silver",
    marker=dict(
                color='Grey',
                line=dict(
                    color='black',
                    width=1),
                opacity=0.5,
            ),
    text=dfS1['Sport'],
    #orientation = 'h'
)

traceBronze = go.Bar(
    x = dfB1['Sport'],y = dfB1['ID'],
    name="Bronze",
    marker=dict(
                color='Brown',
                line=dict(
                    color='black',
                    width=1),
                opacity=0.5,
            ),
    text=dfB1['Sport'],
   # orientation = 'h'
)

female_h = olympics_df[olympics_df['Sex']=='F']['Height'].dropna()
male_h = olympics_df[olympics_df['Sex']=='M']['Height'].dropna()

colors = ['gold', 'brown', 'lightblue']

traceP = go.Pie(labels=df_S['Sport'], 
               values=df_S['Athlets'],
               hoverinfo='label+value+percent', 
               textinfo='value+percent', 
               textfont=dict(size=8),
               rotation=180,
               marker=dict(colors=colors, 

                           line=dict(color='#000000', width=1)
                        )
            )

external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(html.Div(children=[
        html.Div([
    html.H1(children='Interactive Dashboard for 120 Years of Olympic History'),
    html.H2(children='A dashboard created by Manjeet Singh (16BCE2000)'),
    html.H4(children='Sample Data:'),generate_table(merged),
    html.Img(src="http://www.vit.ac.in/images/logo1.png",className='three columns',style={ 'height' : '8%', 'width' : '8%','float' : 'right','relative' : 'fixed','margin-right' : '20','margin-top' : '-400'})
    
    ],className='row'),
    html.Div(children='''
         
    '''),html.Div([
    dcc.Graph(
        id='choropleth1',figure={
                'data' : [go.Choropleth(
            locations = df1['Country'],
            locationmode='country names',
            z = df1['Editions'],
            text = df1['Country'],
            autocolorscale =False,
            reversescale = True,
            colorscale = 'rainbow',
            marker = dict(
                line = dict(
                    color = 'rgb(0,0,0)',
                    width = 0.5)
            ),
            colorbar = dict(
                title = 'Editions',
                tickprefix = '')
        )], 'layout' : go.Layout(
    title = 'Olympic countries',
    geo = dict(
        showframe = True,
        showlakes = False,
        showcoastlines = True,
        projection = dict(
            type = 'natural earth'
        )
    )
)
        },className='six columns'
    )
    ]),
html.Div([
    dcc.Graph(
        id='Scatter1',figure={
               'data': [ go.Scatter(
    x = df['Year'],
    y = df['Athlets'],
    name="Athlets per Olympic game",
    marker=dict(
        color="Blue",
    ),
    mode = "markers"
)],
'layout': go.Layout(dict(title = 'Athlets per Olympic game'),
          
          xaxis = dict(title = 'Year', showticklabels=True), 
          yaxis = dict(title = 'Number of athlets'),
          hovermode = 'closest'
         )
           
        },className='six columns'
    )
    ]),
    html.Div([
            dcc.Graph(
        id='line-1',figure={
               'data': [traceS, traceW],
'layout': go.Layout(
          dict(title = 'Athlets per Olympic game',
          xaxis = dict(title = 'Year', showticklabels=True), 
          yaxis = dict(title = 'Number of athlets'),
          hovermode = 'closest'
         )
          )
           
        },className='six columns'
    )
            
            ]),
     html.Div([
            dcc.Graph(
        id='choropleth-2',figure={
               'data': [trace],
'layout': go.Layout(
          title = 'No. of Medals',
        geo = dict(
            showframe = True,
            showlakes = False,
            showcoastlines = True,
            projection = dict(
                type = 'natural earth'
         )
          )
           )
        },className='six columns'
    )
            
            ]),
     html.Div([
            dcc.Graph(
        id='bar-1',figure={
               'data': [traceGold, traceSilver, traceBronze],
'layout': go.Layout(
          dict(title = 'Medals per sport',
          xaxis = dict(title = 'Sport', showticklabels=True, tickangle=45,
            tickfont=dict(
                size=8,
                color='black'),), 
          yaxis = dict(title = 'Number of medals'),
          hovermode = 'closest',
          barmode='stack',
          showlegend=False,
          width=900,
          height=600
          )
           )
        },className='six columns'
    )
            
            ]),
    html.Div([
            dcc.Graph(
        id='distr-1',figure={
               'data': [traceP],
'layout': go.Layout(
          dict(title = "Number of athlets per sport (Summer Olympics)",
                  width=800,
                  height=1200,
              legend=dict(orientation="h")
           )
          )
        },className='six columns'
    )
            
            ])
   ])
  )
if __name__ == '__main__':
    app.run_server(debug=True)