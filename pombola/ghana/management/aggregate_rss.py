# RSS parser to aggregate desired topics from
# varios rss feeds
import csv
import os
import feedparser
import dateutil

BASEDIR = os.path.dirname(__file__)
#read list os rss feeds from file
FEEDS =[]
reader= csv.reader(open(os.path.join(BASEDIR,'rssfeeds.csv'),'rU'))
for row in reader:
    if reader.line_num ==1:
        headers = row
    else:
        if any(row):
            FEEDS.append(dict(zip(headers,[col.strip() for col in row])))


def aggregate_articles():
    feedhtml = ""
    feed_length = 0
    for feed in FEEDS:
        f = feedparser.parse(feed['feed'])
        focused = feed['category'] is 'parliament'
        for article in f['entries']:
            if focused or 'parliament' in article.title.lower() or 'parliament' in article.description.lower():
                if feed_length > 0:
                    feedhtml += '<article class="item white-panel">'
                else:
                    feedhtml += '<article class="item white-panel active">'
                feedhtml += '<h4 class="muted-text"><a href="{0}">{1}</a></h4>'.format(article.link.encode('utf-8','ignore'), article.title.encode('utf-8','ignore'))
                pubdate = dateutil.parser.parse(article.published.encode('utf-8','ignore')).date().strftime('%a %B %d, %Y')
                feedhtml += '<span><a class="label label-primary" href="http://{0}">{0}</a> &nbsp;&nbsp;<span  class="label label-default">{1}</span></span>'.format(feed['source'],pubdate)
                feedhtml += '<p>{0}...<a href="{1}">view article</a></p>'.format(article.description.encode('utf-8','ignore'), article.link.encode('utf-8','ignore'))
                feedhtml += '</article>\n'
                feed_length += 1
    return feedhtml


