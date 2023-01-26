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
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import numpy as np
import ssl
import certifi
import geopy.geocoders
from collections import OrderedDict
from capacity_page import ctx , countries_dict , countries_coordinates , findGeocode ,get_lon_lat, add_coordinates

geopy.geocoders.options.default_ssl_context = ctx

def add_coord_origins(df,countries_coordinates):
    origin_lon=[]
    origin_lat=[]

    origin_names=df['origin'].to_list()

    for origin  in origin_names:
        origin_lon.append( countries_coordinates[origin][1] )
        origin_lat.append( countries_coordinates[origin][0] )


    df['origin_lon']=origin_lon
    df['origin_lat']=origin_lat


    return df

def add_lons_lats_origins(df):
    origin_lon=[]
    origin_lat=[]

    origin_names=df['origin'].to_list()


    for origin in origin_names:

        if findGeocode(countries_dict[origin]) != None:

            origin_loc = findGeocode(countries_dict[origin])

            # coordinates returned from
            # function is stored into
            # two separate list
            origin_lat.append(origin_loc.latitude)
            origin_lon.append(origin_loc.longitude)

        # if coordinate for a city not
        # found, insert "NaN" indicating
        # missing value
        else:
            origin_lat.append(np.nan)
            origin_lon.append(np.nan)



    df['origin_lon']=origin_lon
    df['origin_lat']=origin_lat


    return df





map_fig=go.Figure(go.Scattermapbox())
text_font_size='1.7vh'
navbar_font_size='2vh'
header_font_size='2vh'

def create_net_import_layout():
    with open("Flow_20220208.pickle", "rb") as f:
        object = pkl.load(f)
        countries = list(object.keys())

    map_fig=go.Figure(go.Scattermapbox())
    map_fig.update_layout(mapbox_style='open-street-map')
    map_div = html.Div([
        dcc.Graph(id='net_import_map', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='55vh', backgroundColor='#20374c'), figure=map_fig
                  )], id='net_imp_map_div'
    )

    df_marks = object['DEU_FRA']
    df_marks['Year'] = (pd.DatetimeIndex(df_marks.iloc[:, 26]).year).astype(str)

    df_marks['Quarter_number'] = df_marks.iloc[:, 26].dt.quarter
    df_marks['Quarter_number']=df_marks['Quarter_number'].astype(str)
   # df_marks['y_q']=(+df_marks['Year']+df_marks['Quarter_number']).astype('int64')
 #   y_q=df_marks['y_q'].to_list()
   # y_q=list(OrderedDict.fromkeys(y_q))
    df_marks['Year']=df_marks['Year'].astype('int32')
  #  years=df_marks['Year'].to_list()
   # years=list(OrderedDict.fromkeys(years))
    years=list(np.arange(df_marks['Year'].min(),(df_marks['Year'].max())+1,0.25))

    df_marks['Quarter_number']=df_marks['Quarter_number'].astype('int32')
    df_marks['marks']=df_marks['Year'] + (   (df_marks['Quarter_number']/4 )-0.25  )
    print(df_marks['marks'].unique())

    marks={
        2021.25:  {'label': '21Q2', 'style': {'color': 'white'}} ,2022: {'label': '22Q1', 'style': {'color': 'white'}},
        2023: {'label': '23Q1', 'style': {'color': 'white'}},2024: {'label': '24Q1', 'style': {'color': 'white'}},
        2025: {'label': '25Q1', 'style': {'color': 'white'}},2026: {'label': '26Q1', 'style': {'color': 'white'}},
        2027: {'label': '27Q1', 'style': {'color': 'white'}},2028: {'label': '28Q1', 'style': {'color': 'white'}},
        2029: {'label': '29Q1', 'style': {'color': 'white'}},2030: {'label': '30Q1', 'style': {'color': 'white'}},
        2031: {'label': '31Q1', 'style': {'color': 'white'}},2032: {'label': '32Q1', 'style': {'color': 'white'}},
        2033: {'label': '33Q1', 'style': {'color': 'white'}},2034: {'label': '34Q1', 'style': {'color': 'white'}},
        2035: {'label': '35Q1', 'style': {'color': 'white'}},2036: {'label': '36Q1', 'style': {'color': 'white'}},
        2037: {'label': '37Q1', 'style': {'color': 'white'}}, 2038: {'label': '38Q1', 'style': {'color': 'white'}},
        2039: {'label': '39Q1', 'style': {'color': 'white'}},


    }
    #{year: '{}'.format(year) for year in years}
    years_slider=html.Div([dcc.RangeSlider(min=df_marks['marks'].min(), max=df_marks['marks'].max(), step=0.25,
                                           value=[2022.0,2023.0], marks=marks ,id='net_imp_map_slider')
                           ])

    refresh_map = html.Div([dbc.Button("Refresh Map", color="primary", size='lg', n_clicks=0, id="refresh_net_import_map",outline=True
                                          , style=dict(fontSize=text_font_size)
                                          )],style={'width': '100%','display': 'flex','align-items': 'center','justify-content': 'center'})

    layout = [dbc.Col([dbc.Card(dbc.CardBody([dbc.Spinner([map_div],size="lg", color="primary", type="border", fullscreen=False )
                                                 ,html.Br(),years_slider,html.Br(),refresh_map])
                          , style=dict(backgroundColor='#20374c')), html.Br()],

                xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
                md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)

                ) ]
    return layout

def create_net_import_map(object,years_range):
    quarters_dic={'0':'1','25':'2','5':'3','75':'4'}
    min_range =float(years_range[0])
    max_range= float(years_range[1])
    min_year=str(min_range).split('.')[0]
    min_quarter=str(min_range).split('.')[1]
    min_quarter=quarters_dic[min_quarter]
    max_year=str(max_range).split('.')[0]
    max_quarter=str(max_range).split('.')[1]
    max_quarter=quarters_dic[max_quarter]
    min_year_quarter=int(min_year+min_quarter)
    max_year_quarter=int(max_year+max_quarter)

    countries = list(object.keys())
    #print(countries)
    countries_names = []
    origins = []
    dists = []
    sum_import_power = []
    map_df = pd.DataFrame()
    for country in countries:
        df = object[country]
        df['Year'] = (pd.DatetimeIndex(df.iloc[:, 26]).year).astype(str)
        df['Quarter_number'] = df.iloc[:, 26].dt.quarter
        df['Quarter_number'] = df['Quarter_number'].astype(str)
        df['y_q']=(df['Year']+df['Quarter_number']).astype('int64')

        df=df[  (df['y_q']>=min_year_quarter) & (df['y_q']<=max_year_quarter)  ]
        countries_names.append(country)
        o=country.split('_')[0]
        d=country.split('_')[1]
        origins.append(o)
        dists.append(d)
        dis_df=object['{}_{}'.format(d,o)]
        dis_df['Year'] = (pd.DatetimeIndex(dis_df.iloc[:, 26]).year).astype(str)
        dis_df['Quarter_number'] = dis_df.iloc[:, 26].dt.quarter
        dis_df['Quarter_number'] = dis_df['Quarter_number'].astype(str)
        dis_df['y_q']=(dis_df['Year']+dis_df['Quarter_number']).astype('int64')

        dis_df=dis_df[  (dis_df['y_q']>=min_year_quarter) & (dis_df['y_q']<=max_year_quarter)  ]
        net_sum=df.iloc[:, 25].sum() - dis_df.iloc[:, 25].sum()
        sum_import_power.append(net_sum)

    map_df['countries'] = countries_names
    map_df['origin'] = origins
    map_df['distination'] = dists
    map_df['sum_net_import'] = sum_import_power

    map_df =add_coordinates(map_df,countries_coordinates)

    map_fig = go.Figure()

    colors_list = px.colors.qualitative.Light24
    colors_list[0]='lightsalmon'
    colors_list.extend(['#d5f4e6','#80ced6','#c83349'])
    colors_dict = {}

    i=0
    for country in list(map_df['origin'].unique()):
        colors_dict[country] = colors_list[i]
        i+=1

    name_arr = []
    for i in range(len(map_df)):
        net_imp = map_df['sum_net_import'][i]
        o=map_df['origin'][i]
        d=map_df['distination'][i]

        lons = [map_df['origin_lon'][i], map_df['dist_lon'][i]]
        lats = [map_df['origin_lat'][i], map_df['dist_lat'][i]]

        color = colors_dict[o]

        if net_imp > 0:
            color=colors_dict[o]

        elif net_imp == 0:
            dist_lon=(map_df['origin_lon'][i] + map_df['dist_lon'][i] ) / 2
            dist_lat=(map_df['origin_lat'][i] + map_df['dist_lat'][i] ) /2
            lons=[map_df['origin_lon'][i], dist_lon]
            lats=[map_df['origin_lat'][i], dist_lat]
            color=colors_dict[o]

        else:
            color=colors_dict[d]

        legend=True
        name=o
        if name in name_arr:
            legend = False
        else:
            legend = True

        name_arr.append(name)

        map_fig.add_trace(go.Scattermapbox(showlegend=False,name=name,
                                           lon=lons,
                                           lat=lats,
                                           mode='lines',
                                           marker={'color': 'white', 'size': 4, 'allowoverlap': True, 'opacity': 0},
                                           line=dict(width=4, color=color), hoverinfo='skip'
                                           # unselected={'marker': {'opacity': 1}},
                                           # selected={'marker': {'opacity': 0.5, 'size': 15}},

                                           )
                          )

    nodes_df = map_df.groupby(['origin', 'origin_lon', 'origin_lat'])['sum_net_import'].mean().reset_index()
    # print(nodes_df)

    hov_text = []
    for ind in nodes_df.index:
        hover_df = map_df[map_df['countries'].str.contains('{}'.format(nodes_df['origin'][ind] + '_'))]
        hover_strings = ['Country Name : {}'.format(nodes_df['origin'][ind])]
        for i, row in hover_df.iterrows():
            hov_string = '{} : {}'.format(row['countries'], row['sum_net_import'])
            hover_strings.append(hov_string)

        final_string = '<br>'.join(hover_strings)
        hov_text.append(final_string)

    nodes_df['hover'] = hov_text

    map_fig.add_trace(go.Scattermapbox(lat=nodes_df['origin_lat'], lon=nodes_df['origin_lon'],showlegend=False,
                                       marker=dict(
                                           size=15,
                                           color=list(map(lambda x: colors_dict[x], nodes_df['origin'].to_list())),
                                           sizemode='area', opacity=1
                                       ),
                                       hoverinfo='text', hovertemplate=nodes_df['hover'], customdata=nodes_df['hover']))

    map_fig.update_layout(mapbox_style='open-street-map', mapbox_center_lon=9, mapbox_center_lat=53,
                          mapbox_zoom=3)
    map_fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0}, hoverdistance=2, uirevision='foo',
                          clickmode='event+select', hovermode='closest')

    map_fig.update_layout(title_text='Net Import MW',
                          title_x=0.5,
                          #  width=1200,  height=700,
                          font=dict(size=12, family='bold', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
                          paper_bgcolor='#20374c'  # ,

                          , margin=dict(l=0, r=0, t=40, b=0)

                          )

    # map_fig.show()

    return map_fig
