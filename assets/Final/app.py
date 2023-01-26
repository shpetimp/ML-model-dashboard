import time
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State,MATCH,ALL
import pandas as pd
import pickle as pkl
import base64
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask
from dash_extensions.snippets import send_data_frame
from dash_extensions import Download
import flow_page
import gen_by_type
import price_page
import capacity_page
import net_import



# first of all i imported all libraries needed for dash , plotly , and all other python libraries that helps in data analysis
# Dash applications are web servers running Flask on the backend and communicating JSON packets over HTTP requests with the client ( web browser ).
# dash app consists of 2 main parts : Layout and Callbacks
# best video that explains dash app structure and functionality in link bellow
# https://www.youtube.com/watch?v=hSPmj7mK6ng
# and the link bellow shows how to use plotly library for data visualization in dash apps
# https://www.youtube.com/watch?v=_b2KXL0wHQg
# also the video bellow shows how to style your app using dash bootstrap for responsive styling
# https://www.youtube.com/watch?v=vqVwpL4bGKY
# this dash app consist of 6 files where 5 files are the layout of the 5 pages of the app ( flow_page,gen_by_type,price_page,capacity_page,net_import)
# and 1 file (app.py) that has all the callback functions that updates the 5 pages layout

# note that you can use css styles without writing css by using style options on dash components but if you need so customized styling use css
# i normally use 70% of styling with style options on dash components and 30% with pure css




# here im defining a Flask server object
#__name__ is just a convenient way to get the import name of the place the app is defined.
# Flask uses the import name to know where to look up resources, templates, static files, instance folder, etc.
server = Flask(__name__)

# her im defining dash app object
# server : server used in backend
# meta_tags : some app configerations like the initial width of app screen
app = dash.Dash(
    __name__,server=server,
    meta_tags=[
        {
            'charset': 'utf-8',
        },
        {
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1.0, shrink-to-fit=no'
        }
    ] ,
)

# telling the app that its okay if the components of a certain callback doesnt exist on the current page
# bellow is link of how to create multi page dash app
# https://dash.plotly.com/urls
app.config.suppress_callback_exceptions = True

# setting different font sizes as variables to be used later
# 'vh' stands for browser viewport height
# Hence, setting an element to value of 50vh means that the element will have size 50% of the viewport size
text_font_size='1.7vh'
navbar_font_size='2vh'
header_font_size='2vh'

# Opening the image file , reading the image data and encoding it in base64 using the base64 module in Python
# this way it is able to be used in html.img component
# you can change the image by only change the name in open('Logo.png', 'rb')
encoded = base64.b64encode(open('Logo.png', 'rb').read())

# using the encoded image in html.img component and setting height , width , margin of the image
# src : https://dash.plotly.com/dash-html-components/img
logo_img=html.Img(src='data:image/jpg;base64,{}'.format(encoded.decode()), id='logo_img', height='70vh',
                  style=dict(marginLeft='1vh'))

# setting the size and spacing of logo_img using dash bootstrap
# more info on dash bootstrap layout : https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
db_logo_img=dbc.Col([ logo_img] ,
        xs=dict(size=2,offset=0), sm=dict(size=2,offset=0),
        md=dict(size=1,offset=0), lg=dict(size=1,offset=0), xl=dict(size=1,offset=0))

# adding the header text component which is a text inside an html div
# note that all parameters in style dict are css styling of the component
# html.Div source : https://dash.plotly.com/dash-html-components/div
header_text=html.Div('Data Visualization Dashboard',style=dict(color='white',
                     fontWeight='bold',fontSize='2.8vh',marginTop='1vh',marginLeft='1.5vh'))

# setting the size and spacing of header_text using dash bootstrap
db_header_text=  dbc.Col([ header_text] ,
        xs=dict(size=10,offset=0), sm=dict(size=10,offset=0),
        md=dict(size=10,offset=0), lg=dict(size=10,offset=0), xl=dict(size=10,offset=0))



# using naviation bar to switch between pages
# see example here : https://dash-bootstrap-components.opensource.faculty.ai/docs/components/nav/
# note that i use external css to style this component you can find it in custom css file in assets folder
# thats because styles of dash here are not enough
navigation_header=dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Flow", active='exact', href="/Flow",id='Flow',className="page-link",
                                style=dict(fontSize=navbar_font_size,color='primary'))),

        dbc.NavItem(dbc.NavLink("Generation By Type", href="/Planets",active='exact',id='Planets',className="page-link",
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

# setting the size and spacing using dash bootstrap
db_navigation_header=dbc.Col([navigation_header],
                             xs=dict(size=12, offset=0), sm=dict(size=12, offset=0),
                             md=dict(size=12, offset=0), lg=dict(size=10, offset=1), xl=dict(size=10, offset=1)
                             )


# creating dash app layout object which will contain the layout of all pages
# note that i included the components that will exist in all pages like navigation header and logo image
# then i included an empty Row ( dbc.Row( id='layout') ) in which the layout of the chosen page will exist and i use callback function for that
# note that dcc.Location(id='url', refresh=True,pathname='/Flow') holds the current page pathname which is changed from the navigation header
# the value of ( href = /Flow ) in navigation header is the value of pathname this component holds and it is used to switch between pages layout by using the callback function

app.layout=html.Div([ dbc.Row([db_logo_img,db_header_text],style=dict(backgroundColor='#20374c') )
                      ,dbc.Row([db_navigation_header])  , html.Br()  ,dbc.Row( id='layout')

                       ,dcc.Location(id='url', refresh=True,pathname='/Flow')

                      ])



# a callback that takes curent pathname ( pressed page ) and changes the layout to the related page layout
# im using here functions that exist in the other files which are used to create the related page layout
# the output here is the layout Row in app.layout ( dbc.Row( id='layout') )

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
    elif url == '/Planets':
        layout=gen_by_type.creat_gen_layout()
        return layout

    else:
        return dash.no_update  # means dont update the output if other pathname is chosen

# used to update the flow page line chart
# inputs are chosen country , resolution , scenarios which are dash components created in flow page
# output is the flow line chart figure
# and the graph dataframe stored ad json in ( dcc.Store() ) component to be downloaded when pressing on download button in anothrt callback

@app.callback([Output('flow_line_chart','figure'),Output('flow_data','data')],
               [Input('flow_country_menu','value'),Input('flow_resolution_menu','value'),Input('flow_scenarios_list','value')]
              )
def update_flow_line_chart(selected_countries,selected_resolution,selected_scenarios):


    with open("Flow_20220208.pickle", "rb") as f:    # opening the flow pickle file
        object = pkl.load(f)   # loading it as a python dictionery , src : https://www.kite.com/python/answers/how-to-read-a-pickle-file-in-python

    df = object['{}'.format(selected_countries)] # getting the dataframe of the selected country in dropdown menu from the pickle file

    ######### very important
    object=None  # clearing the variables that holds the pickle file after using it tor free up Ram memory
                 # this was the solution to the performance problem specially in generation pickle file ( 3.2 gigabytes )


    df.set_index('Date', inplace=True) # setting the index of data frame to be date , src : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.set_index.html

    df.columns=['1991', '1992', '1993', '1994', '1995', '1996', '1997',
            '1998', '1999', '2000', '2001', '2002', '2003', '2004',     # change the name of dataframe columns
            '2005', '2006', '2007', '2008', '2009', '2010', '2011',
            '2012', '2013', '2014', '2015', 'Normal']

    df['Exp']=df.iloc[: , :-1].mean(axis=1) # creating a newe column named EXP which is the mean of all scenarios columns except Normal
                                            #df.iloc src : https://www.shanelynn.ie/pandas-iloc-loc-select-rows-and-columns-dataframe/
                                            # note that axis = 1 means that the means is calculated from rows side ( row by row )

    graph_data =df.resample('3M').mean() # initial value of the final dataframe to be plotted
                                         # resample function aggregate the dataframe on its date index by the resolution chosen ( 3M = every 3 Months )
                                         # src : https://www.geeksforgeeks.org/python-pandas-dataframe-resample/


    # resampling the dataframe based on resolution chosen from dropdown menu

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

    fig=go.Figure() # initializing an empty plotly figure
    colors = px.colors.qualitative.Light24 # creating a color list from plotly default color scale ( Light24 )
                                           # you can check it here : https://plotly.com/python/discrete-color/

    colors[0]='lightsalmon' # changing first color in list
    colors.extend(['#d5f4e6','#80ced6','#c83349']) # adding more colors to list

    # making a dictionery of all selected scenarios colors to be used in figure
    # the reason for this dictionery is that every scenario will have constant color in the page no matter what the order of selection
    scenarios_colors = {'1991': colors[0], '1992': colors[1], '1993': colors[2], '1994': colors[3],
                      '1995': colors[4], '1996': colors[5], '1997': colors[6], '1998': colors[7],
                      '1999': colors[8], '2000': colors[9],'2001': colors[10],'2002': colors[11],'2003': colors[12]
                        ,'2004': colors[13],'2005': colors[14],'2006': colors[15],'2007': colors[16],'2008': colors[17],
                        '2009': colors[18],'2010': colors[19],'2011': colors[20],'2012': colors[21],'2013': colors[22],
                        '2014': colors[23],'2015': colors[24],'Normal': colors[25],'Exp':colors[26]}

    # looping through selected scenarios got from check boxes and ploting the related line chart
    # plotly line chart reference : https://plotly.com/python/line-charts/
    # note that there are 2 plotly graphing libraries (plotly.graph_objects and plotly_express) i use plotly.graph_objects because it has more customizations
    i=0
    for scenario in selected_scenarios:
        fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data[scenario].astype('int64'), mode='lines', name=scenario,
                                 marker_color=scenarios_colors[scenario] # color from dictionery
                                 ))
        i+=1


    # creating the layout of all line charts where you can change titles , colors , and everything , you can find more info on link above
    fig.update_layout(
        title='Power Flow', xaxis_title='Date', yaxis_title='MWh/h',
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

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False) # removing grid lines and other extra lines so that graph is more clear
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)

    graph_data['Date']=graph_data.index # setting the graph data column to be same as date index because datframe index is not save in json format
    selected_scenarios.append('Date') # adding name Date to selected columns list
    return (fig , graph_data[selected_scenarios].to_dict('records')) # returning the figure created and dataframe as json data ( dictionery )
                                                                     # to_dict() src ; https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html







# updating stalked area chart
# inputs are country , resolution , facilities list
# output is the figure
# note that prevent_initial_call=True prevents the initial call of callback when page is loaded and only called when inputs are changed
#########  this is better for performance to not read the 3 large pickle file 3 times on loading
# src : https://dash.plotly.com/advanced-callbacks

@app.callback(Output('gen_area_chart','figure'),
               [Input('facilities_country_menu','value'),Input('facilities_resolution_menu','value'),Input('facilities_list','value')]
,prevent_initial_call=True
              )
def update_area_chart(selected_countries,selected_resolution,selected_facilities):


    with open("Gen_Type_20220209.pickle", "rb") as f:
        object = pkl.load(f)

    # taking the part of dictionery related to the country chosen
    # src : https://www.kite.com/python/answers/how-to-take-a-subset-of-a-dictionary-in-python
    object_subset = {key: value for key, value in object.items() if selected_countries in key}
    object=None

    fig=go.Figure()
    colors = px.colors.qualitative.Light24
    colors[0]='lightsalmon'
    colors.extend(['#d5f4e6','#80ced6','#c83349'])
    fac_colors = {'Solar': colors[0], 'CHP': colors[1], 'Coal': colors[2], 'CH4': colors[3],
                      'Hydro': colors[4], 'Lignite': colors[5], 'Nuc': colors[6], 'Oil': colors[7],
                      'Other/': colors[8], 'Pump': colors[9],'Res': colors[10],'RoR': colors[11],'Biofuels': colors[14]
                      ,'Wind': colors[25]}


    country_facilities=pd.Series(data=list(object_subset.keys()) ) # taking the keys of dictionery which represents the facilities names

    # looping through all selected facilities from check boxes
    for facility in selected_facilities:
        if facility != 'Other/': # if facility name not equal to Other/
            df_name=country_facilities[country_facilities.str.contains(facility)].values[0] # dataframe name got from country_facilities names
                                                                                            # that contains the corresponding selected name
                                                                                            # src : https://pandas.pydata.org/docs/reference/api/pandas.Series.str.contains.html
            df=object_subset[df_name] # get the dataframe of that name from pickle dictionery
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

            fac_name=facility.replace('/','')  # name of facitlity chosen that will be used as graph legend (.replace() removes '/'  )
            # creating line chart with adding stackgroup='one' to convert it to area chart
            # src : https://plotly.com/python/filled-area-plots/
            fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data['Normal'].astype('int64'), mode='lines', name=fac_name,
                                     marker_color=fac_colors[facility] ,stackgroup='one'
                                     ))

        else: # if Other/ in facility name
            other_names=country_facilities[country_facilities.str.contains(facility)] # getting dataframes names that contains Other/

            df=pd.Series(data=0,index=object_subset[other_names.values[0]]['Date']) # creating empty series to calculate sum on it

            for name in other_names: # for every dataframe that contains /Other
                new_df=object_subset[name].iloc[:, 25].reindex(df.index,fill_value=0) # dataframe got from pickle object and
                                                                                     # reindexing it yo same index of initial one to be able to get sum
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

    return fig



# creating stacked balancing assets bar chart
# inputs are country , resolution , the 3 assets list

@app.callback(Output('gen_bar_chart','figure'),
               [Input('bar_country_menu','value'),Input('bar_resolution_menu','value'),Input('planets_list','value')]
,prevent_initial_call=True
              )
def update_gen_bar_chart(selected_countries,selected_resolution,selected_assets):


    with open("Gen_Type_20220209.pickle", "rb") as f:
        object = pkl.load(f)


    object_subset = {key: value for key, value in object.items() if selected_countries in key}
    object=None

    fig=go.Figure()

    # dictionery for assets colors
    assets_colors = {'Flexible Assets': 'indianred', 'Demand Shedding': 'skyblue', 'Curtailment': 'navy'}


    country_assets=pd.Series(data=list(object_subset.keys()) ) # get names of assets dataframes from pickle dictionery keys
    dfs_names=[]
    # looping through selected assets from check boxes
    for asset in selected_assets:
        #################
        # same as  stalked area chart logic except the part of bar chart scroll down to check it
        if asset != 'Other/':
            df_name=country_assets[country_assets.str.contains(asset)].values[0]
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

            # plotly bar chart src : https://plotly.com/python/bar-charts/
            fig.add_trace( go.Bar(name=asset, x=graph_data.index, y=graph_data['Normal'].astype('int64'),
               marker_color=assets_colors[asset])



            )

    object_subset=None

    fig.update_layout(
        title='Power Produced By Balancing Assets', xaxis_title='Date',
        yaxis_title='MWh',
        font=dict(size=14, family='Arial', color='white'), hoverlabel=dict(
            font_size=14, font_family="Rockwell", font_color='white', bgcolor='#20374c'), plot_bgcolor='#20374c',
        paper_bgcolor='#20374c' ,margin=dict(l=0, r=0, t=40, b=0) ,barmode='stack'

    )
#boundaries
    # 0f2537

    fig.update_xaxes(showgrid=False, showline=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=True, zeroline=False)

    return fig


# facilities pie chart
# inputs are country and years slider
# output is figure


@app.callback(Output('pie_chart','figure'),
               [Input('pie_country_menu','value'),Input('pie_slider','value')]
,prevent_initial_call=True
              )
def update_pie_chart(selected_countries,years_range):

    # facilities list to be used

    facilities=['Biofuels', 'CHP', 'Coal', 'CH4', 'Hydro', 'Lignite', 'Nuc', 'Oil',
                       'Other/', 'Pump', 'Res', 'RoR', 'Solar', 'Wind']

    with open("Gen_Type_20220209.pickle", "rb") as f:
        object = pkl.load(f)


    object_subset = {key: value for key, value in object.items() if selected_countries in key}
    object=None

    fig=go.Figure()
    colors = px.colors.qualitative.Light24
    colors[0]='lightsalmon'
    colors.extend(['#d5f4e6','#80ced6','#c83349'])

    ######## very important : same dictionery was used in stalked area chart colors so that both colors in 2 graphs be consistant to be able to get insights easier
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

            sum_power = df['Normal'].sum() # getting sum of power of corresponding facility

            # appending the facility sum power and name to be used as percentages values and labels in pie chart
            if sum_power!=0:
                pie_values.append(sum_power)
                fac_name=fac.replace('/','')
                pie_labels.append(fac_name)

        else:
            other_names=country_facilities[country_facilities.str.contains(fac)]

            other_sum=0 # initialize sum of other facilities
            # loop through facilities conatains other and calculate sum power
            for name in other_names:
                df=object_subset[name]
                ndf=df[(df['Date'].dt.year >= years_range[0]) & (df['Date'].dt.year <= years_range[1])]
                new_sum=df.iloc[:, 25].sum()
                other_sum=other_sum+new_sum

            if other_sum!=0:
                pie_values.append(other_sum)
                fac_name=fac.replace('/','')
                pie_labels.append(fac_name)

    # adding the pie chart facilities colors to be the same as fac_colors dictionery
    pie_colors=[]
    for label in pie_labels:
        if label=='Other':
            pie_colors.append(fac_colors['Other/'])
        else:
            pie_colors.append(fac_colors[label])

    # plotly pie chart src : https://plotly.com/python/pie-charts/
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



############## same as update_price_line_chart , the difference is in components names and values only


@app.callback([Output('price_line_chart','figure'),Output('price_data','data')],
               [Input('price_country_menu','value'),Input('price_resolution_menu','value'),Input('price_scenarios_list','value')]
              )
def update_price_line_chart(selected_countries,selected_resolution,selected_scenarios):
    with open("PowerPrice_20220208.pickle", "rb") as f:
        object = pkl.load(f)
   # countries = list(object.keys())
    df = object['{}'.format(selected_countries)]
    object=None
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
        fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data[scenario].astype('int64'), mode='lines', name=scenario,
                                 marker_color=scenarios_colors[scenario]
                                 ))
        i+=1


    fig.update_layout(
        title='Power Price', xaxis_title='Date', yaxis_title='€/MWh',
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
    graph_data['Date']=graph_data.index
    selected_scenarios.append('Date')
    return (fig , graph_data[selected_scenarios].to_dict('records'))



############## same as update_price_line_chart , the difference is in components names and values and there is no check boxes here



@app.callback([Output('cap_line_chart','figure'),Output('cap_data','data')],
               [Input('cap_country_menu','value'),Input('cap_resolution_menu','value')]
              )
def update_cap_line_chart(selected_countries,selected_resolution):
    with open("TransmissionCap_20220208.pickle", "rb") as f:
        object = pkl.load(f)
   # countries = list(object.keys())
    df = object['{}'.format(selected_countries)]
    object=None
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


    fig.add_trace(go.Scatter(x=graph_data.index, y=graph_data['Normal'].astype('int64'), mode='lines', name='Normal',
                                 marker_color='#80ced6' , showlegend=True
                                 ))



    fig.update_layout(
        title='Power Capacity', xaxis_title='Date', yaxis_title='MW',
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
    graph_data['Date']=graph_data.index

    return (fig , graph_data.to_dict('records'))



# callback to download the figure csv data in your device
# input is download button and output is dash download component that handles the download process

@app.callback(Output('flow_csv_download_data', 'data'),
              Input('flow_download_csv', 'n_clicks'),State('flow_data','data')

    ,prevent_initial_call=True)
def download_flow_csv(clicks,flow_data):
    flow_df=pd.DataFrame(flow_data) # get the dataframe from the json data stored in dcc.Store() component
    return send_data_frame(flow_df.to_csv, "flow_data.csv") # send_data_frame() function integerate with dash download component


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


# updating capacity page map
# input is the map slider and output is map figure

@app.callback(Output('capacity_map', 'figure'),
              Input('cap_map_slider', 'value'))
def update_cap_map(years_range):
    with open("TransmissionCap_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    map_fig=capacity_page.create_cap_map(object, years_range) # using the function that return map figure from the capacity page
    return map_fig

########### same
@app.callback(Output('net_flow_map', 'figure'),
              Input('net_flow_map_slider', 'value'))
def update_flow_map(years_range):
    with open("Flow_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    map_fig=net_import.create_net_flow_map(object, years_range)
    return map_fig

########### same
@app.callback(Output('net_imp_map', 'figure'),
              Input('net_imp_map_slider', 'value'))
def update_net_map(years_range):
    with open("NetImport_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    map_fig=net_import.create_net_import_map(object, years_range)
    return map_fig

# updating flow page bar chart
# input is the  slider and output is bar figure
@app.callback(Output('flow_bar_chart', 'figure'),
              Input('flow_bar_slider', 'value'))
def update_flow_bar(years_range):
    with open("Flow_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    bar_fig=flow_page.create_flow_bar_fig(object,years_range)
    return bar_fig

########### same
@app.callback(Output('price_bar_chart', 'figure'),
              Input('price_bar_slider', 'value'))
def update_price_bar(years_range):
    with open("PowerPrice_20220208.pickle", "rb") as f:
        object = pkl.load(f)
    bar_fig=price_page.create_price_bar_fig(object,years_range)
    return bar_fig



if __name__ == '__main__':
    app.run_server(host='localhost',port=8050,debug=True,dev_tools_silence_routes_logging=True)