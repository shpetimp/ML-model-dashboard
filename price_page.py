import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State,MATCH,ALL
import pandas as pd
import pickle as pkl
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
import json
from flask import Flask
import math
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
from collections import OrderedDict



#################################################

# SAME AS FLOW PAGE LAYOUT WITH DIFFERENCE ONLY IN NAMES AND VALUES

################################################



line_fig=go.Figure()
text_font_size='1.7vh'
navbar_font_size='2vh'
header_font_size='2vh'




line_div=html.Div([
            dcc.Graph(id='price_line_chart', config={'displayModeBar': True, 'scrollZoom': True,'displaylogo': False},
                style=dict(height='45vh',backgroundColor='#20374c') ,figure=line_fig
            ) ] ,id='price_line_div'
        )



resolution_menu=  dcc.Dropdown(
        id='price_resolution_menu',
        options=[
            dict(label='Mean Agg. Quarterly', value='Mean Agg. Quarterly'), dict(label='Sum Agg. Quarterly', value='Sum Agg. Quarterly'),
            dict(label='Mean Agg. Monthly', value='Mean Agg. Monthly'), dict(label='Sum Agg. Monthly', value='Sum Agg. Monthly'),
            dict(label='Mean Agg. Daily', value='Mean Agg. Daily'), dict(label='Sum Agg. Daily', value='Sum Agg. Daily'),
            dict(label='Hourly', value='Hourly')
        ],
        value='Mean Agg. Quarterly' , style=dict(color='#0f2537',fontWeight='bold',textAlign='center',
                                   width='20vh',backgroundColor='#0f2537',border='1px solid #00bfff')
    )

resolution_text=html.Div(html.H1('Resolution',
                           style=dict(fontSize=text_font_size,fontWeight='bold',color='white',marginTop='')),
                         style=dict(display='inline-block',marginLeft='',textAlign="center",width='100%'))
resolution_menu_div= html.Div([resolution_text,resolution_menu],
                          style=dict( fontSize=text_font_size,
                                      marginLeft='2vh',marginBottom='',display='inline-block'))


download_csv=html.Div([dbc.Button("Download CSV", color="primary", size='lg', n_clicks=0,id="price_download_csv"
                            ,style=dict(fontSize='1.6vh')
                            )],style=dict(display='inline-block',marginLeft='2vh',marginTop='3%'))

csv_download_data=html.Div([Download(id="price_csv_download_data")])


def creat_price_layout():
    with open("PowerPrice_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    countries = list(object.keys())
    df_marks = object['DEU']
    object=None
    scenarios = ['Normal','1991', '1992', '1993', '1994', '1995', '1996', '1997',
                 '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                 '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                 '2012', '2013', '2014', '2015','Exp']

    country_menu = dcc.Dropdown(className="custom-dropdown",
                                id='price_country_menu',

                                options=[{'label': country, 'value': country} for country in countries]
                                ,
                                value=countries[0],
                                style=dict(color='#0f2537', fontWeight='bold', textAlign='center',
                                           width='20vh', backgroundColor='#0f2537', border='1px solid #00bfff')
                                )
    # display='inline-block',border='2px solid #082255'
    country_text = html.Div(html.H1('Countries',
                                    style=dict(fontSize=text_font_size, fontWeight='bold', color='white',
                                               marginTop='')),
                            style=dict(display='inline-block', marginLeft='', textAlign="center", width='100%'))
    country_menu_div = html.Div([country_text, country_menu],
                                style=dict(fontSize=text_font_size,
                                           marginLeft='', marginBottom='', display='inline-block'))

    scenarios_text = html.Div(html.H1('Scenarios',
                                      style=dict(fontSize=text_font_size, fontWeight='bold', color='white',
                                                 marginTop='')),
                              style=dict(display='inline-block', marginLeft='', textAlign="left", width='100%'))

    scenarios_list = dbc.Checklist(
        inline=True,
        options=[{'label': scenario, 'value': scenario} for scenario in scenarios]
        ,
        value=[scenarios[0]], label_style=dict(fontSize='1.5vh'),
        id="price_scenarios_list", style=dict(fontSize='2vh', marginLeft='0', color='white')
    )

    bar_fig=go.Figure(go.Bar())

    bar_div = html.Div([
        dcc.Graph(id='price_bar_chart', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='60vh', backgroundColor='#20374c'), figure=bar_fig
                  )], id='price_bar_div'
    )


    df_marks['Year'] = (pd.DatetimeIndex(df_marks.iloc[:, 26]).year).astype(str)
    df_marks['Year']=df_marks['Year'].astype('int32')
    years=df_marks['Year'].to_list()
    years=list(OrderedDict.fromkeys(years))
    print(years)
    marks_values={year: {'label': '{}'.format(year), 'style': {'color': 'white'}} for year in years}
    #{year: '{}'.format(year) for year in years}
    years_slider=html.Div([dcc.RangeSlider(min=years[0], max=years[-1], step=1, value=[years[1],years[-2]], marks=marks_values ,id='price_bar_slider')
                           ])


    layout = [dbc.Col([dbc.Card(dbc.CardBody(
        [html.Div([dbc.Spinner([line_div], size="lg", color="primary", type="border", fullscreen=False),
                   html.Br(), html.Div([country_menu_div, resolution_menu_div, download_csv],
                                                    style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                                           'justify-content': 'center'}),
                   html.Br(), scenarios_text, scenarios_list, csv_download_data,
                   dcc.Store(id='price_data', data=pd.DataFrame().to_dict('records'))

                   ], style=dict(height='75vh'))])
        , style=dict(backgroundColor='#20374c')), html.Br()
    ], xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
        md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)),

        dbc.Col([dbc.Card(
            dbc.CardBody(
                [html.Div(
                    [dbc.Spinner([bar_div], size="lg", color="primary", type="border", fullscreen=False), html.Br(),
                     years_slider

                     ], style=dict(height='75vh'))])



                          , style=dict(backgroundColor='#20374c')), html.Br()],

                xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
                md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)

                )

    ]
    return layout


def create_price_bar_fig(object,range_slider):
    countries = list(object.keys())
    normal_scenario_mean = []
    countries_list = []
    normal_df = pd.DataFrame()
    for country in countries:
        df = object[country]


        df=df[(df['Date'].dt.year>=range_slider[0]) & (df['Date'].dt.year<=range_slider[1])]
        df.set_index('Date', inplace=True)
        df.columns = ['1991', '1992', '1993', '1994', '1995', '1996', '1997',
                      '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                      '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                      '2012', '2013', '2014', '2015', 'Normal']
        mean_power = df['Normal'].mean()
        normal_scenario_mean.append(mean_power)
        countries_list.append(country)

    object = None
    normal_df['countries'] = countries_list
    normal_df['normal_scenario_mean'] = normal_scenario_mean
    normal_df.sort_values(by='normal_scenario_mean', inplace=True, ascending=False)
    normal_df = normal_df.nlargest(5, 'normal_scenario_mean')
    # print(normal_df)
    normal_df['normal_scenario_mean'] = normal_df['normal_scenario_mean'].astype('int64')
    bar_fig = go.Figure(data=[
        go.Bar(name='mean power', x=normal_df['normal_scenario_mean'], y=normal_df['countries'].to_list(),
               marker_color='#00bfff', text=normal_df['normal_scenario_mean'].to_list(),
               textposition='outside', textfont=dict(
                size=15,
                color="white"
            ), orientation='h')
    ])

    bar_fig.update_layout(
        title='Top 5 countries of Avg power price ( normal scenario )', xaxis_title='€/MWh',
        yaxis_title='Countries',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c'

    )
    # ,categoryorder='category descending'
    bar_fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    bar_fig.update_yaxes(showgrid=False, showline=True, zeroline=False, autorange="reversed")

    return bar_fig
