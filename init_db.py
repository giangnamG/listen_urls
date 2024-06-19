import sqlite3

def run():
    con = sqlite3.connect('database.sqlite')

    '''create database'''

    con.execute('''
        create table if not exists urls (
            id integer primary key autoincrement,
            scheme text not null,
            host text not null,
            path text,
            params text,
            query text,
            fragment text,
            time text
        );            
    ''')