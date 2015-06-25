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

        urllist, namelist = self.getFeedList(os.path.join(configpath,'urls')) #get urls
         
        self.screen.showInterface(0);
        #mainloop
        while(1):
            feedListReturn = self.screen.showList(namelist)

            if feedListReturn[1] == -1:
                self.screen.close()
                break;
            elif feedListReturn[1] == -2: #update selected feed
                feed = rssworker.getFeed(urllist[feedListReturn[0]])
                self.database.addFeed(urllist[feedListReturn[0]], feed[0]) #add or update feed name
                #insert feeds into the database
                for article in feed[1]:
                    print(article.links[0]['href'])
                    #database.addArticle(urllist[feedListReturn[0]],article.href,article.title,article.content,article.published)
            else: #feedlist
                feed = self.database.getArticles(urllist[feedListReturn[0]])
                articleList = [];
                #for article in feed[1]:
                #    articleList.append("{0}    {1}".format(article.published,article.title))

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
