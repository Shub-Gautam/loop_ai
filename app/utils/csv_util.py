import secrets
import string
import asyncio
import pandas as pd
from pathlib import Path
import app.utils.time_util as util
from datetime import datetime, timedelta, timezone
import pytz
import csv
import sqlite3 as sql
import os
import pathlib

curr_dir = os.path.dirname(pathlib.Path().resolve())
dbSource = os.path.join(curr_dir,"loop","instance","StoreDatabase.db")

def gen_report_id() -> str:
    length = 7
    characters = string.ascii_uppercase
    random_str = ''.join(secrets.choice(characters) for _ in range(length))
    return random_str

def generate_report(report_id: str, report_df) -> None:
    _df = pd.DataFrame(report_df)
    filepath = Path(f'./generated_csv/{report_id}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    _df.to_csv(filepath)

def get_set_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if e.args[0].startswith('There is no current event loop'):
            asyncio.set_event_loop(asyncio.new_event_loop())
            return asyncio.get_event_loop()
        raise e


timestamp_fmt = '%Y-%m-%d %H:%M:%S.%f %Z'  # 2023-01-24 09:08:23.138922 UTC
bussinesshours_fmt = '%H:%M:%S'
sortableTimestamp_fmt = '%Y%m%d%H%M%S'
time_fmt = '%H%M%S'

def generate_report(report_id,limit=3000000):
    report_fields = ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour',
                     'downtime_last_day', 'downtime_last_week']
    report_rows = []
    print("loop starting")
    print("limit")
    print(limit)
    with sql.connect(dbSource) as con:
        con.row_factory = sql.Row
        con.create_function('getDayOfWeek', 1, util.get_dayOfWeek)
        con.create_function('getTime', 1, util.getTime)
        con.create_function('getSortableTime', 1, util.getSortableTime)
        cur = con.cursor()
        cur.execute("select * from StoreTimezones")
        stores = cur.fetchall();
        count = 1
        for store in stores:
            try:
                #  get store times and convert to UTC
                if count == limit:
                    break
                count += 1
                print(count)
                print("===============")
                print(store['store_id'])
                storeTimes = cur.execute(
                    "select * from StoreHours WHERE store_id = {}".format(store['store_id'])).fetchall()
                startTimePerDay = [None, None, None, None, None, None, None]
                endTimePerDay = [None, None, None, None, None, None, None]
                store_timezone = store['timezone_str'] if store['timezone_str'] != '' else 'America/Chicago'
                for day in storeTimes:
                    startTime_local_str = datetime.strptime(day['start_time_local'], bussinesshours_fmt)
                    startTimelocal = pytz.timezone(store_timezone).localize(startTime_local_str, is_dst=None)
                    endTime_local_str = datetime.strptime(day['end_time_local'], bussinesshours_fmt)
                    endTimelocal = pytz.timezone(store_timezone).localize(endTime_local_str, is_dst=None)
                    startTime = int(startTimelocal.astimezone(timezone.utc).strftime(time_fmt))
                    endTime = int(endTimelocal.astimezone(timezone.utc).strftime(time_fmt))
                    if startTime < endTime:
                        startTimePerDay[int(day['day'])] = startTime
                        endTimePerDay[int(day['day'])] = endTime
                    else:
                        startTimePerDay[int(day['day'])] = endTime
                        endTimePerDay[int(day['day'])] = startTime

                if len(storeTimes) == 0:
                    startTimePerDay = [000000, 000000, 000000, 000000, 000000, 000000, 000000]
                    endTimePerDay = [246060, 246060, 246060, 246060, 246060, 246060, 246060]
                for i in range(0, 7):  # closed
                    if startTimePerDay[i] is None:
                        startTimePerDay[i] = 000000
                        endTimePerDay[i] = 000000

                # print(startTimePerDay)
                # print(endTimePerDay)

                query1 = """
                    SELECT timestamp_utc, getDayOfWeek(timestamp_utc) AS day, getTime(timestamp_utc) AS time, status
                    FROM StoreStatus WHERE store_id = {} 
                    ORDER BY timestamp_utc ASC
                """.format(store['store_id'])
                # next day end Time???

                query2 = """
                    SELECT getSortableTime(timestamp_utc) AS timestamp_utc, status
                    FROM ({}) 
                    WHERE 
                        (time >= {} AND time <= {} AND day = 0) 
                        OR (time >= {} AND time <= {} AND day = 1) 
                        OR (time >= {} AND time <= {} AND day = 2) 
                        OR (time >= {} AND time <= {} AND day = 3) 
                        OR (time >= {} AND time <= {} AND day = 4) 
                        OR (time >= {} AND time <= {} AND day = 5) 
                        OR (time >= {} AND time <= {} AND day = 6) 
                """.format(query1, startTimePerDay[0], endTimePerDay[0],
                           startTimePerDay[1], endTimePerDay[1],
                           startTimePerDay[2], endTimePerDay[2],
                           startTimePerDay[3], endTimePerDay[3],
                           startTimePerDay[4], endTimePerDay[4],
                           startTimePerDay[5], endTimePerDay[5],
                           startTimePerDay[6], endTimePerDay[6])

                lastTimestampQuery = """
                    SELECT MAX(timestamp_utc) AS timestamp
                    FROM ({})
                """.format(query2)

                # calculate uptime in minutes past hour, past day, past week
                lastTimestamp = cur.execute(lastTimestampQuery).fetchone()['timestamp']
                print(lastTimestamp)
                if lastTimestamp is None:
                    continue
                lastTimestampDatetime = datetime.strptime(lastTimestamp, sortableTimestamp_fmt)
                oneHourBack = timedelta(hours=-1)
                oneDayBack = timedelta(days=-1)
                oneWeekBack = timedelta(weeks=-1)
                onehourbackTimestamp = lastTimestampDatetime + oneHourBack
                onedaybackTimestamp = lastTimestampDatetime + oneDayBack
                oneWeekbackTimestamp = lastTimestampDatetime + oneWeekBack

                businessTimestampsPastHour = cur.execute("""
                    SELECT timestamp_utc, status
                    FROM ({})
                    WHERE (timestamp_utc >= '{}' AND timestamp_utc <= '{}')""".format(query2,
                                                                                      onehourbackTimestamp.strftime(
                                                                                          sortableTimestamp_fmt),
                                                                                      lastTimestamp)).fetchall()

                businessTimestampsPastDay = cur.execute("""
                    SELECT timestamp_utc, status
                    FROM ({})
                    WHERE (timestamp_utc >= '{}' AND timestamp_utc <= '{}')""".format(query2,
                                                                                      onedaybackTimestamp.strftime(
                                                                                          sortableTimestamp_fmt),
                                                                                      lastTimestamp)).fetchall()
                businessTimestampsPastWeek = cur.execute("""
                    SELECT timestamp_utc, status
                    FROM ({})
                    WHERE (timestamp_utc >= '{}' AND timestamp_utc <= '{}')""".format(query2,
                                                                                      oneWeekbackTimestamp.strftime(
                                                                                          sortableTimestamp_fmt),
                                                                                      lastTimestamp)).fetchall()

                uptime_PastHour, downtime_PastHour = util.getUptime(businessTimestampsPastHour)
                uptime_PastDay, downtime_PastDay = util.getUptime(businessTimestampsPastDay)
                uptime_PastWeek, downtime_PastWeek = util.getUptime(businessTimestampsPastWeek)

                report_rows.append(
                    [store['store_id'], uptime_PastHour, uptime_PastDay, uptime_PastWeek, downtime_PastHour,
                     downtime_PastDay, downtime_PastWeek])
            except:
                print("exception")

        print("saving file")

        # save CSV
        with open(f'{os.path.join(curr_dir,"loop","generated_csv",f"{report_id}.csv")}', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(report_fields)
            writer.writerows(report_rows)

        cur.execute("UPDATE ReportStatus SET status = '{}' WHERE reportId = '{}'".format("completed", str(report_id)))
        con.commit()