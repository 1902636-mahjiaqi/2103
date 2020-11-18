import pymongo
from datetime import datetime
import hashlib

client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client["ICT2103_Project"]

def SelectAllArticleTitle(cursor):
    pass
    # query = "SELECT a.ArticleID, a.ArticleTitle, a.ArticleDate, c.CategoryName, p.AgencyName FROM article a, articlecategory c, agency p WHERE a.AgencyID = p.AgencyID AND a.CategoryID = c.CategoryID ORDER BY a.ArticleDate DESC"
    # cursor.execute(query)
    # results = cursor.fetchall()
    # Homepageresults = []
    # for result in results:
    #     article = (result[0],result[1],result[2].strftime("%d/%m/%Y"),result[3],result[4])
    #     Homepageresults.append(article)
    # return Homepageresults

def SelectArticleDetails(cursor, articleID):
    #Title, Date, URL, Sentiment, ArticleText,CategoryName, Agency Name
    pass
    # query = "SELECT a.ArticleTitle, a.ArticleDate,a.ArticleURL,a.SentimentRating,a.ArticleText, c.CategoryName, p.AgencyName FROM article a, articlecategory c, agency p WHERE a.AgencyID = p.AgencyID AND a.CategoryID = c.CategoryID AND ArticleID = {0}".format(articleID)
    # cursor.execute(query)
    # result = cursor.fetchone()
    # listresult = list(result)
    # listresult[1] = listresult[1].strftime("%d/%m/%Y")
    # return listresult

def LikeArticle(db,userID,articleID):
    query = {"_id": articleID}
    values = { "$push": { "likeList": userID } }
    selectedcol = db["Articles"]
    result = selectedcol.update_one(query, values)
    if result.matched_count > 0:
        return True
    else:
        return False

def UnlikeArticle(db,userID,articleID):
    query = {"_id": articleID}
    values = {"$pull": {"likeList": userID}}
    selectedcol = db["Articles"]
    result = selectedcol.update_one(query, values)
    if result.matched_count > 0:
        return True
    else:
        return False

def CheckLike(cursor,userID,articleID):
    pass
    # query = "SELECT * FROM likedby WHERE UserID = {0} AND ArticleID = {1}".format(userID,articleID)
    # cursor.execute(query)
    # result = cursor.fetchone()
    # if result != None:
    #     return True
    # else:
    #     return False

def SelectRecentArticles(cursor):
    pass
    #This function is to select the past 24 hours of articles so as to generate the word cloud
    # query = "SELECT ArticleText FROM article WHERE ArticleDate >= date_sub(curdate(), interval 1 day)"
    # cursor.execute(query)
    # result = cursor.fetchall()
    # return result


#print(SelectRecentArticles(cursor))
#print(CheckLike(cursor,6,2420))
#print(LikeArticle(db,21,40))
#print(SelectArticleDetails(cursor,2427))
#print(SelectAllArticleTitle(cursor)[0])
#print(UnlikeArticle(db,21,40))