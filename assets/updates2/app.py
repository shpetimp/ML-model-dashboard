import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State,MATCH,ALL
import pandas as pd
import pickle as pkl
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
from string import digits
import json
from flask import Flask
import math
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
import flow_page
import price_page
import capacity_page
import net_import
import country_converter as coco

#standard_names = coco.convert(names=['NO-02'], to='name_short')
#print(standard_names)


server = Flask(__name__)
app = dash.Dash(
    __name__,server=server,
    meta_tags=[
        {
            'charset': 'utf-8',
        },
        {
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1.0'   #, shrink-to-fit=no
        }
    ] ,
)

with open("NetImport_20220208.pickle", "rb") as f:
    object = pkl.load(f)

countries = list(object.keys())
print(countries)
#df = object['FRA']
#df.to_csv('FRA.csv')
#print(df)
#print(df.columns)
print('2022.5'.split('.'))

#df=object['DEU']
#print(df.head())
#print(df.columns)
#df.to_csv('DEU.csv')

#dic=capacity_page.get_lon_lat(origins)
#print(dic)

#map_df=capacity_page.add_lon_lat(map_df)



#map_df=pd.read_csv('map_data.csv')
#print(map_df['origin'].unique())




#external_stylesheets=[dbc.themes.BOOTSTRAP]
app.config.suppress_callback_exceptions = True

text_font_size='1.7vh'
navbar_font_size='2vh'
header_font_size='2vh'

encoded = base64.b64encode(open('plotly.png', 'rb').read())

logo_img=html.Img(src='data:image/jpg;base64,{}'.format(encoded.decode()), id='logo_img', height='70vh',
                  style=dict(marginLeft='1vh'))

db_logo_img=dbc.Col([ logo_img] ,
        xs=dict(size=2,offset=0), sm=dict(size=2,offset=0),
        md=dict(size=1,offset=0), lg=dict(size=1,offset=0), xl=dict(size=1,offset=0))

header_text=html.Div('Data Visualization Dashboard',style=dict(color='white',
                     fontWeight='bold',fontSize='2.8vh',marginTop='1vh',marginLeft='1.5vh'))

db_header_text=  dbc.Col([ header_text] ,
        xs=dict(size=10,offset=0), sm=dict(size=10,offset=0),
        md=dict(size=10,offset=0), lg=dict(size=10,offset=0), xl=dict(size=10,offset=0))




navigation_header=dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Flow", active='exact', href="/Flow",id='Flow',className="page-link",
                                style=dict(fontSize=navbar_font_size,color='primary'))),

        dbc.NavItem(dbc.NavLink("Power Planets", href="/Planets",active='exact',id='Planets',className="page-link",
                                style=dict(fontSize=navbar_font_size,color='primary'))),

        dbc.NavItem(dbc.NavLink("Power price", href="/price", active='exact', id='price',className="page-link",
                                style=dict(fontSize=navbar_font_size,color='primary'))),

        dbc.NavItem(dbc.NavLink("NetImport", href="/NetImport", active='exact', id='NetImport',className="page-link",
                                 style=dict(fontSize=navbar_font_size,color='primary'))),

        dbc.NavItem(dbc.NavLink("TransmisionCap", href="/TransmisionCap", active='exact', id='TransmisionCap',className="page-link",
                                 style=dict(fontSize=navbar_font_size,color='primary')))

    ],
    pills=True,
)
db_navigation_header=dbc.Col([navigation_header],
                             xs=dict(size=12, offset=0), sm=dict(size=12, offset=0),
                             md=dict(size=12, offset=0), lg=dict(size=5, offset=1), xl=dict(size=5, offset=1)
                             )



#print( list( object.keys() ) )

#print('DEU_AUT' , object['DEU_AUT'].head() )

#filtered_by_hours = int((df.index.max() - df.index.min()) / pd.Timedelta('1 hour'))
#dtick_hours=math.ceil( filtered_by_hours / (12) )












app.layout=html.Div([ dbc.Row([db_logo_img,db_header_text],style=dict(backgroundColor='#20374c') )
                      ,dbc.Row([db_navigation_header])  , html.Br()  ,dbc.Row( id='layout')

                       ,dcc.Location(id='url', refresh=True,pathname='/Flow')

                      ])





@app.callback(Output('layout','children'),
               Input('url','pathname'))
def change_page(url):
    if url == '/Flow':
        layout=flow_page.creat_flow_layout()
        return layout

    elif url == '/price':
        layout=price_page.creat_price_layout()
        return layout

    elif url == '/TransmisionCap':
        layout=capacity_page.create_capacity_layout()
        return layout

    elif url == '/NetImport':
        layout=net_import.create_net_import_layout()
        return layout

    else:
        return dash.no_update

@app.callback([Output('flow_line_chart','figure'),Output('flow_data','data')],
               [Input('flow_country_menu','value'),Input('flow_resolution_menu','value'),Input('flow_scenarios_list','value')]
              )
def update_flow_line_chart(selected_countries,selected_resolution,selected_scenarios):
    with open("Flow_20220208.pickle", "rb") as f:
        object = pkl.load(f)
   # countries = list(object.keys())
    df = object['{}'.format(selected_countries)]
    df.set_index('Date', inplace=True)
    df.columns=['1991', '1992', '1993', '1994', '1995', '1996', '1997',
            '1998', '1999', '2000', '2001', '2002', '2003', '2004',
            '2005', '2006', '2007', '2008', '2009', '2010', '2011',
            '2012', '2013', '2014', '2015', 'Normal']

    df['Exp']=df.iloc[: , :-1].mean(axis=1)
    graph_data =df.resample('3M').mean()
    if selected_resolution == 'Mean Agg. Quarterly':
        graph_data=df.resample('3M').mean()

    elif selected_resolution == 'Sum Agg. Quarterly':
        graph_data=df.resample('3M').sum()

    elif selected_resolution == 'Mean Agg. Monthly':
        graph_data=df.resample('1M').mean()

    elif selected_resolution == 'Sum Agg. Monthly':
        graph_data=df.resample('1M').sum()

    elif selected_resolution == 'Mean Agg. Daily':
        graph_data=df.resample('1D').mean()

    elif selected_resolution == 'Sum Agg. Daily':
        graph_data=df.resample('1D').sum()

    elif selected_resolution== 'Hourly':
        graph_data=df

    fig=go.Figure()
    colors = px.colors.qualitative.Light24
    colors[0]='lightsalmon'
    colors.extend(['#d5f4e6','#80ced6','#c83349'])
    scenarios_colors = {'1991': colors[0], '1992': colors[1], '1993': colors[2], '1994': colors[3],
                      '1995': colors[4], '1996': colors[5], '1997': colors[6], '1998': colors[7],
                      '1999': colors[8], '2000': colors[9],'2001': colors[10],'2002': colors[11],'2003': colors[12]
                        ,'2004': colors[13],'2005': colors[14],'2006': colors[15],'2007': colors[16],'2008': colors[17],
                        '2009': colors[18],'2010': colors[19],'2011': colors[20],'2012': colors[21],'2013': colors[22],
                        '2014': colors[23],'2015': colors[24],'Normal': colors[25],'Exp':colors[26]}
    i=0
    for scenario in selected_scenarios:
        fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data[scenario], mode='lines', name=scenario,
                                 marker_color=scenarios_colors[scenario]
                                 ))
        i+=1


    fig.update_layout(
        title='Power Flow', xaxis_title='Date', yaxis_title='MWh/h',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=16, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c',
        xaxis=dict(

            tickwidth=2, tickcolor='lightsalmon',
            ticks="outside",
            tickson="labels",
            rangeslider_visible=False
        )
    )
#boundaries
    # 0f2537

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)
    graph_data['Date']=graph_data.index
    selected_scenarios.append('Date')
    return (fig , graph_data[selected_scenarios].to_dict('records'))





@app.callback([Output('price_line_chart','figure'),Output('price_data','data')],
               [Input('price_country_menu','value'),Input('price_resolution_menu','value'),Input('price_scenarios_list','value')]
              )
def update_price_line_chart(selected_countries,selected_resolution,selected_scenarios):
    with open("PowerPrice_20220208.pickle", "rb") as f:
        object = pkl.load(f)
   # countries = list(object.keys())
    df = object['{}'.format(selected_countries)]
    df.set_index('Date', inplace=True)
    df.columns=['1991', '1992', '1993', '1994', '1995', '1996', '1997',
            '1998', '1999', '2000', '2001', '2002', '2003', '2004',
            '2005', '2006', '2007', '2008', '2009', '2010', '2011',
            '2012', '2013', '2014', '2015', 'Normal']

    df['Exp']=df.iloc[: , :-1].mean(axis=1)
    graph_data =df.resample('3M').mean()

    graph_data =df.resample('3M').mean()
    if selected_resolution == 'Mean Agg. Quarterly':
        graph_data=df.resample('3M').mean()

    elif selected_resolution == 'Sum Agg. Quarterly':
        graph_data=df.resample('3M').sum()

    elif selected_resolution == 'Mean Agg. Monthly':
        graph_data=df.resample('1M').mean()

    elif selected_resolution == 'Sum Agg. Monthly':
        graph_data=df.resample('1M').sum()

    elif selected_resolution == 'Mean Agg. Daily':
        graph_data=df.resample('1D').mean()

    elif selected_resolution == 'Sum Agg. Daily':
        graph_data=df.resample('1D').sum()

    elif selected_resolution== 'Hourly':
        graph_data=df

    fig=go.Figure()
    colors = px.colors.qualitative.Light24
    colors[0]='lightsalmon'
    colors.extend(['#d5f4e6','#80ced6','#c83349'])
    scenarios_colors = {'1991': colors[0], '1992': colors[1], '1993': colors[2], '1994': colors[3],
                      '1995': colors[4], '1996': colors[5], '1997': colors[6], '1998': colors[7],
                      '1999': colors[8], '2000': colors[9],'2001': colors[10],'2002': colors[11],'2003': colors[12]
                        ,'2004': colors[13],'2005': colors[14],'2006': colors[15],'2007': colors[16],'2008': colors[17],
                        '2009': colors[18],'2010': colors[19],'2011': colors[20],'2012': colors[21],'2013': colors[22],
                        '2014': colors[23],'2015': colors[24],'Normal': colors[25],'Exp':colors[26]}
    i=0
    for scenario in selected_scenarios:
        fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data[scenario], mode='lines', name=scenario,
                                 marker_color=scenarios_colors[scenario]
                                 ))
        i+=1


    fig.update_layout(
        title='Power Price', xaxis_title='Date', yaxis_title='€/MWh',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=16, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c',
        xaxis=dict(

            tickwidth=2, tickcolor='lightsalmon',
            ticks="outside",
            tickson="labels",
            rangeslider_visible=False
        )
    )
#boundaries
    # 0f2537

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)
    graph_data['Date']=graph_data.index
    selected_scenarios.append('Date')
    return (fig , graph_data[selected_scenarios].to_dict('records'))




@app.callback([Output('cap_line_chart','figure'),Output('cap_data','data')],
               [Input('cap_country_menu','value'),Input('cap_resolution_menu','value')]
              )
def update_cap_line_chart(selected_countries,selected_resolution):
    with open("TransmissionCap_20220208.pickle", "rb") as f:
        object = pkl.load(f)
   # countries = list(object.keys())
    df = object['{}'.format(selected_countries)]
    df.set_index('Date', inplace=True)
    df.columns=['1991', '1992', '1993', '1994', '1995', '1996', '1997',
            '1998', '1999', '2000', '2001', '2002', '2003', '2004',
            '2005', '2006', '2007', '2008', '2009', '2010', '2011',
            '2012', '2013', '2014', '2015', 'Normal']

    graph_data =df.resample('3M').mean()
    if selected_resolution == 'Mean Agg. Quarterly':
        graph_data=df.resample('3M').mean()

    elif selected_resolution == 'Sum Agg. Quarterly':
        graph_data=df.resample('3M').sum()

    elif selected_resolution == 'Mean Agg. Monthly':
        graph_data=df.resample('1M').mean()

    elif selected_resolution == 'Sum Agg. Monthly':
        graph_data=df.resample('1M').sum()

    elif selected_resolution == 'Mean Agg. Daily':
        graph_data=df.resample('1D').mean()

    elif selected_resolution == 'Sum Agg. Daily':
        graph_data=df.resample('1D').sum()

    elif selected_resolution== 'Hourly':
        graph_data=df

    fig=go.Figure()


    fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data['Normal'], mode='lines', name='Normal',
                                 marker_color='#80ced6' , showlegend=True
                                 ))



    fig.update_layout(
        title='Power Capacity', xaxis_title='Date', yaxis_title='MW',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=16, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c',
        xaxis=dict(

            tickwidth=2, tickcolor='lightsalmon',
            ticks="outside",
            tickson="labels",
            rangeslider_visible=False
        )
    )
#boundaries
    # 0f2537

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)
    graph_data['Date']=graph_data.index

    return (fig , graph_data.to_dict('records'))





@app.callback(Output('flow_csv_download_data', 'data'),
              Input('flow_download_csv', 'n_clicks'),State('flow_data','data')

    ,prevent_initial_call=True)
def download_flow_csv(clicks,flow_data):
    flow_df=pd.DataFrame(flow_data)
    return send_data_frame(flow_df.to_csv, "flow_data.csv")


@app.callback(Output('price_csv_download_data', 'data'),
              Input('price_download_csv', 'n_clicks'),State('price_data','data')

    ,prevent_initial_call=True)
def download_flow_csv(clicks,price_data):
    price_df=pd.DataFrame(price_data)
    return send_data_frame(price_df.to_csv, "price_data.csv")

@app.callback(Output('cap_csv_download_data', 'data'),
              Input('cap_download_csv', 'n_clicks'),State('cap_data','data')

    ,prevent_initial_call=True)
def download_cap_csv(clicks,cap_data):
    cap_df=pd.DataFrame(cap_data)
    return send_data_frame(cap_df.to_csv, "cap_data.csv")


@app.callback(Output('capacity_map', 'figure'),
              Input('cap_map_slider', 'value'))
def update_cap_map(years_range):
    with open("TransmissionCap_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    map_fig=capacity_page.create_cap_map(object, years_range)
    return map_fig

@app.callback(Output('flow_bar_chart', 'figure'),
              Input('flow_bar_slider', 'value'))
def update_flow_bar(years_range):
    with open("Flow_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    bar_fig=flow_page.create_flow_bar_fig(object,years_range)
    return bar_fig

@app.callback(Output('price_bar_chart', 'figure'),
              Input('price_bar_slider', 'value'))
def update_price_bar(years_range):
    with open("PowerPrice_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    bar_fig=price_page.create_price_bar_fig(object,years_range)
    return bar_fig


@app.callback(Output('net_import_map', 'figure'),
              Input('net_imp_map_slider', 'value'))
def update_net_map(years_range):
    with open("Flow_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    map_fig=net_import.create_net_import_map(object, years_range)
    return map_fig

if __name__ == '__main__':
    app.run_server(host='localhost',port=8050,debug=True,dev_tools_silence_routes_logging=True)