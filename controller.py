import datetime
import time as ptime
import json
import subprocess
import importer
import mysql.connector as mysql
from datetime import datetime, date, time, timedelta


def run_today(db_cursor):

    last_run_datetime = max_batch_date(db_cursor)

    if last_run_datetime.date() == date.today():
        return True
    else:
        return False


def insert_batch(db_cursor, executed_dt, outcome):

    statement = ('INSERT INTO BatchControl '
                 '(executedDT, outcome) '
                 'VALUES (%s, %s)')

    values = (executed_dt, outcome)

    db_cursor.execute(statement, values)


def max_batch_date(db_cursor):

    statement = ('SELECT max(executedDT) '
                 'FROM BatchControl')

    db_cursor.execute(statement)

    return db_cursor.fetchone()[0]


def define_next_runtime(schedule_data, schedule_increment=timedelta()):

    schedule_date = date.today()
    schedule_time = time(hour=schedule_data['hour'], minute=schedule_data['minute'])
    schedule_datetime = datetime.combine(schedule_date, schedule_time) + schedule_increment

    return schedule_datetime


def run_controller(force_run = False):

    config = json.load(open('config.json'))
    username = config['congress']['username']
    password = config['congress']['password']
    schedule_data = config['runtime']

    db_connection = mysql.connect(user=username,
                                  password=password,
                                  host='localhost',
                                  database='Congress')

    db_cursor = db_connection.cursor()

    # Update when nothing available
    print('Checking for existing data.')
    if max_batch_date(db_cursor) is None:

        print('Triggering initial congress data pull.')
        args = ['/home/python/.virtualenvs/congress-scraper/bin/python',
                '/home/python/Documents/cong-db/congress-scraper/run',
                'votes']
        subprocess.run(args, cwd='/home/python/Documents/cong-db/congress-scraper/')

        print('Starting initial data import.')
        importer.load_data(username, password)

        print('Logging successful batch.')
        insert_batch(db_cursor, datetime.now(), 1)
        db_connection.commit()

    # Initiate the schedule
    scheduled_runtime = define_next_runtime(schedule_data)
    if datetime.now() >= scheduled_runtime or run_today(db_cursor):
        scheduled_runtime = define_next_runtime(schedule_data)

    while True:

        print('Checking for scheduled run.')
        if scheduled_runtime >= datetime.now() or force_run is True:

            print('Triggering congress data pull.')
            args = ['/home/python/.virtualenvs/congress-scraper/bin/python',
                    '/home/python/Documents/cong-db/congress-scraper/run',
                    'votes',
                    '--fast']
            subprocess.run(args, cwd='/home/python/Documents/cong-db/congress-scraper/')

            print('Starting modified data import process.')
            importer.load_data(username,
                               password,
                               load_type='modified',
                               cutoff_date=max_batch_date(db_cursor) - timedelta(days=3))

            print('Logging successful batch.')
            insert_batch(db_cursor, datetime.now(), 1)
            db_connection.commit()

            print('Setting next scheduled runtime.')
            scheduled_runtime = define_next_runtime(schedule_data, schedule_increment=timedelta(days=1))

        print('Sleeping.')
        ptime.sleep(5*60)


if __name__ == '__main__':

    run_controller(force_run=False)