import bs4 as bs
import urllib.request
import json
import re
from datetime import datetime
from SentimentTest1 import SentimentAnalyse
import mysql.connector as mysql

class stArticle:
    def __init__(self, title, author, date, content, url):
        self.title = title
        self.author = author
        self.date = date
        self.content = content
        self.url = url

class todayArticle:
    def __init__(self, title, author, date, content, url):
        self.title = title
        self.author = author
        self.date = date
        self.content = content
        self.url = url

def stCrawl(url,pageCount):
    #number of pages
    stURLsList = []
    stArticlesList = []
    for pagenum in range(pageCount):
        #mainpage = urllib.request.urlopen('https://www.straitstimes.com/business/economy?page='+str(pagenum))
        mainPage = urllib.request.urlopen(url+str(pagenum))
        soup = bs.BeautifulSoup(mainPage,'lxml')
        for link in soup.find_all("span", class_="story-headline"):
            stURLsList.append(link.findChild()['href'])

    for link in stURLsList:
        #print (link)
        articlePage = urllib.request.urlopen('https://www.straitstimes.com'+link)
        soup = bs.BeautifulSoup(articlePage,'lxml')

        article = stArticle("title", "author", "date", "", 'https://www.straitstimes.com' + link)

        contentParent = soup.find_all(attrs={"itemprop":"articleBody"})
        for eleParent in contentParent:
            for eleChild in eleParent.find_all('p'):
                if eleChild.text != "":
                    article.content = article.content + "\n" + eleChild.text

        article.title = soup.find_all(attrs={"itemprop":"name"})[0]['content']
        if not soup.find("meta", property="article:author") is None:
            article.author = soup.find("meta", property="article:author")['content']
        else:
            article.author = "2"
        date = soup.find(attrs={"property":"article:published_time"})['content']
        date = datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d')
        article.date = date
        stArticlesList.append(article)
    return stArticlesList

################################################################
def todayCrawl(keyword,pageCount):
    #todayURLsList = []
    todayArticlesList = []
    for pagenum in range(pageCount):
        url = "https://www.todayonline.com/json-solr/"+ keyword + "/search?&page=" + str(pagenum)
        html = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(html,'html.parser')
        url_json = json.loads(soup.text)

        #print(url_json)
        for node in url_json['nodes']:
            article = todayArticle("title", "author", "date", "", "link")
            if not node.get('node').get('author') is "":
                article.author = node.get('node').get('author')
            else:
                article.author = "2"
            article.date = datetime.utcfromtimestamp(int(node.get('node').get('publication_date'))).strftime('%Y-%m-%d')
            article.title = node.get('node').get('title')
            article.url = node.get('node').get('node_url')
            #print(node.get('node').get('title'))

            articleURL = "https://www.todayonline.com/api/v3/article/" + node.get('node').get('node_id')
            #print(articleURL)
            articleHTML = urllib.request.urlopen(articleURL).read()
            articleSoup = bs.BeautifulSoup(articleHTML,'html.parser')
            ArticleURL_Json = json.loads(articleSoup.text)
            articleContent = ArticleURL_Json.get('node').get('body')

            #cleaning of content
            clean = re.compile('<.*?>')
            articleContent = re.sub(clean, '', articleContent)
            articleContent = re.sub('&nbsp;', ' ', articleContent)
            articleContent = re.sub('\n', ' ', articleContent)
            articleContent =  re.sub(' +', ' ', articleContent)
            article.content = articleContent
            #print(articleContent)
            todayArticlesList.append(article)

    # for a in todayArticlesList:
    #     articlePage = urllib.request.urlopen(a.url)
    #     soup = bs.BeautifulSoup(articlePage,'lxml')
    #     contentParent = soup.find_all('p', class_='article-detail_body')

    #     for eleParent in contentParent:
    #         #print(ele.text)
    #         ###### HELP #### somehow got "content" inserted
    #         if eleParent.text != "content":
    #             article.content = article.content + "\n" + eleParent.text        
    #     print(soup)
    return todayArticlesList

db = mysql.connect(
        host="rm-gs595dd89hu8175hl6o.mysql.singapore.rds.aliyuncs.com",
        user="ict1902698psk",
        passwd="KSP8962091",
        database="sql1902698psk"
    )
cursor = db.cursor()

def pushtoDB(articlesList,agency,category):
    #count = 1
    for article in articlesList:
        #print(count)
        SentimentRating = 0
        SentimentRating += SentimentAnalyse(article.content)
        #print("Title is "+article.title)
        #print("author is "+article.author)
        #print(article.content)
        #print(SentimentRating)
        #print("date is "+article.date)
        #print("url is "+article.url)
        #count+=1
        try:
            query = "INSERT INTO article VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,MD5(%s))"
            val = (
            0, article.url, article.title, article.date, SentimentRating, article.content, "2", agency, category,
            article.title)
            cursor.execute(query, val)
            db.commit()
            print("passed: " + article.title)
        except:
            print("error: " + article.title)
            continue
        print("\n")


"""

    1:
        search = "health"
    2:
        search = "business"
    3:
        search = "politics"

"""
#agency = 1
STarticles1 = stCrawl("https://www.straitstimes.com/business/economy?page=",10)
STarticles2 = stCrawl("https://www.straitstimes.com/business/invest?page=",10)
STarticles3 = stCrawl("https://www.straitstimes.com/business/banking?page=",10)
STarticles4 = stCrawl("https://www.straitstimes.com/business/companies-markets?page=",10)

STarticles5 = stCrawl("https://www.straitstimes.com/tags/coronavirus?page=",10)
STarticles6 = stCrawl("https://www.straitstimes.com/singapore/health?page=",10)

STarticles7 = stCrawl("https://www.straitstimes.com/politics/latest?page=",8)
STarticles8 = stCrawl("https://www.straitstimes.com/tags/us-presidential-election-2020?page=",3)

pushtoDB(STarticles5,1,1)
pushtoDB(STarticles6,1,1)

pushtoDB(STarticles1,1,2)
pushtoDB(STarticles2,1,2)
pushtoDB(STarticles3,1,2)
pushtoDB(STarticles4,1,2)

pushtoDB(STarticles7,1,3)
pushtoDB(STarticles8,1,3)
"""

#agency = 3
Tarticles1 = todayCrawl("health",20)
Tarticles2 = todayCrawl("business",20)
Tarticles3 = todayCrawl("politics",20)


pushtoDB(Tarticles1,3,1)
pushtoDB(Tarticles2,3,2)
pushtoDB(Tarticles3,3,3)
"""