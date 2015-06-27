# simpleRSS
## Curses RSS Reader

I know there are a lot of RSS readers out there, I recently decided to learn how to program with curses and also learn how to use git.
My goal is to make something like newsbeuter but with image support and maybe categories.

Screenshots:

![Feed List](http://i.imgur.com/tAOYBzJ.png)
![Article List](http://i.imgur.com/nYcQldL.png)
![Article](http://i.imgur.com/S9ivkCW.png)

Dependencies (Python modules):
  * feedparser
  * html2text
 

**This app is not ready to use yet, it's not finished and contains bugs.**

Tasks:
- [x] Get and parse feeds
- [x] Store feeds in the database
- [x] Show List of Feeds, List of Articles and Articles
- [/] Read/Unread articles
- [ ] Article Links in the end (like newsbeuter)
- [ ] Config file to change colors
- [ ] Show article images (with w3m or similar)
- [ ] Detect terminal resize (curses.update_lines_cols() )
