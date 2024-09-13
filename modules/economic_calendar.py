from openbb_terminal.sdk import openbb
from datetime import datetime, date, timedelta
import pandas as pd

class EconomicCalendar:
    
    def __init__(self):
        self.econ_cal_folder = "data/economic_calendar"

    def get_upcoming_full_econ_cal(self,num_days):  
        curr_day = date.today().strftime('%Y-%m-%d')
        end_date = (date.today() + timedelta(days=num_days)).strftime('%Y-%m-%d')
        upcoming_ecal = openbb.economy.events("united_states",start_date= curr_day, end_date=end_date)
        upcoming_ecal.to_csv(self.econ_cal_folder + '/upcoming_full_ecal.csv', index=False)
        return upcoming_ecal.tail(2) 

    def get_recent_full_econ_cal(self,num_days):
        end_date = date.today().strftime('%Y-%m-%d')
        curr_day = (date.today() - timedelta(days=num_days)).strftime('%Y-%m-%d')
        df = openbb.economy.events("united_states",start_date= curr_day, end_date=end_date)
        df.to_csv(self.econ_cal_folder + '\\recent_full_ecal.csv', index=False)
        return df.tail(2)

    def concat_full_ecal(self):
        full = pd.read_csv(self.econ_cal_folder + '\\full_econ_cal.csv')
        upd = pd.read_csv(self.econ_cal_folder + '\\recent_full_ecal.csv')
        full = pd.concat([full, upd], ignore_index=False)
        full.drop_duplicates(subset=["Date",'Event'], inplace=True)
        full  = full.loc[:,~full.columns.str.contains('^Unnamed')]
        full.to_csv(self.econ_cal_folder + '\\full_econ_cal.csv', index=False)
        return full.tail(2)

    def filter_full_ecal(self):
        upd = pd.read_csv(self.econ_cal_folder + '\\full_econ_cal.csv')
        ecal_event_filter = pd.read_csv(self.econ_cal_folder+ '\\econ_event_list.csv')
        ecal_filter = ecal_event_filter['Event'].to_list()
        filtered_ecal = upd[upd['Event'].isin(ecal_filter)].copy()

    # add codes, it's happier when this already has values

        filtered_ecal['code'] = range(len(filtered_ecal))

        i = 0
        for event in filtered_ecal['Event']:
            # throws warnings about chained assignment/returning a view vs a copy
            # should use format :  filtered_ecal.iat[coe_column_index, i]
            filtered_ecal['code'].iloc[i] = ecal_event_filter[ecal_event_filter['Event'] == event][' Code']
            i = i + 1

        # clean it up
        firstcol = filtered_ecal.pop('Date')
        filtered_ecal.insert(0, 'Date', firstcol)
        filtered_ecal.to_csv(self.econ_cal_folder + '\\filtered_econ_cal.csv', index=False)
        return filtered_ecal.tail(2)

    def filter_update_ecal(self):
        upd = pd.read_csv(self.econ_cal_folder + '\\recent_full_ecal.csv')
        ecal_event_filter = pd.read_csv(self.econ_cal_folder + '\\econ_event_list.csv')
        ecal_filter = ecal_event_filter['Event'].to_list()
        filtered_ecal = upd[upd['Event'].isin(ecal_filter)].copy()

    # add codes, it's happier when this already has values

        filtered_ecal['code'] = range(len(filtered_ecal))

        i = 0
        for event in filtered_ecal['Event']:
            # throws warnings about chained assignment/returning a view vs a copy
            # don't quite understand how to fix yet, but data looks correct so, until then
            filtered_ecal['code'].iloc[i] = ecal_event_filter[ecal_event_filter['Event'] == event][' Code']
            i = i + 1

        # clean it up
        firstcol = filtered_ecal.pop('Date')
        filtered_ecal.insert(0, 'Date', firstcol)
        return filtered_ecal.tail(2)

    def update_filtered_ecal(self):
        full = pd.read_csv(self.econ_cal_folder + '\\filtered_econ_cal.csv')
        upd = self.filter_update_ecal()
        full = pd.concat([full, upd], ignore_index=False)
        full.drop_duplicates(subset=["Date",'Event'], inplace=True)
        
        full.to_csv(self.econ_cal_folder + '\\filtered_econ_cal.csv', index=False)
        return full.tail(2)

    def group_ecal_by_date(self):
        filtered_ecal_fp = self.econ_cal_folder + 'filtered_econ_cal.csv'
        df = pd.read_csv(filtered_ecal_fp, usecols=['Date', 'Event'])

        return df.groupby('Date')['Event'].apply(list)