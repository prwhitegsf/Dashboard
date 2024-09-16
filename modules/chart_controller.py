from openbb import obb as openbb
from datetime import datetime

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