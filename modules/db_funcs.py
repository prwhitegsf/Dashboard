from datetime import datetime, date, timedelta
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy import select, func, and_
import pandas as pd

def create_table(engine, metadata):
    with engine.begin() as conn:
         metadata.create_all(conn)


def get_last_update_datetime(engine, table):
    with engine.connect() as connection:
        select_stmt = select(func.max(table.c.last_updated))
        result = connection.execute(select_stmt)
        return result.one()[0].split(' ')[0]

def get_most_recent_date(engine, table):
    with engine.connect() as connection:
        select_stmt = select(func.max(table.c.date))
        result = connection.execute(select_stmt)
        return result.one()[0].split(' ')[0]

def remove_rows_since_last_updated(engine, table):
    with engine.begin() as connection:
        delete_stmt = (table.delete().where(table.c.date >= table.c.last_updated))
        connection.execute(delete_stmt)

def remove_most_recent_day(engine, table, most_recent_day):
    with engine.begin() as connection:
        delete_stmt = (table.delete().where(table.c.date == most_recent_day))
        connection.execute(delete_stmt)
