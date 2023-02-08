import dash
from dash import dcc
from dash import html,Output,Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

#importing data
data=pd.read_csv("parislistingdata.csv")
data["Date"] = pd.to_datetime(data["host_since"], format="%Y-%m-%d")

data.sort_values("Date", inplace=True)
data=data.replace({'has_availability':{'t':'Available','f':'Unavailable'}})#renaming t and f data
availability_count=data['has_availability'].value_counts()

#sorting data for rooms available/unavailable below the map on home page
avvalues=availability_count.values
accomodatecount=data["accommodates"].value_counts().sort_index()
dataframe=pd.DataFrame({"values":accomodatecount.keys(),"count":accomodatecount.values})


#code for plotting the scatter map on home page
scattermap = px.scatter_mapbox(data, title="Availability Of Airbnb In Paris",lat="latitude", lon="longitude", hover_name="name", hover_data=["host_id", "host_name"],
                        color="has_availability", zoom=10, height=300,labels={"has_availability":"Room Availability"})
scattermap.update_layout(mapbox_style="carto-positron")
scattermap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#Hosts Page Data sorting
superhost=data["host_is_superhost"].value_counts()
superhostcount=pd.DataFrame({"hoststatus":superhost.keys(),"counts":superhost.values})
superhostcount=superhostcount.replace({'hoststatus':{'t':'Superhosts','f':'Hosts'}})

#plotting of bar graph on home page
graph=dbc.Col([ html.Div(dcc.Graph(id="graph"),className='card')])

#data sorting for piechart on hosts page
verifiedstatus=data["host_identity_verified"].value_counts()
verifiedstatuscount=pd.DataFrame({"verifystatus":verifiedstatus.keys(),"counts":verifiedstatus.values})
verifiedstatuscount=verifiedstatuscount.replace({'verifystatus':{'t':'Verified','f':'Not Verified'}})

#plotting of piechart
verifygraph=html.Div(dcc.Graph(figure=px.pie(verifiedstatuscount,template='plotly_white',values="counts",names="verifystatus",color="verifystatus",color_discrete_map={'Verified':'white','Not Verified':'red'}).update_layout({'font_color':'white','plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})),className='card bg-info text-white',style={'font-weight':'520'})

#plotting of bar graph on hosts page
shgraph=html.Div(dcc.Graph(figure=px.bar(superhostcount,x="hoststatus",y="counts",text_auto=True,template='plotly_white',color="hoststatus",color_discrete_map={'Hosts':'green','Superhosts':'red'}).add_annotation(x=1.2,arrowhead=2,y=10000,text="Minority of hosts are superhosts")),className='card')


#data sorting & plotting for treemap on hosts page
hostroomtype=data["room_type"].value_counts()
hostrtcount=pd.DataFrame({"Roomtype":hostroomtype.keys(),"counts":hostroomtype.values})
hostlcgraph=dcc.Graph(figure=px.treemap(hostrtcount,path=["Roomtype"],values="counts",color="Roomtype",title="Roomtype provided by hosts",template="plotly_white"))


#data sorting for table on hosts page
tabledfdata=data[["host_name","review_scores_rating"]].drop_duplicates()
#conditional mean calculation
tabledfdata=tabledfdata.groupby('host_name')["review_scores_rating"].mean()
tabledfdata=pd.DataFrame({'Host Name':tabledfdata.index,'Average Rating':tabledfdata.values}).fillna('No Reviews')








app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])





# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#00A699"
}

# the styles for the main content position it to the right of the sidebar
CONTENT_STYLE = {
    "margin-left": "16rem",
    "margin-right": "5rem",
    "padding": "2rem 1rem",
}

#content for the sidebar
sidebar = html.Div(
    [
        html.H3("Paris Airbnb Analyzer",style={"font-weight":"600","color":"white","padding-left":"30px"}),
        html.Hr(),
        html.Blockquote(
            "Airbnb Insights", className='text-light font-weight-bold', style={"padding-left":"50px"}
        ),
        #helps us navigate between two pages
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Hosts", href="/hosts", active="exact"),       
                        ],
            vertical=True,#orientation for navbar components
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE
)




content = html.Div(id="page-content",children=[] ,style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
app.title="Paris Airbnb Analyzer"


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    #content for homepage, I've used dash bootstrap components to position various elements
    if pathname == "/":
        return [
 dbc.Container([dbc.Row([dbc.Col([html.Div(id='dd-output-container',className='card'),html.Div([html.H4("Select No Of Roommates",className="font-weight-bold",style={"font-size":"20px","padding":"20px","color":"white","font-weight":"600"}),dcc.Dropdown(id='graph_dropdown',placeholder='Choose No Of Roommates',optionHeight=60,options=accomodatecount.keys(),value=0)],style={"background-color":"#00A699"},className="card")])]),
                           dbc.Row([graph]),
                           dbc.Row([html.H3("Room Availability Statistics",style={'margin-top':'20px','color':'#00A699','font-weight':'600'}),html.Div(dcc.Graph(figure=scattermap),id='card',style={'margin-top':'20px'}),html.Blockquote('(Click on legends to isolate specific information)',style={'color':'#00A699'})]),
                           dbc.Row([html.Div([html.Span(avvalues[0], style={'color':'#00A699','font-weight':'600','font-size':'30px'}), ' Airnbs Available In Paris'])],style={'margin-top':'30px'}),
                           dbc.Row([html.Div([html.Span(avvalues[1], style={'color':'red','font-weight':'600','font-size':'30px'}), ' Airnbs Unavailable In Paris'])],style={'margin-top':'30px'})
])
            
                ]
    #content for hosts page
    elif pathname == "/hosts":
        data=pd.read_csv("parislistingdata.csv")
        return [dbc.Container([dbc.Row([dbc.Col([html.H4("Hosts Vs Superhosts",style={'color':'#00A699','font-weight':'600'}),shgraph],width=6),dbc.Col([html.H4("Are all my hosts verified?",style={'color':'#00A699','font-weight':'600'}),verifygraph],width=6)]),hostlcgraph,html.H4('Sort Host By Reviews',style={'color':'#00A699','font-weight':'600'}),html.Div(dcc.Slider(0,5,value=0,id='my-slider'),className='card'),html.Div(id='table-container',style={'margin-top':'30px'})])]
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

#Callback for the table on hosts page, you can use the slider to choose between various ratings and table will be generated according to your filters
@app.callback(
    Output('table-container', 'children'),
    Input('my-slider', 'value'))
def update_table(value):
    df=tabledfdata[tabledfdata['Average Rating']==value]
    if value==0:
     return dbc.Table.from_dataframe(tabledfdata, striped=True, bordered=True, hover=True,dark=True)
    if value>0:
     return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True,dark=True)
    
#callback for the graph on home page, lets you choose a value from dropdown and a graph is created accordingly    
@app.callback(
    Output('graph', 'figure'),
    Input('graph_dropdown', 'value')
)
def update_output(value): 
    df=dataframe[dataframe["values"]==value]
    print(value)
    if value is None:
        fig=px.bar(accomodatecount,x=accomodatecount.keys(),y=accomodatecount.values,text_auto=True,template="plotly_white",color_discrete_sequence =['#00A699']*3,title="Rooms available as per no of visitors",labels={"index":"No Of Roommates","y":"No of Rooms Available"})
        return fig
    if value is not None:
        fig1 = px.bar(df,x=df["values"],y=df["count"],text_auto=True,template="plotly_white",color_discrete_sequence =['#00A699']*3,title="Rooms available as per no of visitors",labels={"values":"No Of Roommates","count":"No of Rooms Available"})
        return fig1
if __name__ == "__main__":
    app.run_server(port=8050)
