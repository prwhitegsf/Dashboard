# Import packages
from openbb import obb as openbb
from datetime import date, datetime
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine


class ChartController:

    def __init__(self):
        pass

    # drop the index so that it plays nice with
    def drop_index(self, df):
        df['date'] = df.index
        df.reset_index(drop=True, inplace=True)
        return df

    def get_obb_indices(self, ticker, start_date, end_date):
        df = openbb.index.price.historical(symbol=ticker, provider='yfinance',start_date=start_date, end_date=end_date).to_df().round(2)
        return self.drop_index(df)

    def get_obb_equities(self,ticker, start_date, end_date):
        df = openbb.equity.price.historical(symbol=ticker,start_date=start_date, end_date=end_date, provider='yfinance').to_df().round(2)
        return self.drop_index(df)
            
    def get_obb_series(self, type='equities', ticker='SPY', start_date='2019-01-01', end_date =datetime.today().strftime('%Y-%m-%d')):

        if type == "price_index":
            return self.get_obb_indices(ticker, start_date, end_date)
        else:
            return self.get_obb_equities(ticker, start_date, end_date)



cc = ChartController()


engine = create_engine('postgresql+psycopg2://postgres:password@localhost/vol_event_db', future=True)
ec = pd.read_sql_table('economic_calendar', engine, columns=['date','event','consensus','previous','actual'])
ec.sort_values(by=['date'], ascending=False, inplace=True)



app = Dash(__name__)

app.layout = html.Div(children=[
    html.P(html.H4('Upcoming Data Releases'), style={'font-family':'sans-serif'}),
    html.Div(
    dash_table.DataTable(data=ec.to_dict('records'), page_size=10), 
    style={'width' : 800}),
    
    html.Div([
    html.Div(children=[
        html.Div("Select Series", style={'padding-right':  40, 'padding-left': 20, 'font-family':'sans-serif', 'text-align': 'center'}),
        html.Div(
        dcc.Dropdown(
            id="series-type",
            options=['index', 'equities'],
            value='equities',
            clearable=False,
            style={'width' : 100}
        ), style={'padding-right':  40, 'padding-left': 20, 'font-family':'sans-serif', 'align': 'center'})]), 
    
    
   
    html.Div(children=[
    html.Div("Enter Ticker", style={'padding-right':  40, 'padding-left': 20, 'font-family':'sans-serif', 'text-align': 'center'}),
    html.Div(dcc.Input(id="ticker", type="text", placeholder="SPY", debounce=True, style={'marginRight':'10px', 'padding-right':  40, 'padding-left': 20, 'font-family':'sans-serif', 'text-align': 'center'}))
    ]),
    html.Div(children=[
    html.Div("Select Date Range", style={'padding-right':  40, 'padding-left': 20, 'font-family':'sans-serif', 'text-align': 'center'}),
    html.Div([
    html.Div(
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2024, 9, 19),
        initial_visible_month=date(2019, 1, 1),
        start_date=date(2019, 1, 1),
        end_date=date(2024, 9, 14)
    ), style={'padding-right':  40, 'padding-left': 20, 'font-family':'sans-serif', 'align': 'center', 'font-size': 12}),
    html.Div(id='output-container-date-picker-range')
    ])
    ])
    ], style={'display': 'flex', 'flexDirection': 'row'}),

    html.Div(
    dcc.Graph(id="time-series-chart"),
    style={'width' : 800})
])


@app.callback(
    Output("time-series-chart", "figure"), 
    Input("series-type", "value"),
    Input("ticker", "value"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
    
)
    

def display_time_series(type, ticker, start, end):
   
  
    df = cc.get_obb_series(type, ticker, start, end)
    fig = px.line(df, x='date', y='close')
    return fig


app.run_server(debug=True)