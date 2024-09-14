from openbb import obb as openbb
from sqlalchemy import MetaData, Table, Column, String, Integer, inspect
import modules.db_funcs as db
import pandas as pd

class EconomicCalendar:
    
    def __init__(self, engine):
        self.econ_cal_folder = "data/economic_calendar"
        self.engine = engine
        self.last_updated = ''
        self.metadata = MetaData()
        self.events = Table(
            "economic_calendar",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("date", String(50)),
            Column("country", String(50)),
            Column("event", String(50)),
            Column("consensus", String(50)),
            Column("previous", String(50)),
            Column("actual", String(50)),
            Column("last_updated", String(50)),
        )
    
    def __download_historical_calendar(self, start_date, end_date,country='united_states'):
        ec = openbb.economy.calendar(provider='nasdaq',country=country,start_date=start_date, end_date=end_date).to_df()
        ec.drop(columns=['description'], inplace=True)
        ec['last_updated'] = pd.Timestamp.now()
        return ec

    def create_table(self, start_date, end_date):
   
        if inspect(self.engine).has_table('economic_calendar'):
            print("Table already exists. Please remove the table from the database and try again")
        else:
            db.create_table(self.engine, self.metadata)
            ec = self.__download_historical_calendar(start_date, end_date)
            ec.to_sql('economic_calendar', con=self.engine, if_exists='append')


    def update_table(self, end_date):

        ec = self.__download_historical_calendar(db.get_last_update_datetime(self.engine, self.events), end_date)
        db.remove_rows_since_last_updated(self.engine, self.events)
        ec.to_sql('economic_calendar', con=self.engine, if_exists='append')
        return ec.head()