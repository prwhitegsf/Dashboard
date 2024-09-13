from openbb_terminal.sdk import openbb
import pandas as pd


class Rates:

    def __init__(self):
        self.rates_folder = "data/rates"


    def get_current_yc(self):
        # update yield curve
        yc_link = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2024/all?type=daily_treasury_yield_curve&field_tdr_date_value=2024&page&_format=csv'
        yc = pd.read_csv(yc_link)
        yc.drop(columns=['2 Mo', '4 Mo'], inplace=True)

        # rename columns for concatenation
        new_cols = ['Date', '1m', '3m','6m','1y','2y','3y','5y','7y','10y','20y','30y']
        yc.columns = new_cols
        yc['Date'] = pd.to_datetime(yc['Date'], format='%m/%d/%Y')

        return yc

    def update_yc(self):
        
        # gets current yields from treasury
        yc = self.get_current_yc()

        # open the historical file
        yc_fp = self.rates_folder + "/us_yc.csv"
        h_yc = pd.read_csv(yc_fp)
        h_yc['Date'] = pd.to_datetime(h_yc['Date'])

        # concat with new, sort, and dedupe
        h_yc = pd.concat([yc, h_yc], axis=0)
        h_yc.sort_values(by='Date',ascending=False, inplace=True)
        h_yc.drop_duplicates(subset='Date', keep='first', inplace=True)
        h_yc.reset_index(inplace=True, drop=True)
        # write back out to historical file
        h_yc.to_csv(yc_fp, index=False)

        # return update yc
        return h_yc

    def get_yc_deltas(self,yc):
        # gets the change in close val from prev day
        dff = yc.copy()
        dff = dff[dff['10y'] != '-']                # filter out null days
        dff.index = pd.to_datetime(dff['Date'])     # date col to index
        dff.drop(columns=['Date'], inplace=True)    # then drop date
        dff = dff.astype(float)                     # all date to floats
        col_names = dff.columns                     # loop through all columns taking the diff
        for col in col_names:
            dff[col] = dff[col].diff(periods=-1)
        # process/clean
        dff.sort_index(ascending = False, inplace=True)
        yc_dfp = self.rates_folder + "/us_yc_deltas.csv"
        dff.to_csv(yc_dfp)
        return dff

    def get_hyig(self):
        out_fp = self.rates_folder + "/hyig.csv"
        hyig = openbb.fixedincome.icebofa(data_type = "spread", category = "usd", area = "us", grade  = "high_yield", options = False)
        hyig.rename(columns={'ICE BofA US High Yield Index Option-Adjusted Spread' :'HYIG'}, inplace = True)
        hyig.to_csv(out_fp, index=True)
        return hyig.tail(2)