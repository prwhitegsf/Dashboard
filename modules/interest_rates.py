from openbb import obb as openbb
from sqlalchemy import MetaData, Table, Column, String, Double, inspect
import modules.db_funcs as db
import pandas as pd
from datetime import datetime
from io import StringIO
import requests

class Rates:
    def __init__(self,  engine, sig_digits=2):
        
        self.rates_folder = "data/rates"
        self.table_name = "us_treasury_yield_curve"
        self.engine = engine
        self.sig_digits = sig_digits
        self.metadata = MetaData()


        self.tbl = Table(
                self.table_name,
                self.metadata,
                Column("date", String(50), primary_key=True),
                Column("1m", Double),
                Column("3m", Double),
                Column("6m", Double),
                Column("1y", Double),
                Column("2y", Double),
                Column("3y", Double),
                Column("5y", Double),
                Column("7y", Double),
                Column("10y", Double),
                Column("20y", Double),
                Column("30y", Double),
            )
      

    def __rename_cols(self,yc):
        new_cols = ['date','1m','3m','6m','1y','2y','3y','5y','7y','10y','20y','30y']
        yc.columns = new_cols
        return yc


    def __get_local_csv(self):
        yc_fp = self.rates_folder + "/us_yc.csv"
        yc = pd.read_csv(yc_fp)

        # holiday's are listed with a price of '-', we replace that with prev day's price
        yc.replace('-', method='ffill', inplace=True)
        yc.bfill(inplace=True)
        return self.__rename_cols(yc)


    # requires the csv to initialize table
    def create_table(self):
        if inspect(self.engine).has_table(self.table_name):
            print("Table already exists. Please remove the table from the database and try again")
        else:
            db.create_table(self.engine, self.metadata)
            yc = self.__get_local_csv()
            yc.reset_index(inplace=True, drop=True)
            print(yc.head(2))
            yc.to_sql(self.table_name, con=self.engine, if_exists='append',index=False)


    def __get_curve(self, year='2024'):
        # add fucntionality to insert year into this string
        
        # Download directly from treasury site
        url='https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2024/all?type=daily_treasury_yield_curve&field_tdr_date_value=2024&page&_format=csv'
        s=requests.get(url).text
        yc=pd.read_csv(StringIO(s))

        # column and date formatting
        yc.drop(columns=['2 Mo', '4 Mo'], inplace=True)
        yc['Date'] = pd.to_datetime(yc['Date'], format='%m/%d/%Y').dt.date.astype("string")
        
        # we only want records that are newer than the ones we have
        last_date = db.get_most_recent_date(self.engine, self.tbl)
        yc =yc[yc['Date'] > last_date]
        return self.__rename_cols(yc)


    def update_table(self):
        idx = self.__get_curve()
        idx.to_sql(self.table_name, con=self.engine, if_exists='append',index=False)