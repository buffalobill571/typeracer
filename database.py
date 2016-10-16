## Hello World

import sqlite3
SELECT = "SELECT name, password FROM users WHERE name = ?"
INSERT = "INSERT INTO users (name, password) VALUES (?, ?)"
ALL = "SELECT * FROM users"
NAME = "SELECT name FROM users"
DELETE = "DELETE FROM users WHERE name=?"


def selectbyname(name, password):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(SELECT, (name,))
    tup = cur.fetchone()
    db.close()
    if tup is None:
        return False
    if tup[0] == name and tup[1] == password:
        return True
    else:
        return False


def insertuser(name, password):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(INSERT, (name, password))
    db.commit()
    db.close()


def selectall():
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(NAME)
    tup = cur.fetchall()
    db.close()
    return tup


def deletebyname(name):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute(DELETE, (name,))
    db.commit()
    db.close()
