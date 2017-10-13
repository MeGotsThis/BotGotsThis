from contextlib import closing
import configparser
import csv
import datetime
import io
import sqlite3
import urllib.request
import zipfile

ini = configparser.ConfigParser()
ini.read('database.ini')

response = urllib.request.urlopen('http://timezonedb.com/date.txt')
tzdate = datetime.date(*[int(i) for i in response.read().decode().split('-')])

with sqlite3.connect(
    ini['DATABASE']['timezonedb'], detect_types=True) as connection, \
        closing(connection.cursor()) as cursor:
    try:
        cursor.execute('SELECT updated FROM updated')
        lastUpdated, = cursor.fetchone()
    except Exception:
        lastUpdated = datetime.date.min
    if tzdate > lastUpdated:
        with open('lib/database/sqlite/timezonedb.sql', 'r') as file:
            cursor.executescript(file.read())
        url = 'https://timezonedb.com/files/timezonedb.csv.zip'
        with urllib.request.urlopen(url) as response, \
                io.BytesIO(response.read()) as zipIO, \
                zipfile.ZipFile(zipIO) as zipFile:
            with zipFile.open('zone.csv', 'r') as file, \
                    io.TextIOWrapper(file) as text:
                reader = csv.reader(text)
                query = 'INSERT INTO zone VALUES (?, ?, ?)'
                cursor.executemany(query, reader)
            with zipFile.open('timezone.csv', 'r') as file, \
                    io.TextIOWrapper(file) as text:
                reader = csv.reader(text)
                query = 'INSERT INTO timezone VALUES (?, ?, ?, ?, ?)'
                cursor.executemany(query, reader)
            with zipFile.open('country.csv', 'r') as file, \
                    io.TextIOWrapper(file) as text:
                reader = csv.reader(text)
                query = 'INSERT INTO country VALUES (?, ?)'
                cursor.executemany(query, reader)
        cursor.execute('INSERT INTO updated VALUES (?)', (tzdate,))
        print('Database has been updated')
    else:
        print('Database is up to date')
    connection.commit()
