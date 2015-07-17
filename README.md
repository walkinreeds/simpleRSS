# simpleRSS
## Curses RSS Reader

I know there are a lot of RSS readers out there, I recently decided to learn how to program with curses and also learn how to use git.
My goal is to make something like newsbeuter but with image support and maybe categories.

###Screenshots:

![Feed List](http://i.imgur.com/tAOYBzJ.png)
![Article List](http://i.imgur.com/nYcQldL.png)
![Article](http://i.imgur.com/S9ivkCW.png)

Dependencies (Python modules):
  * feedparser
  * html2text


**This app is not ready to use yet, it's not finished and contains bugs.**

Tasks for 0.1 release:
- [x] Get and parse feeds
- [x] Store feeds in the database
- [x] Show List of Feeds, List of Articles and Articles
- [x] Open Articles in Browser
- [x] Config file (set default browser, other settings will be implemented as needed)
- [x] Read/Unread articles
- [x] Detect terminal resize
- [x] Article Links in the end (like newsbeuter)
- [x] Choose colors in config file
- [x] Open Help in ? key

###Configuration
Configuration files are stored in ~/.simplerss/ directory, all files are created the first time you run the program.

You can add feeds simply adding urls to .simplerss/urls, example:
```
http://strangequark.tk/index.php/feed
http://distrowatch.com/news/dw.xml
https://www.archlinux.org/feed/news
http://www.reddit.com/r/archlinux/.rss
```
By default simpleRSS will open links with xdg-open, if you want to use other browser you can set it on .simplerss/config, example:
```
browser = firefox
```

###Keys
####Feed List
* j,Down Arrow - Select next item
* k,Up Arrow	 - Select previous item
* l, Enter	 - Enter feed
* h, q		 - Quit
* a			 - Mark selected feed as read
* A			 - Mark all feeds read
* r			 - Reload selected feed
* R			 - Reload all feeds
* u			 - Mark selected feed as unread
* U			 - Mark all feeds as unread

####Article List
* j,Down Arrow - Select next item
* k,Up Arrow	 - Select previous item
* l, Enter	 - Show article
* h, q		 - Go back to Feed List
* a			 - Mark selected article as read
* A			 - Mark feed articles in read
* r			 - Reload this feed
* o			 - Open this article in browser
* u			 - Mark selected article as unread
* U			 - Mark all feed articles as unread

####Article Content
* j,Down Arrow - Select next item
* k,Up Arrow	 - Select previous item
* l, Enter	 - Show article
* h, q		 - Go back to Article List
* o			 - Open this article in browser
* u			 - Mark this article as unread
