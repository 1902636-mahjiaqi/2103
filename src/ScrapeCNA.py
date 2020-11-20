import requests
from bs4 import BeautifulSoup
from SentimentTest1 import SentimentAnalyse
from datetime import datetime
from selenium import webdriver
import random
import time
from time import sleep
from main_pak import stArticle, pushtoMongoDB


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
    pushtoMongoDB(listofarticles,2,search)

ScrapeCNA(3,5)


