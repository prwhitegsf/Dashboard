
from datetime import datetime
import pandas as pd
from openbb import obb as openbb

class FedFunds:

    def __init__(self):
        self.ff_current_folder = "data/fed_funds/current"
        self.ff_historical_folder = "data/fed_funds/historical"

    def get_expiry_list(self,num_expiry_months):
        expiries = []
        for i in range(num_expiry_months):
            date = datetime.now() + pd.DateOffset(months=i)
            expiries.append(date.strftime('%Y-%m'))
        return expiries

    def get_ff(self,num_expiry_months, months):
        start_date = (datetime.now() - pd.DateOffset(months=months)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        expiries = self.get_expiry_list(num_expiry_months)

        # load current front month data into df, do this to seed our full dataframe
        ff = openbb.futures.historical(symbols=['ZQ'], expiry= expiries[0], start_date=start_date, end_date=end_date)

        # then we load each expiry
        # get the close data
        # rename the column for the expiry
        # then merge
        for expiry in expiries:
            #print(type(expiry))
            nff = openbb.futures.historical(symbols=['ZQ'], expiry= expiry, start_date=start_date, end_date=end_date)
            nff.rename(columns={'Close' : expiry}, inplace=True)
            nff.drop(columns=['Open', 'High', 'Low','Adj Close', 'Volume'], inplace=True)
            ff = pd.merge(ff, nff, how='outer', on='Date')

        # process/clean merged dataframe
        ff.drop(columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'], inplace=True)
        ff.sort_index(ascending = False, inplace=True)

        # write out to csv
        f_name_curr = self.ff_current_folder+ '/ff_curve' + '.csv'
        f_name_hist =  self.ff_historical_folder + '/ff_curve_' + end_date + '.csv'
        ff = ff.round(3)
        ff.to_csv(f_name_curr)
        ff.to_csv(f_name_hist)
        return ff
    

    def get_ff_deltas(self,ff):
        # gets the change in close val from prev day
        dff = ff.copy()
        col_names = dff.columns
        for col in col_names:
            dff[col] = dff[col].diff(periods=-1)
        # process/clean
        dff.sort_index(ascending = False, inplace=True)
        f_name_curr = self.ff_current_folder + '/ff_deltas' + '.csv'
        dff.to_csv(f_name_curr)
        return dff