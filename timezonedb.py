import configparser
import csv
import datetime
import io
import sqlite3
import urllib.request
import zipfile

ini = configparser.ConfigParser()
ini.read('config.ini')

response = urllib.request.urlopen('http://timezonedb.com/date.txt')
tzdate = datetime.date(*[int(i) for i in response.read().decode().split('-')])

connection = sqlite3.connect(ini['DATABASE']['timezonedb'], detect_types=True)
cursor = connection.cursor()
try:
    cursor.execute('SELECT updated FROM updated')
    row = cursor.fetchone()
except:
    row = None
if row is None or tzdate > row[0]:
    with open('source/database/sqlite/timezonedb.sql', 'r') as file:
        cursor.executescript(file.read())
            
    url = 'https://timezonedb.com/files/timezonedb.csv.zip'
    response = urllib.request.urlopen(url)
    with io.BytesIO(response.read()) as zipIO:
        with zipfile.ZipFile(zipIO) as zipFile:
            with zipFile.open('zone.csv', 'r') as file:
                with io.TextIOWrapper(file) as text:
                    reader = csv.reader(text)
                    query = 'INSERT INTO zone VALUES (?, ?, ?)'
                    cursor.executemany(query, list(reader))

            with zipFile.open('timezone.csv', 'r') as file:
                with io.TextIOWrapper(file) as text:
                    reader = csv.reader(text)
                    query = 'INSERT INTO timezone VALUES (?, ?, ?, ?, ?)'
                    cursor.executemany(query, list(reader))

            with zipFile.open('country.csv', 'r') as file:
                with io.TextIOWrapper(file) as text:
                    reader = csv.reader(text)
                    query = 'INSERT INTO country VALUES (?, ?)'
                    cursor.executemany(query, list(reader))

    cursor.execute('INSERT INTO updated VALUES (?)', (tzdate,))
    print('Database has been updated')
else:
    print('Database is up to date')
cursor.close()
connection.commit()
connection.close()
