from screen import screen
from rssget import rss
from database import database
import os

class mainprogram(object):
    def __init__(self):
        #intantiate classes
        configpath = self.getConfigPath()
        config, urlsfile = self.getConfigs()
        self.database = database(os.path.join(configpath,'database.db3'))
        self.screen = screen()
        self.rssworker = rss()

        #check browser configs
        if 'browser' in config.keys():
            browser = config['browser']
        else:
            browser = 'xdg-open'
        #mainloop
        feedPadY = 0
        selectedFeed = 0;
        while(1):
            self.screen.showInterface(" simpleRSS v0.1 Alpha", " q:Quit,ENTER:Open,r:Reload,R:Reload All,a:Mark Feed Read,A:Mark All Read");
            urllist, namelist,totallist,unreadlist = self.getFeedList(urlsfile) #get urls
            viewList = []
            for number in unreadlist:
                if number > 0:
                    viewList.append(0)
                else:
                    viewList.append(1)
            feedListKey,feedPadY,selectedFeed = self.screen.showList(namelist, feedPadY, selectedFeed, viewList)
            if feedListKey == 'q': #pressed q / exit app
                self.screen.close()
                break;
            elif feedListKey == 'r': #pressed r / update selected feed
                self.updateFeed(urllist[selectedFeed])
            elif feedListKey == 'R': #pressed R / update all feeds
                for feed in urllist:
                    self.screen.setStatus('Updating: {0}'.format(feed))
                    self.updateFeed(feed)
                self.updateFeed("Done")
            elif feedListKey == 'a': #mark feed as read
                self.database.setFeedViewed(urllist[selectedFeed],1)
            elif feedListKey == 'A': #mark all read
                self.database.setAllViewed(1)
            elif feedListKey == 'u': #mark feed as NOT read
                self.database.setFeedViewed(urllist[selectedFeed],0)
            elif feedListKey == 'U': #mark all NOT read
                self.database.setAllViewed(0)
            elif feedListKey == 'return': #feedlist
                selectedArticle = 0
                articlePadY = 0
                while(1):
                    self.screen.showInterface(" simpleRSS v0.1 Alpha - {0}".format(namelist[selectedFeed].split("\t")[1]), " q:Back,ENTER:Open,o: Open in Browser,r:Reload,a:Mark Article Read,A:Mark All Read");
                    articleList,articleContent,articleViewed,articleUrl = self.getArticleList(urllist[selectedFeed])
                    articleListKey, articlePadY, selectedArticle = self.screen.showList(articleList, articlePadY, selectedArticle, articleViewed)
                    if (articleListKey == 'q'):
                        break;
                    elif (articleListKey == 'r' or articleListKey == 'R'): #pressed r / update this feed
                        self.updateFeed(urllist[selectedArticle])
                    elif articleListKey == 'a': #mark article read
                        self.database.setArticleViewed(articleUrl[selectedArticle])
                    elif articleListKey == 'A': #mark feed read
                        self.database.setFeedViewed(urllist[selectedFeed],1)
                    elif articleListKey == 'u': #mark article NOT read
                        self.database.setArticleViewed(articleUrl[selectedArticle],0)
                    elif articleListKey == 'U': #mark feed NOT read
                        self.database.setFeedViewed(urllist[selectedFeed],0)
                    elif articleListKey == 'o': #open in browser
                        os.system(browser+' '+articleUrl[selectedArticle] + " > /dev/null &")
                    elif (articleListKey == 'return'):
                        showArticlePadY = 0
                        self.screen.showInterface(" simpleRSS v0.1 Alpha - {0}".format(namelist[selectedFeed].split("\t")[1]), " q:Back,o: Open in Browser");
                        self.database.setArticleViewed(articleUrl[selectedArticle])
                        while(1):
                            showArticleKey, showArticlePadY = self.screen.showArticle(self.rssworker.htmlToText(articleContent[selectedArticle],self.screen.getDimensions()[1]), showArticlePadY)
                            if showArticleKey == 'q':
                                break;
                            elif showArticleKey == 'o':
                                os.system(browser+' '+articleUrl[selectedArticle] + " > /dev/null 2>&1")
                            elif articleListKey == 'u': #mark article NOT read
                                self.database.setArticleViewed(articleUrl[selectedArticle],0)
        return


    def getArticleList(self, feedurl):
        feed = self.database.getArticles(feedurl)
        articleList = [];
        articleContent = []
        articleViewed = []
        articleUrl = []
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

            articleViewed.append(int(article[6]))
            articleUrl.append(article[2])
        return articleList, articleContent, articleViewed, articleUrl


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
        return


    def getFeedList(self,urlFile):
        if (os.path.exists(urlFile) == False): #create the file if it doesnt exist
            f = open(urlFile,'w')
            f.write("")
            f.close()

        f = open(urlFile, 'r')
        feedNameList = []
        feedUrlList = []
        feedTotalList = []
        feedUnreadList = []
        for url in f.readlines():
            feedUrlList.append(url)
            feedName,totalArticles,unreadArticles = self.database.getFeedInfo(url)
            feedTotalList.append(totalArticles)
            feedUnreadList.append(unreadArticles)
            unreadArticles = str(unreadArticles)
            totalArticles = str(totalArticles)
            feedNameList.append("({0}/{1})\t{2}".format(unreadArticles.zfill(2),totalArticles.zfill(2),feedName))
        f.close()
        return feedUrlList, feedNameList, feedTotalList, feedUnreadList;

    def getConfigs(self):
        configFilePath = os.path.join(self.getConfigPath(),'config')
        if (os.path.exists(configFilePath) == False):
            f = open(configFilePath,'w')
            f.write("")
            f.close()
        f = open(configFilePath,'r')
        fileLines = f.readlines()
        configs = {}
        for line in fileLines:
            if '=' in line:
                config = line.split('=')
                config[0] = config[0].strip()
                config[1] = config[1].strip()
                configs[config[0]] = config[1]
        f.close()

        urlFilePath = os.path.join(self.getConfigPath(),'urls')
        return configs,urlFilePath
        
    def getConfigPath(self):
        homefolder = os.path.expanduser('~')
        configfolder = os.path.join(homefolder, '.cursesrss')
        if (os.path.exists(configfolder) == False):
            os.mkdir(configfolder)
        return configfolder

#
prog = mainprogram()
