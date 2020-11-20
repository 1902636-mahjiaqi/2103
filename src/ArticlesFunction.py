import pymongo
import datetime as dt
import hashlib

client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client["ICT2103_Project"]

def SelectAllArticleTitle(db):
    query = {}
    selectedcol = db["Articles"]
    results = selectedcol.find(query)
    Homepageresults = []
    for result in results:
        article = [result["_id"],result["ArticleTitle"],result["ArticleDate"],result["CategoryName"],result["AgencyName"]]
        Homepageresults.append(article)
    return Homepageresults


def SelectArticleDetails(db, articleID):
    #Title, Date, URL, Sentiment, ArticleText,CategoryName, Agency Name
    query = {"_id": int(articleID)}
    selectedcol = db["Articles"]
    result = selectedcol.find_one(query)
    result = [result["ArticleTitle"], result["ArticleDate"], result["ArticleURL"],
                result["SentimentRating"],result["ArticleContent"],
                result["CategoryName"],result["AgencyName"]]
    return result

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

def CheckLike(db,userID,articleID):
    query = {"_id": articleID, "likeList": {"$in": [userID]}}
    selectedcol = db["Articles"]
    result = selectedcol.find_one(query)
    if result != None:
        return True
    else:
        return False

def SelectRecentArticles(db):
    date = dt.datetime.today().date()
    selectedcol = db["Articles"]
    start = dt.datetime(2019, 11, 20, 0, 0, 0, 0)
    end = dt.datetime(2020, 11, 20, 0, 0, 0, 0)

    for doc in selectedcol.find({'time': {'$gte': start, '$lt': end}}):
        print(doc)
    return
    #print(date.isoformat())
    #"ArticleDate": {"$lte": "new Date()", "$gt": (date - dt.timedelta(days=1)).isoformat()}
    query = {"ArticleDate": { "$gte": "ISODate('2019-11-20Z')", "$lt": "ISODate('2020-11-21Z')"}}

    results = list(selectedcol.find(query))
    print(results)
    # for i in results:
    #     print(i)
    #print(results)
    #This function is to select the past 24 hours of articles so as to generate the word cloud
    # query = "SELECT ArticleText FROM article WHERE ArticleDate >= date_sub(curdate(), interval 1 day)"
    # cursor.execute(query)
    # result = cursor.fetchall()
    # return result


print(SelectRecentArticles(db))
#print(CheckLike(db,21,40))
#print(LikeArticle(db,21,40))
#print(SelectArticleDetails(db,40))
#print(SelectAllArticleTitle(db))
#print(UnlikeArticle(db,21,40))