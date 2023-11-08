from datetime import datetime, time, timedelta

timestamp_fmt = '%Y-%m-%d %H:%M:%S.%f %Z'  # 2023-01-24 09:08:23.138922 UTC
bussinesshours_fmt = '%H:%M:%S'
sortableTimestamp_fmt = '%Y%m%d%H%M%S'
time_fmt = '%H%M%S'

def getUptime(businessTimestamps):
    uptime = timedelta()
    downtime = timedelta()
    lastActivetime = datetime.strptime(businessTimestamps[0]['timestamp_utc'], sortableTimestamp_fmt)
    lastInactivetime = datetime.strptime(businessTimestamps[0]['timestamp_utc'], sortableTimestamp_fmt)
    timestampDateTime = datetime(1000, 1, 1)
    storeActive = True
    for timestamp in businessTimestamps:
        timestampDateTime = datetime.strptime(timestamp['timestamp_utc'], sortableTimestamp_fmt)
        # update uptime and downtime when status switches
        if timestamp['status'] == 'inactive' and storeActive:
            lastActivetime = timestampDateTime
            uptime += timestampDateTime - lastInactivetime
        elif timestamp['status'] == 'active' and not storeActive:
            lastInactivetime = timestampDateTime
            downtime += timestampDateTime - lastActivetime

        if timestamp['status'] == 'active':
            storeActive = True
        elif timestamp['status'] == 'inactive':
            storeActive = False

    # Add final status time block
    if storeActive:
        uptime += timestampDateTime - lastInactivetime
    else:
        downtime += timestampDateTime - lastActivetime
    uptime_in_seconds = uptime.total_seconds()
    uptime_in_minutes = round(uptime_in_seconds / 60)
    downtime_in_seconds = uptime.total_seconds()
    downtime_in_minutes = round(downtime_in_seconds / 60)
    return uptime_in_minutes, downtime_in_minutes


def get_dayOfWeek(timestamp):
    datetime_obj = datetime.strptime(timestamp, timestamp_fmt)
    return datetime_obj.weekday()


def getTime(timestamp):
    datetime_obj = datetime.strptime(timestamp, timestamp_fmt)
    return int(datetime_obj.strftime(time_fmt))


def getSortableTime(timestamp):
    datetime_obj = datetime.strptime(timestamp, timestamp_fmt)
    return datetime_obj.strftime(sortableTimestamp_fmt)
