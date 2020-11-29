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


def pushtoMongoDB(articlesList,agency,category):
    client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
    db = client["ICT2103_Project"]

    #val = (0, article.url, article.title, article.date, SentimentRating, article.content, agency, category, article.title)

    if category == "Health":
        categoryDetail = "Articles from the various publishers based on health crisis that is occuring around the world"
    elif category == "Politics":
        categoryDetail = "Articles from the various publishers based on current political news from around the world"
    elif category == "Business":
        categoryDetail = "Articles from the various publishers based on latest business news from around the world"
    else:
        categoryDetail = "Not found"

    if agency == 1:
        agency = "The Straits Times"
        agencyDetail = "The Straits Times is an English-language daily broadsheet newspaper based in Singapore and currently owned by Singapore Press Holdings"
    elif agency == 2:
        agency = "Channel News Asia"
        agencyDetail = "CNA is an English-language news channel based in Singapore. It broadcasts free-to-air domestically and as a subscription network to 29 territories across Asia and Australia."
    elif agency == 3:
        agency = "Today"
        agencyDetail = "TODAY is a Singapore English-language digital news provider under Mediacorp. It was formerly a national free daily newspaper."
    else:
        agency = "Not found"
        agencyDetail = "Not found"

    for article in articlesList:
        try:
            # Getting ArticleID Counter
            selectedcol = db["Articles"]

            SentimentRating = 0
            SentimentRating += SentimentAnalyse(article.content)


            aDate = datetime.strptime(article.date, "%Y-%m-%d")

            row = { 
            "ArticleURL": article.url, 
            "ArticleTitle": article.title,
            "ArticleDate": aDate,
            "ArticleContent": article.content,
            "SentimentRating": SentimentRating,
            "CategoryName": category,
            "CategoryDetail":categoryDetail,
            "AgencyName":agency,
            "AgencyDetail":agencyDetail,
            "likeList":[]}

            selectedcol.insert_one(row)
        except Exception as e: 
            print(e)
            continue


"""
Tarticles1 = todayCrawl("health",20)
Tarticles2 = todayCrawl("business",20)
Tarticles3 = todayCrawl("politics",20)

pushtoMongoDB(Tarticles1,3,"Health")
pushtoMongoDB(Tarticles2,3,"Business")
pushtoMongoDB(Tarticles3,3,"Politics")

STarticles1 = stCrawl("https://www.straitstimes.com/business/economy?page=",10)
STarticles2 = stCrawl("https://www.straitstimes.com/business/invest?page=",10)
STarticles3 = stCrawl("https://www.straitstimes.com/business/banking?page=",10)
STarticles4 = stCrawl("https://www.straitstimes.com/business/companies-markets?page=",10)

STarticles5 = stCrawl("https://www.straitstimes.com/tags/coronavirus?page=",8)
STarticles6 = stCrawl("https://www.straitstimes.com/singapore/health?page=",10)

STarticles7 = stCrawl("https://www.straitstimes.com/politics/latest?page=",8)
STarticles8 = stCrawl("https://www.straitstimes.com/tags/us-presidential-election-2020?page=",3)

pushtoMongoDB(STarticles5,1,"Business")
pushtoMongoDB(STarticles6,1,"Business")

pushtoMongoDB(STarticles1,1,"Health")
pushtoMongoDB(STarticles2,1,"Health")
pushtoMongoDB(STarticles3,1,"Health")
pushtoMongoDB(STarticles4,1,"Health")

pushtoMongoDB(STarticles7,1,"Politics")
pushtoMongoDB(STarticles8,1,"Politics")

#CNA

CNAarticles1 = ScrapeCNA(1,3)
CNAarticles2 = ScrapeCNA(2,3)
CNAarticles3 = ScrapeCNA(3,3)

pushtoMongoDB(CNAarticles1,3,1)
pushtoMongoDB(CNAarticles2,3,2)
pushtoMongoDB(CNAarticles3,3,3)
"""