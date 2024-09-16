from openbb import obb as openbb
from sqlalchemy import MetaData, Table, Column, String, Double, inspect
import modules.db_funcs as db
import pandas as pd
from datetime import datetime

class PriceIndex:

    def __init__(self, symbol, engine, sig_digits=2):
        
        self.indices_folder = "data/indices"
        self.table_name = symbol.lower()
        self.ticker = "^"+symbol
        self.engine = engine
        self.sig_digits = sig_digits
        self.metadata = MetaData()
        self.tbl = Table(
                self.table_name,
                self.metadata,
                Column("date", String(50), primary_key=True),
                Column("open", Double),
                Column("high",  Double),
                Column("low", Double),
                Column("close",  Double),
                Column("volume",  Double),
            )
      

    def __get_index(self, symbol, start_date, end_date):
      
        return openbb.index.price.historical(symbol=symbol, provider='yfinance',start_date=start_date, end_date=end_date).to_df().round(self.sig_digits)

    def update_table(self, end_date = datetime.today().strftime('%Y-%m-%d')):
        last_date = db.get_most_recent_date(self.engine, self.tbl)
        db.remove_most_recent_day(self.engine, self.tbl,last_date)
        idx = self.__get_index(self.ticker, last_date,end_date)
        idx.to_sql(self.table_name, con=self.engine, if_exists='append')  

    def create_table(self, start_date, end_date = datetime.today().strftime('%Y-%m-%d')):
        if inspect(self.engine).has_table(self.table_name):
            self.update_table(end_date)
        else:
            db.create_table(self.engine, self.metadata)
            idx = self.__get_index(self.ticker, start_date, end_date)
            idx.to_sql(self.table_name, con=self.engine, if_exists='append')


    
        