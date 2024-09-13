from openbb_terminal.sdk import openbb
from datetime import datetime, date, timedelta
import pandas as pd

class Indices:

    def __init__(self):
        
        self.indices_folder = "data/indices"

    def get_index(self, symbol):
        sym = '^'+symbol
        df = openbb.stocks.load(symbol=sym, interval = 1440, start_date='2019-01-01')
        df.drop(columns=['Stock Splits', 'Dividends','Volume', 'Adj Close'], inplace=True)
        df.rename(columns={'Open': (symbol + '_Open'), 'High': (symbol+'_High'), 'Low': (symbol+'_Low'),'Close': (symbol+'_Close')}, inplace=True)
        return df

    def get_indices(self):
       
        vix = self.get_index('VIX')
        move = self.get_index('MOVE')
        skew = self.get_index('SKEW')
        spx = self.get_index('SPX')


        vix.to_csv(self.indices_folder + '/vix.csv', index=True)
        move.to_csv(self.indices_folder + '/move.csv', index=True)
        skew.to_csv(self.indices_folder + '/skew.csv', index=True)
        spx.to_csv(self.indices_folder + '/spx.csv', index=True)

        return vix.tail(2)