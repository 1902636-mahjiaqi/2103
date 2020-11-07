import requests
from bs4 import BeautifulSoup
from SentimentTest1 import SentimentAnalyse
from datetime import datetime
from selenium import webdriver
import random
import mysql.connector as mysql
import time
from time import sleep

def ScrapeCNA(category,pages):
    #1 is health, #2 is business, #3 politics
    # db = mysql.connect(
    #     host="rm-gs595dd89hu8175hl6o.mysql.singapore.rds.aliyuncs.com",
    #     user="ict1902698psk",
    #     passwd="KSP8962091",
    #     database="sql1902698psk"
    # )
    # cursor = db.cursor()
    if category == 1:
        search = "health"
    elif category == 2:
        search = "business"
    else:
        search = "politics"

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
            AgencyID = 2
            CategoryID = category
            print("----------------------")
            print(links)
            ArticleURL = links
            contentpage = requests.get(links)
            soup = BeautifulSoup(contentpage.content, 'html.parser')
            author_results = soup.find("a", class_="article__author-title")

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
                    print("here")
                    continue
                SentimentRating += SentimentAnalyse(i.getText())
                ArticleText += i.getText()
                print(i.getText())
            # Find Date
            Dateresult = soup.find("time", class_="article__details-item")
            datetime_object = datetime.strptime(Dateresult.getText(), '%d %b  %Y %I:%M%p')
            ArticleDate = datetime_object.strftime("%Y-%m-%d")
            # try:
                # query = "INSERT INTO article VALUES (%s,%s,%s,%s,%s,%s,%s,%s,MD5(%s))"
                # val = (
                # 0, ArticleURL, ArticleTitle, ArticleDate, SentimentRating, ArticleText, AgencyID, CategoryID,
                # ArticleTitle)
                # cursor.execute(query, val)
                # print(ArticleDate)
                # print(ArticleText)
                # print(ArticleURL)
                # print(SentimentRating)
                # print(ArticleTitle)
                # db.commit()
            # except:
            #     print("error")
            #     print(ArticleTitle)
            #     continue

ScrapeCNA(3,2)


