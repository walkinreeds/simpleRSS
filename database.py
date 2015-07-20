import sqlite3
import hashlib
import os

class database(object):
    def __init__(self,path,currentVersion):
        databaseExists = os.path.exists(path)
        self.conn = sqlite3.connect(path)
        if databaseExists == False:
            c = self.conn.cursor()
            c.execute('''CREATE TABLE feeds(
                urlhash text primary key,
                name    text,
                error   integer DEFAULT 0
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
            self.setValue('version',str(currentVersion))
        else:
            version = self.getValue('version');
            if version != None:
                version = float(version);
                if version < currentVersion:
                   self.databaseUpgrade(version)


    def databaseUpgrade(self, version):
        """
        Upgrade old database to be compatible with the current version.
        """
        c = self.conn.cursor()
        if version <= 0.1:
            c.execute("ALTER TABLE feeds ADD error integer DEFAULT 0")
            c.execute("UPDATE feeds SET error=0;")

        del c;
        self.setValue('version',str(version))
        return

    def getValue(self, name):
        """
        Gets a value from simplerss table
        """
        c = self.conn.cursor()
        c.execute("SELECT value FROM simplerss WHERE name = ?",(name,))
        value = c.fetchone()
        if (value == None):
            return None
        elif (len(value) > 0):
            return value[0]
        else:
            return None

    def setValue(self, name, value):
        """
        Creates/Sets a value in simplerss table
        """
        c = self.conn.cursor()
        if (self.getValue(name) == None):
            c.execute("INSERT INTO simplerss VALUES (?, ?)", (name, value));
        else:
            c.execute("UPDATE simplerss SET value = ? WHERE name = ?", (value,name));
        self.conn.commit()
        return

    def getFeedInfo(self,url):
        c = self.conn.cursor()
        md5url=hashlib.md5(url.encode('utf-8')).hexdigest()
        c.execute("SELECT name,error FROM feeds WHERE urlhash = '{0}'".format(md5url))
        name = c.fetchone()
        if (name == None):
            return url,0,0,0

        c.execute("SELECT COUNT(*) FROM articles WHERE feed = ?",(md5url,))
        articlesTotal = int(c.fetchone()[0])
        c.execute("SELECT COUNT(*) FROM articles WHERE feed = ? AND viewed = 0",(md5url,))
        articlesNotRead = int(c.fetchone()[0])
        return name[0],articlesTotal,articlesNotRead,name[1]

    def addFeed(self,url,name,error=0):
        try:
            c = self.conn.cursor()
            md5url=hashlib.md5(url.encode('utf-8')).hexdigest()
            c.execute("SELECT name FROM feeds WHERE urlhash = ?",(md5url,))
            feeds = c.fetchall()
            if len(feeds) == 0 and error == 1:
                #invalid feed not in database
                return
            elif len(feeds) == 0 and error == 0:
                #valid new feed
                c.execute("INSERT INTO feeds VALUES(?,?)",(md5url,name,))
            elif len(feeds) > 0 and error == 0:
                #existant feed no errors
                c.execute("UPDATE feeds SET name = ?, error = ? WHERE urlhash = ?", (name, error, md5url))
            elif len(feeds) > 0 and error == 1:
                #existant feed, error
                c.execute("UPDATE feeds SET error = ? WHERE urlhash = ?", (error, md5url))

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


if __name__ == '__main__':
    db = database('/home/bruno/.simplerss/database.db3',0.2)
    db.databaseUpgrade(0.2)
    pass
