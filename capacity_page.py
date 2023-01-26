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

ctx = ssl.create_default_context(cafile=certifi.where()) # a certificate used with free api of geopy.geocoders for contries coordinates and addresses
geopy.geocoders.options.default_ssl_context = ctx


# countries name and corresponding iso alpha 3 code dictionery used on begining to get longitude and latitude of countries
############# not needed now because data is got from countries_coordinates csv file
countries_dict={'DEU': 'Germany', 'AUT': 'Austria', 'FRA': 'France', 'BEL': 'Belgium', 'NLD': 'Netherlands', 'NO2': 'Kristiansand',
                'DK1': 'Aarhus', 'GBR': 'United Kingdom', 'CHE': 'Switzerland', 'CZE': 'Czechia', 'DK2': 'Copenhagen', 'POL': 'Poland',
                'SE4': 'Lund', 'ITA': 'Italy', 'ESP': 'Spain', 'NO5': 'Bergen', 'BGR': 'Bulgaria', 'HRV': 'Croatia', 'CYP': 'Cyprus',
                'DNK': 'Denmark', 'EST': 'Estonia', 'FIN': 'Finland', 'GRC': 'Greece', 'HUN': 'Hungary', 'IRL': 'Ireland', 'PRT': 'Portugal',
                'ROU': 'Romania', 'SWE': 'Sweden', 'NO1': 'Oslo', 'NO3': 'Molde', 'NO4': 'Tromsø', 'SE1': 'Luleå', 'SE2': 'Sundsvall',
                'SE3': 'Stockholm'}



# function uses the csv file of countries_coordinates to add the coordinated to the countries ( origin and distination )of the input dataframe
# returns the dataframe with the added countries coordinated to be ready to be used in making a map
def add_coordinates(df):
    # origin and distination latitudes and longitute lists to be filled and added to the dataframe
    origin_lon=[]
    origin_lat=[]
    dist_lon=[]
    dist_lat=[]
    origin_names=df['origin'].to_list() # get origin names
    dist_names=df['distination'].to_list() # get distinations names

    df_coord = pd.read_csv('countries_coordinates.csv') # get coordinates data
    countries_coordinates = df_coord.to_dict('list') # convert it to dictionery to be used easily

    for origin , dist in zip(origin_names, dist_names): # looping through origins and distinations names and get corresponding
                                                        # coordinates to be added to lists
        origin_lon.append( countries_coordinates[origin][1] )
        origin_lat.append( countries_coordinates[origin][0] )
        dist_lon.append( countries_coordinates[dist][1] )
        dist_lat.append( countries_coordinates[dist][0] )

    # add the gotten coordinates to the dataframe and return it
    df['origin_lon']=origin_lon
    df['origin_lat']=origin_lat
    df['dist_lon']=dist_lon
    df['dist_lat']=dist_lat

    return df



# this function gets the all geo info about the country oe city name passe
################# not needed now because data is got from countries_coordinates csv file

def findGeocode(country):
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout
    try:

        # Specify the user_agent as your
        # app name it should not be none
        geolocator = Nominatim(user_agent="dash_plotly")

        return geolocator.geocode(country)

    except GeocoderTimedOut:

        return findGeocode(country)


# take input as countries names list and return all its coordinates
################# not needed now because data is got from countries_coordinates csv file
def get_lon_lat(names_list):
    coordinates_dict={}

    for name in names_list:

        if findGeocode(countries_dict[name]) != None:

            loc = findGeocode(countries_dict[name])

            # coordinates returned from
            # function is stored into
            # two separate list
            coordinates_dict[name]=[loc.latitude,loc.longitude]


        # if coordinate for a city not
        # found, insert "NaN" indicating
        # missing value
        else:
            coordinates_dict[name]=[np.nan,np.nan]

    return coordinates_dict


map_fig=go.Figure(go.Scattermapbox())
line_fig=go.Figure()
text_font_size='1.7vh'
navbar_font_size='2vh'
header_font_size='2vh'



line_div=html.Div([
            dcc.Graph(id='cap_line_chart', config={'displayModeBar': True, 'scrollZoom': True,'displaylogo': False},
                style=dict(height='50vh',backgroundColor='#20374c') ,figure=line_fig
            ) ] ,id='cap_line_div'
        )



resolution_menu=  dcc.Dropdown(
        id='cap_resolution_menu',
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


download_csv=html.Div([dbc.Button("Download CSV", color="primary", size='lg', n_clicks=0,id="cap_download_csv"
                            ,style=dict(fontSize='1.6vh')
                            )],style=dict(display='inline-block',marginLeft='2vh',marginTop='3%'))

csv_download_data=html.Div([Download(id="cap_csv_download_data")])



def create_capacity_layout():

    with open("TransmissionCap_20220208.pickle", "rb") as f:
        object = pkl.load(f)

    df_marks = object['DEU_FRA']
    countries = list(object.keys())

    object = None
    scenarios = ['Normal','1991', '1992', '1993', '1994', '1995', '1996', '1997',
                 '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                 '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                 '2012', '2013', '2014', '2015']

    country_menu = dcc.Dropdown(className="custom-dropdown",
                                id='cap_country_menu',

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
        id="cap_scenarios_list", style=dict(fontSize='2vh', marginLeft='0', color='white')
    )



    map_fig=go.Figure(go.Scattermapbox()) # initializing empty map fig
    map_fig.update_layout(mapbox_style='open-street-map') # adding map background style
    # available backgrounds : "open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor"
    map_div = html.Div([
        dcc.Graph(id='capacity_map', config={'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False},
                  style=dict(height='60vh', backgroundColor='#20374c'), figure=map_fig
                  )], id='cap_map_div'
    )


    df_marks['Year'] = (pd.DatetimeIndex(df_marks.iloc[:, 26]).year).astype(str)
    df_marks['Year']=df_marks['Year'].astype('int32')
    years=df_marks['Year'].to_list()
    years=list(OrderedDict.fromkeys(years))
    #print(years)
    marks_values={year: {'label': '{}'.format(year), 'style': {'color': 'white'}} for year in years}
    #{year: '{}'.format(year) for year in years}
    years_slider=html.Div([dcc.RangeSlider(min=years[0], max=years[-1], step=1, value=[years[1],years[-2]], marks=marks_values ,id='cap_map_slider')
                           ])

    refresh_map = html.Div([dbc.Button("Refresh Map", color="primary", size='lg', n_clicks=0, id="refresh_map",outline=True
                                          , style=dict(fontSize=text_font_size)
                                          )],style={'width': '100%','display': 'flex','align-items': 'center','justify-content': 'center'})



    # layout to be returned
    layout = [dbc.Col([dbc.Card(dbc.CardBody(
        [html.Div([dbc.Spinner([map_div],size="lg", color="primary", type="border", fullscreen=False )
                                                 ,html.Br(),years_slider

                                                    ] , style=dict(height='70vh'))])
                          , style=dict(backgroundColor='#20374c')), html.Br()],

                xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
                md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1)

                )    ,

              dbc.Col([dbc.Card(dbc.CardBody(
                  [html.Div([dbc.Spinner([line_div], size="lg", color="primary", type="border", fullscreen=False)
                                , html.Br(), html.Div([country_menu_div, resolution_menu_div, download_csv],
                                                           style={'width': '100%', 'display': 'flex',
                                                                  'align-items': 'center',
                                                                  'justify-content': 'center'}),
                             html.Br(), csv_download_data,
                             dcc.Store(id='cap_data', data=pd.DataFrame().to_dict('records'))

                             ], style=dict(height='70vh'))])
                  , style=dict(backgroundColor='#20374c')), html.Br()
              ], xl=dict(size=6, offset=0), lg=dict(size=6, offset=0),
                  md=dict(size=10, offset=1), sm=dict(size=10, offset=1), xs=dict(size=10, offset=1))

                                ]
    return layout

# function used in callback in app.py that returns the capacity map figure
# it takes input of pickle file dictionery and slider range value
def create_cap_map(object,years_range):

    countries = list(object.keys())

    # lists of country names ('DEU_FRA') , origin names ('DEU') , distination names ('FRA'), mean capacity for each
    # it will be used in the map figure
    countries_names = []
    origins = []
    dists = []
    mean_cap = []
    map_df = pd.DataFrame() # new dataframe will contain these lists as columns to be used in map figure
    for country in countries:
        df = object[country]


        df=df[(df['Date'].dt.year>=years_range[0]) & (df['Date'].dt.year<=years_range[1])] # filtering on slider range
        # appending country names ('DEU_FRA') , origin names ('DEU') , distination names ('FRA'), mean capacity for each to the lists
        countries_names.append(country)
        origins.append(country.split('_')[0])
        dists.append(country.split('_')[1])
        mean_cap.append(df.iloc[:, 25].mean())

    object = None

    # filling dataframe columns with these lists
    map_df['countries'] = countries_names
    map_df['origin'] = origins
    map_df['distination'] = dists
    map_df['mean_cap'] = mean_cap

    map_df = add_coordinates(map_df) # adding coordinates of origins and destinations

    #print(map_df)

#line=dict(width=map_df['mean_cap']/(map_df['mean_cap'].min()),color='blue')  mapbox_zoom=3 margin={"r": 0, "t": 30, "l": 0, "b": 0}
# min_cap (map_df['mean_cap'].min())
    map_fig = go.Figure()

    # looping through map dataframe
    for i in range(len(map_df)):
        cap = map_df['mean_cap'][i]  # get capacity

        scale=int(map_df['mean_cap'].max()/12 ) # make scale for ( 0 - 12 ) for lines width
                                                # by dividing max value over 12
        line_size=int(map_df['mean_cap'][i]/scale) # line width will be its value divided by scale

        if line_size==0: # make minimum width is 1
            line_size=1

        # if we have DEU_FRA check if the reverse FRA_DEU exist
        # if it exist we will split the line between them if not dont split the line

        reversed_df=map_df[  (map_df['origin']==map_df['distination'][i])  & (map_df['distination']==map_df['origin'][i]) ]
        if reversed_df.empty: # check if the reverse value is empty
            lons=[map_df['origin_lon'][i], map_df['dist_lon'][i]] # get longitude and latitude
            lats=[map_df['origin_lat'][i], map_df['dist_lat'][i]]

        else:
            dist_lon=(map_df['origin_lon'][i] + map_df['dist_lon'][i] ) / 2 # get longitude but get half distance to latitude ( split line ) by getting the mid point in between as the latitude
            dist_lat=(map_df['origin_lat'][i] + map_df['dist_lat'][i] ) /2
            lons=[map_df['origin_lon'][i], dist_lon]
            lats=[map_df['origin_lat'][i], dist_lat]

        # create the map figure with corresponding line width
        # lines map source : https://plotly.com/python/lines-on-mapbox/
        # bubble map source : https://plotly.com/python/scattermapbox/
        # great video : https://www.youtube.com/watch?v=7R7VMSLwooo
        map_fig.add_trace(go.Scattermapbox( showlegend=False,
                                       lon=lons,
                                       lat=lats,
                                       mode='lines',
                                       marker={'color': 'skyblue', 'size': 4, 'allowoverlap': True, 'opacity': 1},
                                       line=dict(width=line_size,color='blue'),hoverinfo='skip'
                                            # unselected={'marker': {'opacity': 1}},
                                       # selected={'marker': {'opacity': 0.5, 'size': 15}},

                                       )
                      )


    # making a dataframe contains the unique country names and coordinates to be used to plot bubble map on top of lines map
    nodes_df = map_df.groupby(['origin', 'origin_lon', 'origin_lat'])['mean_cap'].mean().reset_index()
    #print(nodes_df)


    # creating the hover text array when you hover over the node or bubble
    # this is all based on python string formatiing and str.contains function illustrated before
    hov_text = []
    for ind in nodes_df.index:
        hover_df=map_df[map_df['countries'].str.contains('{}'.format(nodes_df['origin'][ind]+'_'))]
        hover_strings=['Country Name : {}'.format(nodes_df['origin'][ind])]
        for i , row in hover_df.iterrows(): # src : https://www.geeksforgeeks.org/pandas-dataframe-iterrows-function-in-python/
            hov_string='{} : {}'.format(row['countries'],int(row['mean_cap']))
            hover_strings.append(hov_string)

        final_string='<br>'.join(hover_strings)
        hov_text.append(final_string)

    nodes_df['hover'] = hov_text

    # lines map source : https://plotly.com/python/lines-on-mapbox/
    # bubble map source : https://plotly.com/python/scattermapbox/
    # great video : https://www.youtube.com/watch?v=7R7VMSLwooo

    map_fig.add_trace(go.Scattermapbox(lat=nodes_df['origin_lat'], lon=nodes_df['origin_lon'],name= 'Country' ,
                                      marker=dict(
                                          size=20,
                                          color='#00bfff',
                                          sizemode='area',opacity=1
                                      ),
                                      hoverinfo='text', hovertemplate=nodes_df['hover'], customdata=nodes_df['hover']))

    map_fig.update_layout(mapbox_style='open-street-map', mapbox_center_lon=9, mapbox_center_lat=53,
                       mapbox_zoom=3)
    map_fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0}, hoverdistance=2, uirevision='foo',
                       clickmode='event+select', hovermode='closest')

    map_fig.update_layout(title_text='Average Capacity Transmitted ( MW )',
                       title_x=0.5,
                       #  width=1200,  height=700,
                       font=dict(size=12, family='bold', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
                       paper_bgcolor='#20374c'  # ,

                       , margin=dict(l=0, r=0, t=40, b=0)

                       )

    #map_fig.show()

    return map_fig