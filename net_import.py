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
from capacity_page import ctx , countries_dict  , findGeocode ,get_lon_lat, add_coordinates

geopy.geocoders.options.default_ssl_context = ctx

# same function as add_coordinates in capacity page but used when no destination in dataframe ( only origin )
def add_coord_origins(df):
    origin_lon=[]
    origin_lat=[]

    origin_names=df['origin'].to_list()
    df_coord = pd.read_csv('countries_coordinates.csv')
    countries_coordinates = df_coord.to_dict('list')

    for origin  in origin_names:
        origin_lon.append( countries_coordinates[origin][1] )
        origin_lat.append( countries_coordinates[origin][0] )


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
    df_marks = object['DEU_FRA']
    with open("NetImport_20220208.pickle", "rb") as f2:
        object2 = pkl.load(f2)

    countries2 = list(object.keys())
    df_marks2 = object2['DEU']
    object=None
    object2=None
    map_fig=go.Figure(go.Scattermapbox())
    map_fig.update_layout(mapbox_style='open-street-map')
    map_div = html.Div([
        dcc.Graph(id='net_flow_map', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='60vh', backgroundColor='#20374c'), figure=map_fig
                  )], id='net_flow_map_div'
    )


    df_marks['Year'] = (pd.DatetimeIndex(df_marks.iloc[:, 26]).year).astype(str)
    df_marks['Year']=df_marks['Year'].astype('int32')
    years=df_marks['Year'].to_list()
    years=list(OrderedDict.fromkeys(years))
    #print(years)
    marks_values={year: {'label': '{}'.format(year), 'style': {'color': 'white'}} for year in years}
    #{year: '{}'.format(year) for year in years}
    years_slider=html.Div([dcc.RangeSlider(min=years[0], max=years[-1], step=1, value=[years[1],years[-2]], marks=marks_values ,id='net_flow_map_slider')
                           ])


    refresh_map = html.Div([dbc.Button("Refresh Map", color="primary", size='lg', n_clicks=0, id="refresh_net_flow_map",outline=True
                                          , style=dict(fontSize=text_font_size)
                                          )],style={'width': '100%','display': 'flex','align-items': 'center','justify-content': 'center'})


    map_fig2=go.Figure(go.Scattermapbox())
    map_fig2.update_layout(mapbox_style='open-street-map')
    map_div2 = html.Div([
        dcc.Graph(id='net_imp_map', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='60vh', backgroundColor='#20374c'), figure=map_fig2
                  )], id='net_imp_map_div'
    )


    df_marks2['Year'] = (pd.DatetimeIndex(df_marks2.iloc[:, 26]).year).astype(str)
    df_marks2['Year']=df_marks2['Year'].astype('int32')
    years2=df_marks2['Year'].to_list()
    years2=list(OrderedDict.fromkeys(years2))
    #print(years)
    marks_values2={year: {'label': '{}'.format(year), 'style': {'color': 'white'}} for year in years2}
    #{year: '{}'.format(year) for year in years}
    years_slider2=html.Div([dcc.RangeSlider(min=years2[0], max=years2[-1], step=1, value=[years2[1],years2[-2]], marks=marks_values2 ,id='net_imp_map_slider')
                           ])


    refresh_map2 = html.Div([dbc.Button("Refresh Map", color="primary", size='lg', n_clicks=0, id="refresh_net_imp_map",outline=True
                                          , style=dict(fontSize=text_font_size)
                                          )],style={'width': '100%','display': 'flex','align-items': 'center','justify-content': 'center'})




    layout = [dbc.Col([dbc.Card(dbc.CardBody([dbc.Spinner([map_div],size="lg", color="primary", type="border", fullscreen=False )
                                                 ,html.Br(),years_slider,html.Br()])
                          , style=dict(backgroundColor='#20374c')), html.Br()],

                xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
                md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)

                ) ,

              dbc.Col([dbc.Card(
                  dbc.CardBody([dbc.Spinner([map_div2], size="lg", color="primary", type="border", fullscreen=False)
                                   , html.Br(), years_slider2, html.Br()])
                  , style=dict(backgroundColor='#20374c')), html.Br()],

                      xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
                      md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)

                      )





              ]
    return layout

# i only commented on the parts different from capacity map
def create_net_flow_map(object,years_range):


    countries = list(object.keys())
    #print(countries)
    countries_names = []
    origins = []
    dists = []
    sum_flow_power = []
    map_df = pd.DataFrame()
    for country in countries:
        df = object[country]
        countries_names.append(country)
        o=country.split('_')[0]
        d=country.split('_')[1]
        origins.append(o)
        dists.append(d)
        dis_df=object['{}_{}'.format(d,o)]


        df=df[(df['Date'].dt.year>=years_range[0]) & (df['Date'].dt.year<=years_range[1])]


        dis_df=dis_df[(dis_df['Date'].dt.year>=years_range[0]) & (dis_df['Date'].dt.year<=years_range[1])]
        net_sum=df.iloc[:, 25].sum() - dis_df.iloc[:, 25].sum()
        sum_flow_power.append(net_sum)

    object = None
    map_df['countries'] = countries_names
    map_df['origin'] = origins
    map_df['distination'] = dists
    map_df['sum_net_flow'] = sum_flow_power

    map_df =add_coordinates(map_df)

    map_fig = go.Figure()

    # making colors list to be used in map bubbles
    colors_list = px.colors.qualitative.Dark24
    colors_list[0]='lightsalmon'
    colors_list.extend(['#d5f4e6','#80ced6','#c83349'])
    colors_dict = {} # countries colors dictionery that will be filled

    i=0
    for country in list(map_df['origin'].unique()): # filling countries colors dictionery with country and color
        colors_dict[country] = colors_list[i]
        i+=1


    for i in range(len(map_df)):
        net_imp = map_df['sum_net_flow'][i]
        o=map_df['origin'][i]
        d=map_df['distination'][i]

        lons = [map_df['origin_lon'][i], map_df['dist_lon'][i]]
        lats = [map_df['origin_lat'][i], map_df['dist_lat'][i]]

        color = colors_dict[o]

        if net_imp > 0: # if the net flow > 0 the color of line will be the color of origin country
            color=colors_dict[o]

        elif net_imp == 0: # if the net flow = 0 the color of line will be splitted between the two countries
            dist_lon=(map_df['origin_lon'][i] + map_df['dist_lon'][i] ) / 2
            dist_lat=(map_df['origin_lat'][i] + map_df['dist_lat'][i] ) /2
            lons=[map_df['origin_lon'][i], dist_lon]
            lats=[map_df['origin_lat'][i], dist_lat]
            color=colors_dict[o]

        else: # if the net flow < 0 the color of line will be the color of distination country
            color=colors_dict[d]

        # make the map with corresponding marker color ( bubble )

        map_fig.add_trace(go.Scattermapbox(showlegend=False,
                                           lon=lons,
                                           lat=lats,
                                           mode='lines',
                                           marker={'color': 'white', 'size': 4, 'allowoverlap': True, 'opacity': 0},
                                           line=dict(width=4, color=color), hoverinfo='skip'
                                           # unselected={'marker': {'opacity': 1}},
                                           # selected={'marker': {'opacity': 0.5, 'size': 15}},

                                           )
                          )

    nodes_df = map_df.groupby(['origin', 'origin_lon', 'origin_lat'])['sum_net_flow'].mean().reset_index()
    # print(nodes_df)

    hov_text = []
    for ind in nodes_df.index:
        hover_df = map_df[map_df['countries'].str.contains('{}'.format(nodes_df['origin'][ind] + '_'))]
        hover_strings = ['Country Name : {}'.format(nodes_df['origin'][ind])]
        for i, row in hover_df.iterrows():
            hov_string = '{} : {}'.format(row['countries'], int(row['sum_net_flow']))
            hover_strings.append(hov_string)

        final_string = '<br>'.join(hover_strings)
        hov_text.append(final_string)

    nodes_df['hover'] = hov_text

    map_fig.add_trace(go.Scattermapbox(lat=nodes_df['origin_lat'], lon=nodes_df['origin_lon'],showlegend=False,name= 'Net Flows',
                                       marker=dict(
                                           size=20,
                                           color=list(map(lambda x: colors_dict[x], nodes_df['origin'].to_list())),
                                           sizemode='area', opacity=1
                                       ),
                                    #    text=nodes_df['origin'].to_list(),textposition ='top left' ,
                                       hoverinfo='text', hovertemplate=nodes_df['hover'], customdata=nodes_df['hover']))

    map_fig.update_layout(mapbox_style='open-street-map', mapbox_center_lon=9, mapbox_center_lat=53,
                          mapbox_zoom=3.2)
    map_fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0}, hoverdistance=2, uirevision='foo',
                          clickmode='event+select', hovermode='closest')

    map_fig.update_layout(title_text='Net Flow MW',
                          title_x=0.5,
                          #  width=1200,  height=700,
                          font=dict(size=14, family='bold', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
                          paper_bgcolor='#20374c'  # ,

                          , margin=dict(l=0, r=0, t=40, b=0)

                          )

    # map_fig.show()

    return map_fig

# i only commented on the parts different from previous bubble map
def create_net_import_map(object,years_range):

    countries = list(object.keys())
    # print(countries)
    countries_names = []
    sum_imp_power = []
    map_df = pd.DataFrame()
    for country in countries:
        df = object[country]


        df = df[(df['Date'].dt.year>=years_range[0]) & (df['Date'].dt.year<=years_range[1])]
        countries_names.append(country)
        sum_imp_power.append(df.iloc[:, 25].sum())

    object = None
    map_df['origin'] = countries_names
    map_df['sum_imp_power'] = sum_imp_power

    map_df = add_coord_origins(map_df)


    hov_text = []
    for ind in map_df.index:
        hov_text.append(
            'Country : {}<br>Net-Import : {}'.format(
                map_df['origin'][ind], int(map_df['sum_imp_power'][ind]), ))

    map_df['hover'] = hov_text


    map_fig=go.Figure()

    scale1 = int(map_df['sum_imp_power'].max() / 50) # scale of positive values ( 25 to 50 )
    scale2=int(map_df['sum_imp_power'].min() / 25)   # scale of negative values ( 0 to 25 )

    for i in map_df.index:
        net_imp=map_df['sum_imp_power'][i]
        marker_size=25
        if net_imp>0: # if net import is positive value divide it scale 1 to get the size ( max is 50 )
            marker_size=int(net_imp/scale1)
            if marker_size<25: # make 25 is the minimum size
                marker_size=25

        elif net_imp<0: # if if net import is positive value divide it scale 1 to get the size
            marker_size=26 - int( (abs(net_imp) / abs(scale2)) )
            if marker_size > 25: # make 25 is the maximum size
                marker_size=25

        if marker_size==0:
            marker_size=25

        map_fig.add_trace(go.Scattermapbox(lat=[map_df['origin_lat'][i]], lon=[map_df['origin_lon'][i]],name= 'Net Import' ,showlegend=False,
                                      marker=dict(
                                          size=marker_size,
                                          color='blue',
                                          sizemode='area',opacity=1
                                      ),
                                      hoverinfo='text', hovertemplate=map_df['hover'][i]))
#, customdata=map_df['hover'][i]
    map_fig.update_layout(mapbox_style='open-street-map', mapbox_center_lon=9, mapbox_center_lat=53,
                       mapbox_zoom=3.2)
    map_fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0},  uirevision='foo',
                       clickmode='event+select', hovermode='closest',)

    map_fig.update_layout(title_text='Net Import MW ',
                       title_x=0.5,
                       #  width=1200,  height=700,
                       font=dict(size=14, family='bold', color='white'), hoverlabel=dict(
            font_size=18, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
                       paper_bgcolor='#20374c'  # ,

                       , margin=dict(l=0, r=0, t=40, b=0)

                       )

    #map_fig.show()

    return map_fig