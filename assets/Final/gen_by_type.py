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
    with open("Gen_Type_20220209.pickle", "rb") as f:
        object = pkl.load(f)
    print(time.time() - start)

    pie_df_marks = object['DEU/Plant/Steam/Biofuels1']

    keys=object.keys()
    object_sub = {key: value for key, value in object.items() if 'DEU' in key}
    pie_fig =create_pie_chart([2022,2029],object_sub)
    area_fig = create_area_chart('Mean Agg. Quarterly',['Biofuels', 'CHP', 'Coal'],object_sub)
    bar_fig=create_gen_bar_chart('Mean Agg. Quarterly',['Flexible Assets', 'Demand Shedding', 'Curtailment'],object_sub)
    object=None
    object_sub=None
    countries = []
    for key in keys:
        country=key.split('/')[0]
        if country not in countries:
            countries.append(country)

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
        value=[facilities[0],facilities[1] , facilities[2]], label_style=dict(fontSize='1.5vh'),
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


def create_pie_chart(years_range,object_subset):

    facilities=['Biofuels', 'CHP', 'Coal', 'CH4', 'Hydro', 'Lignite', 'Nuc', 'Oil',
                       'Other/', 'Pump', 'Res', 'RoR', 'Solar', 'Wind']




    colors = px.colors.qualitative.Light24
    colors[0]='lightsalmon'
    colors.extend(['#d5f4e6','#80ced6','#c83349'])
    fac_colors = {'Solar': colors[0], 'CHP': colors[1], 'Coal': colors[2], 'CH4': colors[3],
                      'Hydro': colors[4], 'Lignite': colors[5], 'Nuc': colors[6], 'Oil': colors[7],
                      'Other/': colors[8], 'Pump': colors[9],'Res': colors[10],'RoR': colors[11],'Biofuels': colors[14]
                      ,'Wind': colors[25]}


    country_facilities=pd.Series(data=list(object_subset.keys()) )
    pie_values=[]
    pie_labels=[]
    for fac in facilities:
        if fac !='Other/':
            df_name=country_facilities[country_facilities.str.contains(fac)].values[0]
            df=object_subset[df_name]

            df = df[(df['Date'].dt.year >= years_range[0]) & (df['Date'].dt.year <= years_range[1])]

            df.set_index('Date', inplace=True)
            df.columns = ['1991', '1992', '1993', '1994', '1995', '1996', '1997',
                          '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                          '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                          '2012', '2013', '2014', '2015', 'Normal']
            sum_power = df['Normal'].sum()
            if sum_power!=0:
                pie_values.append(sum_power)
                fac_name=fac.replace('/','')
                pie_labels.append(fac_name)

        else:
            other_names=country_facilities[country_facilities.str.contains(fac)]

            other_sum=0
            for name in other_names:
                df=object_subset[name]
                ndf=df[(df['Date'].dt.year >= years_range[0]) & (df['Date'].dt.year <= years_range[1])]
                new_sum=df.iloc[:, 25].sum()
                other_sum=other_sum+new_sum

            if other_sum!=0:
                pie_values.append(other_sum)
                fac_name=fac.replace('/','')
                pie_labels.append(fac_name)


    pie_colors=[]
    for label in pie_labels:
        if label=='Other':
            pie_colors.append(fac_colors['Other/'])
        else:
            pie_colors.append(fac_colors[label])

    fig = go.Figure(data=go.Pie(labels=pie_labels, values=pie_values ))
    fig.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=14, textfont_family='Arial' ,
                      marker=dict(colors=pie_colors, line=dict(color='#0f2937')))


    fig.update_layout(
        title='Percentages of Facilities power produced',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c' ,margin=dict(l=0, r=0, t=40, b=0)

    )
    return fig



def create_area_chart(selected_resolution,selected_facilities,object_subset):
  #  ctx = dash.callback_context
   # if ctx.triggered:
   #     input_id = ctx.triggered[0]['prop_id'].split('.')[0]


    fig=go.Figure()
    colors = px.colors.qualitative.Light24
    colors[0]='lightsalmon'
    colors.extend(['#d5f4e6','#80ced6','#c83349'])
    fac_colors = {'Solar': colors[0], 'CHP': colors[1], 'Coal': colors[2], 'CH4': colors[3],
                      'Hydro': colors[4], 'Lignite': colors[5], 'Nuc': colors[6], 'Oil': colors[7],
                      'Other/': colors[8], 'Pump': colors[9],'Res': colors[10],'RoR': colors[11],'Biofuels': colors[14]
                      ,'Wind': colors[25]}


    country_facilities=pd.Series(data=list(object_subset.keys()) )
    dfs_names=[]
    for facility in selected_facilities:
        if facility != 'Other/':
            df_name=country_facilities[country_facilities.str.contains(facility)].values[0]
            df=object_subset[df_name]
            df.set_index('Date', inplace=True)
            df.columns = ['1991', '1992', '1993', '1994', '1995', '1996', '1997',
                          '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                          '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                          '2012', '2013', '2014', '2015', 'Normal']

            graph_data = df.resample('3M').mean()

            if selected_resolution == 'Mean Agg. Quarterly':
                graph_data = df.resample('3M').mean()

            elif selected_resolution == 'Sum Agg. Quarterly':
                graph_data = df.resample('3M').sum()

            elif selected_resolution == 'Mean Agg. Monthly':
                graph_data = df.resample('1M').mean()

            elif selected_resolution == 'Sum Agg. Monthly':
                graph_data = df.resample('1M').sum()

            elif selected_resolution == 'Mean Agg. Daily':
                graph_data = df.resample('1D').mean()

            elif selected_resolution == 'Sum Agg. Daily':
                graph_data = df.resample('1D').sum()

            elif selected_resolution == 'Hourly':
                graph_data = df

            fac_name=facility.replace('/','')
            fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data['Normal'].astype('int64'), mode='lines', name=fac_name,
                                     marker_color=fac_colors[facility] ,stackgroup='one'
                                     ))

        else:
            other_names=country_facilities[country_facilities.str.contains(facility)]

            df=pd.Series(data=0,index=object_subset[other_names.values[0]]['Date'])
            for name in other_names:
                new_df=object_subset[name].iloc[:, 25].reindex(df.index,fill_value=0)
                df=df+new_df

            graph_data = df.resample('3M').mean()

            if selected_resolution == 'Mean Agg. Quarterly':
                graph_data = df.resample('3M').mean()

            elif selected_resolution == 'Sum Agg. Quarterly':
                graph_data = df.resample('3M').sum()

            elif selected_resolution == 'Mean Agg. Monthly':
                graph_data = df.resample('1M').mean()

            elif selected_resolution == 'Sum Agg. Monthly':
                graph_data = df.resample('1M').sum()

            elif selected_resolution == 'Mean Agg. Daily':
                graph_data = df.resample('1D').mean()

            elif selected_resolution == 'Sum Agg. Daily':
                graph_data = df.resample('1D').sum()

            elif selected_resolution == 'Hourly':
                graph_data = df

            fac_name = facility.replace('/', '')
            fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data.astype('int64'), mode='lines', name=fac_name,
                                     marker_color=fac_colors[facility] ,stackgroup='one'
                                     ))

    object_subset=None
    fig.update_layout(
        title='Power Produced by Facilities', xaxis_title='Date', yaxis_title='MWh/h',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=16, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c',
        xaxis=dict(

            tickwidth=2, tickcolor='#80ced6',
            ticks="outside",
            tickson="labels",
            rangeslider_visible=False
        )
    )
#boundaries
    # 0f2537

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)

    return (fig )


def create_gen_bar_chart(selected_resolution,selected_assets,object_subset):
    fig = go.Figure()

    assets_colors = {'Flexible Assets': 'indianred', 'Demand Shedding': 'skyblue', 'Curtailment': 'navy'}

    country_assets = pd.Series(data=list(object_subset.keys()))
    dfs_names = []
    for asset in selected_assets:
        if asset != 'Other/':
            df_name = country_assets[country_assets.str.contains(asset)].values[0]
            df = object_subset[df_name]

            df.set_index('Date', inplace=True)
            df.columns = ['1991', '1992', '1993', '1994', '1995', '1996', '1997',
                          '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                          '2005', '2006', '2007', '2008', '2009', '2010', '2011',
                          '2012', '2013', '2014', '2015', 'Normal']

            graph_data = df.resample('3M').mean()

            if selected_resolution == 'Mean Agg. Quarterly':
                graph_data = df.resample('3M').mean()

            elif selected_resolution == 'Sum Agg. Quarterly':
                graph_data = df.resample('3M').sum()

            elif selected_resolution == 'Mean Agg. Monthly':
                graph_data = df.resample('1M').mean()

            elif selected_resolution == 'Sum Agg. Monthly':
                graph_data = df.resample('1M').sum()

            elif selected_resolution == 'Mean Agg. Daily':
                graph_data = df.resample('1D').mean()

            elif selected_resolution == 'Sum Agg. Daily':
                graph_data = df.resample('1D').sum()

            elif selected_resolution == 'Hourly':
                graph_data = df

            fig.add_trace(go.Bar(name=asset, x=graph_data.index, y=graph_data['Normal'].astype('int64'),
                                 marker_color=assets_colors[asset])

                          )

    object_subset = None
    fig.update_layout(
        title='Power Produced By Balancing Assets', xaxis_title='Date',
        yaxis_title='MWh',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c', margin=dict(l=0, r=0, t=40, b=0), barmode='stack'

    )
    # boundaries
    # 0f2537

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)

    return fig