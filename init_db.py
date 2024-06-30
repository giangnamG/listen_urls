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
    con.execute('''
        create table if not exists strings (
            id integer primary key autoincrement,
            string text,
            time text
        );            
    ''')
    con.execute('''
        create table if not exists payloads (
            id integer primary key autoincrement,
            code_identifier integer not null,
            payload text not null,
            time text
        )
    ''')
    con.close()

def reset_db():
    con = sqlite3.connect('database.sqlite')
    con.execute('delete from urls')
    con.execute('delete from strings')
    con.commit()
    con.close()