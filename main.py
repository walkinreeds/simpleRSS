from screen import screen
from rssget import rss
from database import database
import os

class mainprogram(object):
    def __init__(self):
        #intantiate classes
        configpath = self.getConfigPath()
        self.database = database(os.path.join(configpath,'database.db3'))
        self.screen = screen()
        self.rssworker = rss()

        self.screen.showInterface(0);
        #mainloop
        while(1):
            urllist, namelist = self.getFeedList(os.path.join(configpath,'urls')) #get urls
            feedListReturn = self.screen.showList(namelist)
            if feedListReturn[0] == 'q': #pressed q / exit app
                self.screen.close()
                break;
            elif feedListReturn[0] == 'r': #pressed r / update selected feed
                self.updateFeed(urllist[feedListReturn[1]])
            elif feedListReturn[0] == 'R': #pressed R / update all feeds
                for feed in urllist:
                    self.screen.setStatus('Updating: {0}'.format(feed))
                    self.updateFeed(feed)

            else: #feedlist
                while(1):
                    articleList,articleContent = self.getArticleList(urllist[feedListReturn[1]])
                    articleListReturn = self.screen.showList(articleList)
                    if (articleListReturn[0] == 'q'):
                        break;
                    elif (articleListReturn[0] == 'r' or articleListReturn[0] == 'R'): #pressed r / update this feed
                        self.updateFeed(urllist[feedListReturn[1]])
                    else:
                        self.screen.showArticle(self.rssworker.htmlToText(articleContent[articleListReturn[1]]))

        return


    def getArticleList(self, feedurl):
        feed = self.database.getArticles(feedurl)
        articleList = [];
        articleContent = []
        for article in feed:
            datetimetuple = article[5].split(",")
            pubdate = "{0}/{1}/{2}".format(datetimetuple[0],datetimetuple[1],datetimetuple[2])
            articleList.append("{0}    {1}".format(pubdate,article[3]))

            thisHeader = []
            thisHeader.append("Title: {0}<br>".format(article[3]))
            thisHeader.append("Date:  {0} {1}:{2}<br>".format(pubdate,datetimetuple[3],datetimetuple[4]))
            thisHeader.append("Link:  {0}<br>".format(article[2]))
            thisHeader.append("<hr>")
            articleContent.append(''.join(thisHeader)+article[4])

        return articleList, articleContent


    def updateFeed(self, feedurl):
        """
        Add articles to database
        """
        feedName, articles, version = self.rssworker.getFeed(feedurl)
        if (feedName == -1 and articles == -1):
            return #invalid feed
        self.database.addFeed(feedurl, feedName) #add or update feed name
        #insert feeds into the database
        try:
            for article in articles:
                year   = str(article[3][0])
                month  = str(article[3][1]).zfill(2);
                day    = str(article[3][2]).zfill(2)
                hour   = str(article[3][3]).zfill(2);
                minute = str(article[3][4]).zfill(2);

                pubDate = "{0},{1},{2},{3},{4}".format(year,month,day,hour,minute)
                self.database.addArticle(feedurl,article[0],article[1],article[2],pubDate)
        except Exception as e:
            self.screen.close()
            print(feedName)
            print(article)
            print(e)
        return


    def getFeedList(self,urlFile):
        if (os.path.exists(urlFile) == False): #create the file if it doesnt exist
            f = open(urlFile,'w')
            f.write("")
            f.close()

        f = open(urlFile, 'r')
        feedNameList = []
        feedUrlList = []
        for url in f.readlines():
            feedUrlList.append(url)
            feedName = self.database.getFeedInfo(url)
            if (feedName == ""):
                feedNameList.append(url)
            else:
                feedNameList.append(feedName)
        f.close()
        return feedUrlList, feedNameList


    def getConfigPath(self):
        homefolder = os.path.expanduser('~')
        configfolder = os.path.join(homefolder, '.cursesrss')
        if (os.path.exists(configfolder) == False):
            os.mkdir(configfolder)
        return configfolder

#
prog = mainprogram()