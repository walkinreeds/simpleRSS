import sqlite3
import os

class database(object):
    def __init__(self,path):
        databaseExists = os.path.exists(path)
        conn = sqlite3.connect(path)
        self.c = conn.cursor()
        if databaseExists == False:
            self.c.execute('''CREATE TABLE feeds(
                urlhash text primary key,
                name    text
            )''')
            self.c.execute('''CREATE TABLE articles(
                articleid   integer primary key autoincrement,
                feed        text,
                url         text unique,
                title       text,
                content     text,
                pubdatetime text,
                viewed      integer,
                FOREIGN KEY (feed) REFERENCES feeds(urlhash)
            )''')

    def getFeedInfo(self,url):
        self.c.execute("SELECT name FROM feeds WHERE urlhash = '{0}'".format(hash(url)))
        name = self.c.fetchone()
        if (name == None):
            return ""
        return ""

    def addFeed(self,url,name):
        self.c.execute("INSERT INTO feeds VALUES '{0}','{1}'".format(hash(url),name))

#
databaseTest = database('/home/bruno/.cursesrss/database.db3')
databaseTest.getFeedInfo('http://www.archlinux.org/feed/news/')
