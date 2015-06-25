#gets rss feeds and manages the database
import feedparser

class rss(object):
    def getFeed(self,url):
        d = feedparser.parse(url)
        return d.feed.title, d.entries
