#gets rss feeds and manages the database
import feedparser
import datetime
import html2text

class rss(object):
    def getFeed(self,url):
        d = feedparser.parse(url)
        try:
            if d.version == '':
                return -1,-1,-1
        except Exception as e:
            return -1,-1,-2

        articles = []
        for entry in d.entries:
            article = []
            article.append(entry['link'])
            article.append(entry['title'])

            content = ""
            if 'content' in entry.keys():
                content = entry['content'][0]['value']
            elif 'summary' in entry.keys():
                content = entry['summary']
            article.append(content)

            if 'published_parsed' in entry.keys():
                articleDate = entry['published_parsed']
            elif 'updated_parsed' in entry.keys():
                articleDate = entry['updated_parsed']
            else:
                articleDate = datetime.datetime.timetuple(datetime.datetime.now())
            article.append(articleDate)

            articles.append(article)

        return d.feed.title, articles, d.version

    def htmlToText(self,content, showImgTags = False):
        parser = html2text.HTML2Text(bodywidth=0)                    
        parser.images_with_size = showImgTags
        #parser.images_to_alt = not(showImgTags)
        parser.inline_links = False
        markdown = parser.handle(content)

        #remove some chars
        markdown = markdown.replace('&lt;','<')
        markdown = markdown.replace('&gt;','>')
        markdown = markdown.replace(' \- ', ' - ') #dont know why html2text does this
        return markdown

if __name__ == '__main__':
    import sys
    url = sys.argv[1]
    article = int(sys.argv[2])
    width = int(sys.argv[3])
    prog = rss()
    title, content, version = rss.getFeed(prog,url)
    #print()
    #print(title)
    #print(version)
    #print("Title:",content[0][1])
    #print("Link:",content[0][0])
    #pubDate = content[0][3]
    #print("Date: {0}-{1}-{2} {3}:{4}".format(pubDate[0],pubDate[1],pubDate[2],pubDate[3],pubDate[4]))
    print("Content:")
    print(prog.htmlToText(content[article][2], width))
