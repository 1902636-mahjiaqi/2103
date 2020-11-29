import bs4 as bs
import urllib.request
import json
import re
from datetime import datetime
from SentimentTest1 import SentimentAnalyse
import mysql.connector as mysql
import pymongo

import requests
from bs4 import BeautifulSoup
from SentimentTest1 import SentimentAnalyse
from datetime import datetime
from selenium import webdriver
import random
import time
from time import sleep

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
        mainPage = urllib.request.urlopen(url+str(pagenum))
        soup = bs.BeautifulSoup(mainPage,'lxml')
        for link in soup.find_all("span", class_="story-headline"):
            stURLsList.append(link.findChild()['href'])

    for link in stURLsList:
        #finding the content of the article
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
    todayArticlesList = []
    #uses JSON instead of bs
    for pagenum in range(pageCount):
        url = "https://www.todayonline.com/json-solr/"+ keyword + "/search?&page=" + str(pagenum)
        html = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(html,'html.parser')
        url_json = json.loads(soup.text)
        #finding the content of the article
        for node in url_json['nodes']:
            article = todayArticle("title", "author", "date", "", "link")
            if node.get('node').get('author') != "":
                article.author = node.get('node').get('author')
            else:
                article.author = "Not Found"
            article.date = datetime.utcfromtimestamp(int(node.get('node').get('publication_date'))).strftime('%Y-%m-%d')
            article.title = node.get('node').get('title')
            article.url = node.get('node').get('node_url')

            articleURL = "https://www.todayonline.com/api/v3/article/" + node.get('node').get('node_id')
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
            todayArticlesList.append(article)
    return todayArticlesList

#Using selenium webdriver to retrieve CNA since as they use javascript to create content
def ScrapeCNA(category,pages):
    #1 is health, #2 is business, #3 politics
    listofarticles = []
    if category == 1:
        search = "Health"
    elif category == 2:
        search = "Politics"
    else:
        search = "Business"

    for i in range(pages):
        contentlinks = []
        driver = webdriver.Chrome(executable_path="chromedriver.exe", port=8080)
        pageurl = "https://www.channelnewsasia.com/action/news/8396414/search?q={0}&page={1}".format(search, i)
        driver.get(pageurl)
        time.sleep(5)
        try:
            driver1 = driver.find_element_by_class_name("result-section__list")
            driver2 = driver1.find_elements_by_class_name("teaser__title")
        except:
            continue

        for pages in driver2:
            print(pages.get_attribute('href'))
            contentlinks.append(pages.get_attribute('href'))

        driver.quit()
        for links in contentlinks:

            SentimentRating = 0
            ArticleText = ""
            print("----------------------")
            print(links)
            ArticleURL = links
            contentpage = requests.get(links)
            soup = BeautifulSoup(contentpage.content, 'html.parser')

            # Find Title
            Title = soup.find("h1", class_="article__title")
            if (Title != None):
                ArticleTitle = Title.getText()
            # Find Content
            content_result = soup.find("div", class_="c-rte--article")
            if content_result == None:
                print("No results")
                continue
            content_result = content_result.findAll("p")
            for i in content_result:
                if i.find(class_='c-picture--article'):
                    continue
                SentimentRating += SentimentAnalyse(i.getText())
                ArticleText += i.getText()
            # Find Date
            Dateresult = soup.find("time", class_="article__details-item")
            datetime_object = datetime.strptime(Dateresult.getText(), '%d %b  %Y %I:%M%p')
            ArticleDate = datetime_object.strftime("%Y-%m-%d")
            listofarticles.append(stArticle(ArticleTitle,"",ArticleDate,ArticleText,ArticleURL))
    return listofarticles

def pushtoDB(articlesList,agency,category):
    db = mysql.connect(
        host="rm-gs595dd89hu8175hl6o.mysql.singapore.rds.aliyuncs.com",
        user="ict1902698psk",
        passwd="KSP8962091",
        database="sql1902698psk"
    )
    cursor = db.cursor()
    for article in articlesList:
        SentimentRating = 0
        SentimentRating += SentimentAnalyse(article.content)
        try:
            query = "INSERT INTO article VALUES (%s,%s,%s,%s,%s,%s,%s,%s,MD5(%s))"
            #val = (0, article.url, article.title, article.date, SentimentRating, article.content, "2", agency, category, article.title)
            val = (0, article.url, article.title, article.date, SentimentRating, article.content, agency, category, article.title)
            cursor.execute(query, val)
            db.commit()
            print("passed: " + article.title)
        except:
            print("error: " + article.title)
            continue
    cursor.close()


"""
#straitstime
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

#Today's
Tarticles1 = todayCrawl("health",20)
Tarticles2 = todayCrawl("business",20)
Tarticles3 = todayCrawl("politics",20)


pushtoDB(Tarticles1,3,1)
pushtoDB(Tarticles2,3,2)
pushtoDB(Tarticles3,3,3)

#CNA

CNAarticles1 = ScrapeCNA(1,3)
CNAarticles2 = ScrapeCNA(2,3)
CNAarticles3 = ScrapeCNA(3,3)

pushtoDB(CNAarticles1,3,1)
pushtoDB(CNAarticles2,3,2)
pushtoDB(CNAarticles3,3,3)

"""