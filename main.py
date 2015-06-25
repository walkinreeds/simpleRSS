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
        rssworker = rss()

        urllist = self.getFeedList(os.path.join(configpath,'urls')) #get urls

        self.screen.showInterface(0);
        #mainloop
        while(1):
            feedListReturn = self.screen.showList(urllist)

            if feedListReturn[0] == -1:
                self.screen.close()
                break;
            else: #feedlist
                feed = rssworker.getFeed(urllist[feedListReturn[0]])
                articleList = [];
                for article in feed[1]:
                    articleList.append("{0}    {1}".format(article.published,article.title))

                #articlesloop
                while(1):
                    articleListReturn = self.screen.showList(articleList)
                    if (articleListReturn[0] == -1):
                        break;
        return


    def getFeedList(self,urlFile):
        if (os.path.exists(urlFile) == False): #create the file if it doesnt exist
            f = open(urlFile,'w')
            f.write("")
            f.close()

        f = open(urlFile, 'r')
        feedlist = []
        for url in f.readlines():
            feedName = self.database.getFeedInfo(url)
            if (feedName == ""):
                feedlist.append(url)
            else:
                feedlist.append(feedName)
        f.close()
        return feedlist


    def getConfigPath(self):
        homefolder = os.path.expanduser('~')
        configfolder = os.path.join(homefolder, '.cursesrss')
        if (os.path.exists(configfolder) == False):
            os.mkdir(configfolder)
        return configfolder

#
prog = mainprogram()
