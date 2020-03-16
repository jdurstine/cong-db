import json
import traceback
import logging
import os
from os import path
import mysql.connector as mysql

def loadererror_insert(err_cursor, error_description, error_path):

    statement = ('INSERT INTO SystemErrors_Loader'
                 '(systemID, errorDescription, errorPath)'
                 'VALUES (%s, %s, %s);')

    values = (1, error_description, error_path)

    err_cursor.execute(statement, values)

def votes_insert(db_cursor, json_input):

    statement = ('INSERT INTO Votes'
                 '(voteID, updatedAt, type, subject, sourceURL, session, '
                 '   resultText, result, requires, question, number) '
                 'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);')

    values = (json_input['vote_id'],
              json_input['updated_at'][0:10],
              json_input['type'],
              json_input['subject'],
              json_input['source_url'],
              json_input['session'],
              json_input['result_text'],
              json_input['result'],
              json_input['requires'],
              json_input['question'],
              json_input['number'])

    db_cursor.execute(statement, values)

def congressmembers_insert(db_cursor, json_input):

    for key in json_input['votes'].keys():

        for person in json_input['votes'][key]:

            if not isinstance(person, dict):
                # quick fix, unexpected input needs to be handled better
                continue

            statement = ('INSERT INTO CongressMembers '
                         '(memberID, displayName, party, state) '
                         'VALUES (%s, %s, %s, %s);')

            values = (person['id'],
                      person['display_name'],
                      person['party'],
                      person['state'])

            try:
                db_cursor.execute(statement, values)
            except mysql.errors.IntegrityError as e:
                if e.errno == 1062:
                    # duplicate keys aren't an issue here
                    pass
                else:
                    raise

def membervotes_insert(db_cursor, json_input):

    vote_id = json_input['vote_id']

    for key in json_input['votes']:

        for person in json_input['votes'][key]:

            if not isinstance(person, dict):
                # quick fix, unexpected input needs to be handled better
                continue

            values = (vote_id, person['id'], key)

            statement = ('INSERT INTO MemberVotes (voteID, memberID, memberVote) '
                         'VALUES (%s, %s, %s);')

            db_cursor.execute(statement, values)

def load_data(username, password):

    # This log is for unhandled errors which cause the program to stop running
    logging.basicConfig(filename='importer.log')

    # Set up the main db connection and cursor
    db_connection = mysql.connect(user=username,
                                  password=password,
                                  host='localhost',
                                  database='Congress')

    db_cursor = db_connection.cursor()

    # Set up the error db connection and cursor
    err_connection = mysql.connect(user=username,
                                   password=password,
                                   host='localhost',
                                   database='CongressErrors')

    err_cursor = err_connection.cursor()

    # Path to the data we're inserting into our DB
    root_path = path.abspath('congress-scraper/data')

    for cur_path, cur_dir, files in os.walk(root_path):
        if 'data.json' in files:
            json_input = json.load(open(path.join(cur_path, 'data.json')))

            if 'subject' not in json_input:
                json_input['subject'] = ''

            try:
                # Insert into the tables, order matters for FK constraints
                votes_insert(db_cursor, json_input)
                congressmembers_insert(db_cursor, json_input)
                membervotes_insert(db_cursor, json_input)
                db_connection.commit()
                logging.info('Data from {} committed'.format(cur_path))
            except (mysql.errors.IntegrityError, mysql.errors.DataError) as e:
                loadererror_insert(err_cursor, e.args[0], cur_path)
                err_connection.commit()
                db_connection.rollback()
            except:
                # We've encountered a critical error - log error and reraise the error
                logging.warning('Error encountered committing data from {}.'.format(cur_path))
                raise

if __name__ ==  '__main__':
    config = json.load(open('config.json'))
    load_data(config['congress']['username'], config['congress']['password'])