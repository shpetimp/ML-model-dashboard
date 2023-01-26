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
import numpy as np
from collections import OrderedDict
import time

text_font_size='1.7vh'
navbar_font_size='2vh'
header_font_size='2vh'






resolution_menu=  dcc.Dropdown(
        id='facilities_resolution_menu',
        options=[
            dict(label='Mean Agg. Quarterly', value='Mean Agg. Quarterly'), dict(label='Sum Agg. Quarterly', value='Sum Agg. Quarterly'),
            dict(label='Mean Agg. Monthly', value='Mean Agg. Monthly'), dict(label='Sum Agg. Monthly', value='Sum Agg. Monthly'),
            dict(label='Mean Agg. Daily', value='Mean Agg. Daily'), dict(label='Sum Agg. Daily', value='Sum Agg. Daily'),
            dict(label='Hourly', value='Hourly')
        ],
        value='Mean Agg. Quarterly' , style=dict(color='#0f2537',fontWeight='bold',textAlign='center',
                                   width='20vh',backgroundColor='#0f2537',border='1px solid #00bfff')
    )
#display='inline-block',border='2px solid #082255'
resolution_text=html.Div(html.H1('Resolution',
                           style=dict(fontSize=text_font_size,fontWeight='bold',color='white',marginTop='')),
                         style=dict(display='inline-block',marginLeft='',textAlign="center",width='100%'))
resolution_menu_div= html.Div([resolution_text,resolution_menu],
                          style=dict( fontSize=text_font_size,
                                      marginLeft='2vh',marginBottom='',display='inline-block'))

bar_resolution_menu=  dcc.Dropdown(
        id='bar_resolution_menu',
        options=[
            dict(label='Mean Agg. Quarterly', value='Mean Agg. Quarterly'), dict(label='Sum Agg. Quarterly', value='Sum Agg. Quarterly'),
            dict(label='Mean Agg. Monthly', value='Mean Agg. Monthly'), dict(label='Sum Agg. Monthly', value='Sum Agg. Monthly'),
            dict(label='Mean Agg. Daily', value='Mean Agg. Daily'), dict(label='Sum Agg. Daily', value='Sum Agg. Daily'),
            dict(label='Hourly', value='Hourly')
        ],
        value='Mean Agg. Quarterly' , style=dict(color='#0f2537',fontWeight='bold',textAlign='center',
                                   width='20vh',backgroundColor='#0f2537',border='1px solid #00bfff')
    )
#display='inline-block',border='2px solid #082255'
bar_resolution_text=html.Div(html.H1('Resolution',
                           style=dict(fontSize=text_font_size,fontWeight='bold',color='white',marginTop='')),
                         style=dict(display='inline-block',marginLeft='',textAlign="center",width='100%'))
bar_resolution_menu_div= html.Div([bar_resolution_text,bar_resolution_menu],
                          style=dict( fontSize=text_font_size,
                                      marginLeft='2vh',marginBottom='',display='inline-block'))


def creat_gen_layout():
    start=time.time()
    with open("PowerPrice_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    print(time.time() - start)

    pie_df_marks = object['DEU']
    countries = list(object.keys())
    pie_fig =go.Figure(go.Pie())
    pie_fig.update_layout(
        title='Percentages of Facilities power produced',
        font=dict(size=14, family='Arial', color='white'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c' ,margin=dict(l=0, r=0, t=40, b=0)

    )
    area_fig = go.Figure(go.Scatter())
    area_fig.update_layout(
        title='Power Produced by Facilities', xaxis_title='Date', yaxis_title='MWh/h',
        font=dict(size=14, family='Arial', color='white'),  plot_bgcolor='#20374c',
        paper_bgcolor='#20374c',
    )
    bar_fig=go.Figure(go.Bar())
    bar_fig.update_layout(
        title='Power Produced By Balancing Assets', xaxis_title='Date',
        yaxis_title='MWh',
        font=dict(size=14, family='Arial', color='white'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c' ,margin=dict(l=0, r=0, t=40, b=0) ,barmode='stack'

    )
    bar_fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    bar_fig.update_yaxes(showgrid=False, showline=True, zeroline=False)

    object=None


    facilities=['Biofuels', 'CHP', 'Coal', 'CH4', 'Hydro', 'Lignite', 'Nuc', 'Oil',
                       'Other/', 'Pump', 'Res', 'RoR', 'Solar', 'Wind']

    facilities_labels=['Biofuels', 'CHP', 'Coal', 'CH4', 'Hydro', 'Lignite', 'Nuc', 'Oil',
                       'Other', 'Pump', 'Res', 'RoR', 'Solar', 'Wind']


    planets=['Flexible Assets', 'Demand Shedding', 'Curtailment']

    planets_labels=['Flexible Assets', 'Demand Shedding', 'Curtailment']



    country_menu = dcc.Dropdown(className="custom-dropdown",
                                id='facilities_country_menu',

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

    pie_country_menu = dcc.Dropdown(className="custom-dropdown",
                                id='pie_country_menu',

                                options=[{'label': country, 'value': country} for country in countries]
                                ,
                                value=countries[0],
                                style=dict(color='#0f2537', fontWeight='bold', textAlign='center',
                                           width='20vh', backgroundColor='#0f2537', border='1px solid #00bfff')
                                )
    # display='inline-block',border='2px solid #082255'
    pie_country_text = html.Div(html.H1('Countries',
                                    style=dict(fontSize=text_font_size, fontWeight='bold', color='white',
                                               marginTop='')),
                            style=dict(display='inline-block', marginLeft='', textAlign="center", width='100%'))
    pie_country_menu_div = html.Div([pie_country_text, pie_country_menu],
                                style=dict(fontSize=text_font_size,
                                           marginLeft='', marginBottom='', display='inline-block'))

    bar_country_menu = dcc.Dropdown(className="custom-dropdown",
                                id='bar_country_menu',

                                options=[{'label': country, 'value': country} for country in countries]
                                ,
                                value=countries[0],
                                style=dict(color='#0f2537', fontWeight='bold', textAlign='center',
                                           width='20vh', backgroundColor='#0f2537', border='1px solid #00bfff')
                                )
    # display='inline-block',border='2px solid #082255'
    bar_country_text = html.Div(html.H1('Countries',
                                    style=dict(fontSize=text_font_size, fontWeight='bold', color='white',
                                               marginTop='')),
                            style=dict(display='inline-block', marginLeft='', textAlign="center", width='100%'))
    bar_country_menu_div = html.Div([bar_country_text, bar_country_menu],
                                style=dict(fontSize=text_font_size,
                                           marginLeft='', marginBottom='', display='inline-block'))

    try:
        pie_df_marks.set_index('Date', inplace=True)
    except:
        pass

    pie_df_marks['Year'] = (pd.DatetimeIndex(pie_df_marks.index).year).astype(str)
    pie_df_marks['Year']=pie_df_marks['Year'].astype('int32')
    years=pie_df_marks['Year'].to_list()
    years=list(OrderedDict.fromkeys(years))
    print(years)
    marks_values={year: {'label': '{}'.format(year), 'style': {'color': 'white'}} for year in years}

    pie_years_slider=html.Div([dcc.RangeSlider(min=years[0], max=years[-1], step=1, value=[years[1],years[-2]], marks=marks_values ,id='pie_slider')
                           ])



    facilities_text = html.Div(html.H1('Facilities',
                                      style=dict(fontSize=text_font_size, fontWeight='bold', color='white',
                                                 marginTop='')),
                              style=dict(display='inline-block', marginLeft='', textAlign="left", width='100%'))

    facilities_list = dbc.Checklist(
        inline=True,
        options=[{'label': facility_label, 'value': facility} for facility_label,facility in zip(facilities_labels,facilities)]
        ,
        value=['CHP','Solar' ,'Wind'], label_style=dict(fontSize='1.5vh'),
        id="facilities_list", style=dict(fontSize='2vh', marginLeft='0', color='white')
    )


    planets_list =html.Div([ dbc.Checklist(
        inline=True,
        options=[{'label': planet_label, 'value': planet} for planet_label,planet in zip(planets_labels,planets)]
        ,
        value=[planets[0],planets[1] , planets[2]], label_style=dict(fontSize='1.5vh'),
        id="planets_list", style=dict(fontSize='2vh', marginLeft='2vh', color='white')
    )],       style=dict(fontSize=text_font_size,
                                           marginLeft='', marginBottom='', display='inline-block')

    )

    pie_div = html.Div([
        dcc.Graph(id='pie_chart', config={'displayModeBar': False, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='60vh', backgroundColor='#20374c'), figure=pie_fig
                  )], id='pie_div'
    )


    area_div = html.Div([
        dcc.Graph(id='gen_area_chart', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='40vh', backgroundColor='#20374c'), figure=area_fig
                  )], id='gen_area_div'
    )

    bar_div = html.Div([
        dcc.Graph(id='gen_bar_chart', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='40vh', backgroundColor='#20374c'), figure=bar_fig
                  )], id='gen_bar_div'
    )

    layout=  [dbc.Col([dbc.Card(dbc.CardBody(
        [html.Div([dbc.Spinner([area_div], size="lg", color="primary", type="border", fullscreen=False)
                      , html.Div([country_menu_div, resolution_menu_div],
                                                    style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                                           'justify-content': 'center'}),
                   html.Br(), facilities_list,
                #   dcc.Store(id='flow_data', data=pd.DataFrame().to_dict('records'))

                   ], style=dict(height='55vh'))])
        , style=dict(backgroundColor='#20374c')), html.Br()

        ,dbc.Card(dbc.CardBody(
            [html.Div([dbc.Spinner([bar_div], size="lg", color="primary", type="border", fullscreen=False),html.Br()
                                  , html.Div([bar_country_menu_div,bar_resolution_menu_div,planets_list],
                                     style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                            'justify-content': 'center'}), html.Br(),




                       ], style=dict(height='55vh'))])
            , style=dict(backgroundColor='#20374c')) , html.Br()



    ],



        xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
        md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)),

        dbc.Col([dbc.Card(dbc.CardBody(
            [html.Div([dbc.Spinner([pie_div], size="lg", color="primary", type="border", fullscreen=False),
                       html.Br(),    pie_years_slider , html.Br() ,

                       html.Div([pie_country_menu_div],
                                style={'width': '100%', 'display': 'flex', 'align-items': 'center',
                                       'justify-content': 'center'}),

                       ], style=dict(height=''))])

            , style=dict(backgroundColor='#20374c', height='')), html.Br()],

            xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
            md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1),
        ),






    ]

    return layout


