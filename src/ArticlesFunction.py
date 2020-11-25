import pymongo
from bson.objectid import ObjectId
import datetime as dt
import hashlib

# client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
# db = client["ICT2103_Project"]

def SelectAllArticleTitle(db):
    query = {}
    selectedcol = db["Articles"]
    results = selectedcol.find(query).sort('ArticleDate', pymongo.DESCENDING)
    Homepageresults = []
    for result in results:
        article = [result["_id"],result["ArticleTitle"],result["ArticleDate"].date().strftime("%d-%m-%Y"),result["CategoryName"],result["AgencyName"]]
        Homepageresults.append(article)
    return Homepageresults


def SelectArticleDetails(db, articleID):
    #Title, Date, URL, Sentiment, ArticleText,CategoryName, Agency Name
    query = {"_id": ObjectId(articleID)}
    selectedcol = db["Articles"]
    result = selectedcol.find_one(query)
    result = [result["ArticleTitle"], result["ArticleDate"], result["ArticleURL"],
                result["SentimentRating"],result["ArticleContent"],
                result["CategoryName"],result["AgencyName"]]
    return result

def LikeArticle(db,userID,articleID):
    query = {"_id": ObjectId(articleID)}
    values = { "$push": { "likeList": str(userID) } }
    selectedcol = db["Articles"]
    result = selectedcol.update_one(query, values)
    if result.matched_count > 0:
        return True
    else:
        return False

def UnlikeArticle(db,userID,articleID):
    query = {"_id": ObjectId(articleID)}
    values = {"$pull": {"likeList": str(userID)}}
    selectedcol = db["Articles"]
    result = selectedcol.update_one(query, values)
    if result.matched_count > 0:
        return True
    else:
        return False

def CheckLike(db,userID,articleID):
    query = {"_id": ObjectId(articleID), "likeList": {"$in": [str(userID)]}}
    selectedcol = db["Articles"]
    result = selectedcol.find_one(query)
    if result != None:
        return True
    else:
        return False

def SelectRecentArticles(db):
    selectedcol = db["Articles"]
    emptylist = []
    for post in selectedcol.find({"ArticleDate": {"$lt": dt.datetime.today(),"$gte": (dt.datetime.today() -dt.timedelta(days=30))}},{"ArticleContent"}):
        emptylist.append(post["ArticleContent"])

    return emptylist


#print(SelectRecentArticles(db))
#print(CheckLike(db,3,"5fb805947eb2da66a5f639a0"))
#print(LikeArticle(db,21,40))
#print(SelectArticleDetails(db,40))
#print(SelectAllArticleTitle(db))
#print(UnlikeArticle(db,3,"5fb805947eb2da66a5f639a0"))