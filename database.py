import sqlite3
import hashlib
import os

class database(object):
    def __init__(self,path):
        databaseExists = os.path.exists(path)
        self.conn = sqlite3.connect(path)
        if databaseExists == False:
            c = self.conn.cursor()
            c.execute('''CREATE TABLE feeds(
                urlhash text primary key,
                name    text
            )''')
            c.execute('''CREATE TABLE articles(
                articleid   integer primary key autoincrement,
                feed        text,
                url         text unique,
                title       text,
                content     text,
                pubdatetime text,
                viewed      integer,
                FOREIGN KEY (feed) REFERENCES feeds(urlhash)
            )''')
            c.execute('''CREATE TABLE simplerss(
                name    text primary key,
                value   text
            )''');
            c.execute("INSERT INTO simplerss VALUES (?,?)",('version','0.1'));
            self.conn.commit()

    def getFeedInfo(self,url):
        c = self.conn.cursor()
        md5url=hashlib.md5(url.encode('utf-8')).hexdigest()
        c.execute("SELECT name FROM feeds WHERE urlhash = '{0}'".format(md5url))
        name = c.fetchone()
        if (name == None):
            return url,0,0

        c.execute("SELECT COUNT(*) FROM articles WHERE feed = ?",(md5url,))
        articlesTotal = int(c.fetchone()[0])
        c.execute("SELECT COUNT(*) FROM articles WHERE feed = ? AND viewed = 0",(md5url,))
        articlesNotRead = int(c.fetchone()[0])
        return name[0],articlesTotal,articlesNotRead

    def addFeed(self,url,name):
        try:
            c = self.conn.cursor()
            md5url=hashlib.md5(url.encode('utf-8')).hexdigest()
            c.execute("INSERT INTO feeds VALUES(?,?)",(md5url,name,))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            pass
        return

    def addArticle(self,feedurl, url, title, content, pubdatetime):
        try:
            c = self.conn.cursor()
            md5feedUrl=hashlib.md5(feedurl.encode('utf-8')).hexdigest()
            c.execute("INSERT INTO articles(feed,url,title,content,pubdatetime,viewed) VALUES (?,?,?,?,?,?)", (md5feedUrl,url,title,content,pubdatetime,0))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            pass
        return

    def getArticles(self, feedurl):
        c = self.conn.cursor()
        md5feedUrl=hashlib.md5(feedurl.encode('utf-8')).hexdigest()
        c.execute("SELECT * FROM articles WHERE feed = ? ORDER BY pubdatetime DESC",(md5feedUrl,))
        articleList = c.fetchall()
        return articleList

    def setArticleViewed(self, articleurl, viewed = 1):
        c = self.conn.cursor()
        c.execute("UPDATE articles SET viewed = ? WHERE url = ?", (viewed, articleurl))
        self.conn.commit()
        return

    def setFeedViewed(self, feedurl, viewed = 1):
        c = self.conn.cursor()
        md5feedUrl=hashlib.md5(feedurl.encode('utf-8')).hexdigest()
        c.execute("UPDATE articles SET viewed = ? WHERE feed = ?", (viewed, md5feedUrl))
        self.conn.commit()

    def setAllViewed(self, viewed = 1):
        c = self.conn.cursor()
        c.execute("UPDATE articles SET viewed = ?", (viewed,))
        self.conn.commit()
#
#databaseTest = database('/home/bruno/.cursesrss/database.db3')
#url = 'http://www.archlinux.org/feed/news/'
#databaseTest.addFeed(url,"Arch Linux")
#print(databaseTest.getFeedInfo(url))
