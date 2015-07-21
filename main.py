from screen import screen
from rssget import rss
from database import database
import os
import traceback

import time
VERSION = 0.2

KEY_UP = 259
KEY_DOWN = 258
KEY_RIGHT = 261
KEY_LEFT = 260
class mainprogram(object):
    def __init__(self):
        self.title = "SimpleRSS {0} Development Version".format(VERSION)
        #instantiate classes
        self.config = self.getConfigs()
        self.database = database(os.path.join(self.getConfigPath(),'database.db3'), VERSION)
        self.screen = screen(self.config)
        self.rssworker = rss()

        self.screen.setWindowTitle(self.title);

        self.moveUpKeys = [KEY_UP,ord('k')]
        self.moveDownKeys = [KEY_DOWN,ord('j')]

        try:
            self.showFeedList()
        except Exception as e:
            self.screen.close()
            print("simpleRSS crashed:")
            traceback.print_exc()
        return

    def showCategoryList(self, selectedItem, padY):
        pass
    
    def showFeedList(self, category = "all"):
        feedPadY = 0
        selectedFeed = 0;
        feedListReturnKeys = [ord('q'), ord('h'), ord('r'), ord('R'), ord('a'), ord('A'), ord('u'), ord('U'), 10, ord('l'), ord('?')]
        #loop
        while(1):
            urllist, namelist,totallist,unreadlist = self.getFeedList() #get urls
            if (len(urllist) == 0):
                self.screen.close()
                print("You need to add feeds to your {0} file.".format(os.path.join(self.getConfigPath(), 'urls')))
                return

            self.screen.showInterface(" {0}".format(self.title), " q:Quit,ENTER:Open,r:Reload,R:Reload All,a:Mark Feed Read,A:Mark All Read");
            viewList = []
            for number in unreadlist:
                if number > 0: viewList.append(0)
                else: viewList.append(1)

            feedListKey,feedPadY,selectedFeed = self.screen.showList(namelist, True, feedPadY, selectedFeed, viewList, self.moveUpKeys, self.moveDownKeys, feedListReturnKeys)

            if feedListKey == ord('q') or feedListKey == ord('h'): #exit app
                self.screen.close()
                break;
            elif feedListKey == ord('r'): #pressed r / update selected feed
                self.updateFeed(urllist[selectedFeed])
            elif feedListKey == ord('R'): #pressed R / update all feeds
                for feed in urllist:
                    self.updateFeed(feed)
                self.screen.setStatus("Done updating")
            elif feedListKey == ord('a'): #mark feed as read
                self.database.setFeedViewed(urllist[selectedFeed],1)
            elif feedListKey == ord('A'): #mark all read
                self.database.setAllViewed(1)
            elif feedListKey == ord('u'): #mark feed as NOT read
                self.database.setFeedViewed(urllist[selectedFeed],0)
            elif feedListKey == ord('U'): #mark all NOT read
                self.database.setAllViewed(0)
            elif feedListKey == ord('?'): #help
                self.showHelp()
            elif feedListKey == 10 or feedListKey == ord('l'):
                #open article list
                self.showArticleList(namelist[selectedFeed].split("\t")[1], urllist[selectedFeed])
        return
                       
    def showArticleList(self, feedName, feedUrl):
        selectedArticle = 0
        articlePadY = 0
        articleListReturnKeys = [ord('q'), ord('h'), ord('r'), ord('R'), ord('a'), ord('A'), ord('u'), ord('U'), 10, ord('l'), ord('?'), ord('o')]
        while(1):
            articleList,articleContent,articleViewed,articleUrl = self.getArticleList(feedUrl)

            #get out if there's no articles
            if (len(articleList) == 0):
                break;

            self.screen.showInterface(" {0} - {1}".format(self.title, feedName), " q:Back,ENTER:Open,o: Open in Browser,r:Reload,a:Mark Article Read,A:Mark All Read");
            articleListKey, articlePadY, selectedArticle = self.screen.showList(articleList, False, articlePadY, selectedArticle, articleViewed, self.moveUpKeys, self.moveDownKeys, articleListReturnKeys)
            if articleListKey == ord('q') or articleListKey == ord('h'):
                break;
            elif articleListKey == ord('r'): #pressed r / update this feed
                self.updateFeed(feedUrl)
            elif articleListKey == ord('a'): #mark article read
                self.database.setArticleViewed(articleUrl[selectedArticle])
            elif articleListKey == ord('A'): #mark feed read
                self.database.setFeedViewed(feedUrl,1)
            elif articleListKey == ord('u'): #mark article NOT read
                self.database.setArticleViewed(articleUrl[selectedArticle],0)
            elif articleListKey == ord('U'): #mark feed NOT read
                self.database.setFeedViewed(feedUrl,0)
            elif articleListKey == ord('o'): #open in browser
                self.openInBrowser(articleUrl[selectedArticle])
            elif articleListKey == ord('?'): #help
                self.showHelp()
            elif articleListKey == 10 or articleListKey == ord('l'):
                self.showArticle(feedName, articleUrl[selectedArticle], articleContent[selectedArticle])
        return

    def showArticle(self, feedName, articleUrl, articleContent):
        showArticlePadY = 0
        self.screen.showInterface(" {0} - {1}".format(self.title,feedName), " q:Back,o: Open in Browser");
        self.database.setArticleViewed(articleUrl)
        while(1):
            showArticleKey, showArticlePadY = self.screen.showArticle(self.rssworker.htmlToText(articleContent), showArticlePadY, self.moveUpKeys, self.moveDownKeys,[ord('q'), ord('h'), ord('l'), ord('o'), ord('u'), ord('?')])
            if showArticleKey == ord('q') or showArticleKey == ord('h'):
                break;
            elif showArticleKey == ord('o') or showArticleKey == ord('l'):
                self.openInBrowser(articleUrl)
            elif showArticleKey == ord('u'): #mark article NOT read
                self.database.setArticleViewed(articleUrl,0)
            elif showArticleKey == ord('?'): #help
                self.showHelp()
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
        self.screen.setStatus("Updating: "+feedurl)
        feedName, articles, version = self.rssworker.getFeed(feedurl)
        error = 0;
        if (feedName == -1 and articles == -1):
            self.screen.setStatus("Failed to get feed: "+feedurl)
            error = 1

        self.database.addFeed(feedurl, feedName, abs(error)) #add or update feed name
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
            self.screen.setStatus("Exception: {0}".format(e))
            return 

        self.screen.setStatus("Updated: "+feedurl)
        return

    def openInBrowser(self,url):
        #check browser configs
        if 'browser' in self.config.keys():
            browser = self.config['browser']
        else:
            browser = 'xdg-open'
        os.system(browser+' '+url+ " > /dev/null 2>&1")
        return

    def getFeedList(self):
        urlFile = os.path.join(self.getConfigPath(), 'urls');
        if (os.path.exists(urlFile) == False): #create the file if it doesnt exist
            f = open(urlFile,'w')
            f.write("http://strangequark.tk/index.php/feed")
            f.close()

        f = open(urlFile, 'r')
        feedNameList = []
        feedUrlList = []
        feedTotalList = []
        feedUnreadList = []
        for url in f.readlines():
            url = url.strip()
            if url[0] == "=": #is a category
                feedUrlList.append("")
                feedTotalList.append(-1)
                feedUnreadList.append(-1)
                feedNameList.append(url)
            else: #is a feed url
                feedUrlList.append(url)
                feedName,totalArticles,unreadArticles,error = self.database.getFeedInfo(url)
                feedTotalList.append(totalArticles)
                feedUnreadList.append(unreadArticles)
                unreadArticles = str(unreadArticles)
                totalArticles = str(totalArticles)
                if error == 1: 
                    indicator = "E";
                else:
                    indicator = " "; 
                feedNameList.append("{3} ({0}/{1})\t{2}".format(unreadArticles.zfill(2),totalArticles.zfill(2),feedName,indicator))
        f.close()
        return feedUrlList, feedNameList, feedTotalList, feedUnreadList

    def getConfigs(self):
        configFilePath = os.path.join(self.getConfigPath(),'config')
        if (os.path.exists(configFilePath) == False):
            f = open(configFilePath,'w')
            f.write("""# simpleRSS config file
browser = xdg-open

# Screen Colors
# 0 - Black; 1 - Red; 2 - Green; 3 - Yellow; 4 - Blue;
# 5 - Magenta; 6 - Cyan; 7 - White;
color_topbar = 0,7
color_bottombar = 0,7
color_listitem = 7,0
color_listitem_selected = 0,7
color_listitem_unread = 1,0
color_listitem_unread_selected = 1,7""")
            f.close()
        f = open(configFilePath,'r')
        fileLines = f.readlines()
        configs = {}
        for line in fileLines:
            if '=' in line and line[0] != "#":
                config = line.split('=')
                config[0] = config[0].strip()
                config[1] = config[1].strip()
                configs[config[0]] = config[1]
        f.close()
        return configs

    def getConfigPath(self):
        homefolder = os.path.expanduser('~')
        configfolder = os.path.join(homefolder, '.simplerss')
        if (os.path.exists(configfolder) == False):
            os.mkdir(configfolder)
        return configfolder

    def showHelp(self):
        self.screen.showInterface("{0} - Help".format(self.title),"q - Quit")
        helpContent = """<h1>Keys</h1><h2>Feed List</h2><ul>
                         <li>j,Down Arrow - Select next item</li>
                         <li>k,Up Arrow     - Select previous item</li>
                         <li>l, Enter   - Enter feed</li>
                         <li>h, q       - Quit</li>
                         <li>a          - Mark selected feed as read</li>
                         <li>A          - Mark all feeds read</li>
                         <li>r          - Reload selected feed</li>
                         <li>R          - Reload all feeds</li>
                         <li>u          - Mark selected feed as unread</li>
                         <li>U          - Mark all feeds as unread</li>
                         </ul>
                         <h2>Article List</h2>
                         <ul>
                         <li>j,Down Arrow - Select next item</li>
                         <li>k,Up Arrow     - Select previous item</li>
                         <li>l, Enter   - Show article</li>
                         <li>h, q       - Go back to Feed List</li>
                         <li>a          - Mark selected article as read</li>
                         <li>A          - Mark feed articles in read</li>
                         <li>r          - Reload this feed</li>
                         <li>o          - Open this article in browser</li>
                         <li>u          - Mark selected article as unread</li>
                         <li>U          - Mark all feed articles as unread</li>
                         </ul>
                         <h2>Article Content</h2>
                         <ul>
                         <li>j,Down Arrow - Select next item</li>
                         <li>k,Up Arrow     - Select previous item</li>
                         <li>l, Enter   - Show article</li>
                         <li>h, q       - Go back to Article List</li>
                         <li>o          - Open this article in browser</li>
                         <li>u          - Mark this article as unread</li>
                         </ul>"""
        showArticleKey, showArticlePadY = self.screen.showArticle(self.rssworker.htmlToText(helpContent),returnKeys=[ord('q')])
        return


if __name__ == '__main__':
    prog = mainprogram()
