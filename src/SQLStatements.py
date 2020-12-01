import hashlib
import mysql.connector as mysql
import datetime as dt

db = mysql.connect(
     host ="rm-gs595dd89hu8175hl6o.mysql.singapore.rds.aliyuncs.com",
     user ="ict1902698psk",
     passwd ="KSP8962091",
     database = "sql1902698psk"
)
cursor = db.cursor()


# admin
# Topic: Percentage of people with different tier privileges.(PIE CHART)
def TierAnalysis(cursor):
    query = "SELECT TierID,Count(*) FROM user Group by TierID"
    cursor.execute(query)
    result = cursor.fetchall()
    return result


# normal user
# Topic: SENTIMENT VALUE WITH CATEGORY NAME---(BAR CHART)
def SentimentValueCategory(cursor):
    query = "SELECT c.CategoryName,a.CategoryID,sum(a.SentimentRating) " \
            "FROM article a ,articlecategory c where a.CategoryID = c.CategoryID " \
            "group by a.CategoryID order by a.CategoryID Asc;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# Topic:Most popular Agency(for article likes)--(bar chart)
def MostArticleLikedAgency(cursor):
    query = "SELECT a.AgencyID,c.AgencyName," \
            "Count(a.AgencyID) FROM article a,likedby b,agency c " \
            "WHERE a.ArticleID = b.ArticleID AND a.AgencyID = c.AgencyID GROUP BY a.AgencyID Order By a.AgencyID";
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# Avg sentiment value for each agency(bar chart)

# Avg sentiment value for specific agency with number
def SpecificAvgSentimentRatingAgencyNum(cursor):
    query = "SELECT AgencyID,avg(SentimentRating) " \
            "FROM sql1902698psk.article " \
            "where agencyID = '1' and ArticleDate >= '2020/10/31' and ArticleDate <= '2020/11/21';"
    cursor.execute(query)
    result = cursor.fetchall()
    return result



# Avg sentiment value for all agency
def AllAvgSentimentRating(cursor):
    query = "SELECT a.AgencyID,b.AgencyName,avg(SentimentRating) " \
            "FROM sql1902698psk.article a,sql1902698psk.agency b  " \
            "Where ArticleDate >= '2020/10/31' and ArticleDate <= '2020/11/21' and a.AgencyID = b.AgencyID  Group By AgencyID;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# User side
# Topic: Percentage of Articles written by different Agencies(PIE CHART)
# Without Agency name
def NumOfArticlesByAgency(cursor):
    query = "Select AgencyID,count(AgencyID) " \
            "from article group by AgencyID order by AgencyID Asc;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# With Agency name
def NumOfArticlesByAgencyWithName(cursor):
    query = "Select a.AgencyID,b.AgencyName,count(a.AgencyID) as 'Number of Article' " \
            "from article a,agency b " \
            "WHERE a.AgencyID=b.AgencyID group by a.AgencyID order by a.AgencyID Asc;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# Topic:TOP 10 MOST LIKES for article(FOR SUGGESTION PAGE INSTEAD)
# Without Article Title
def TopTenMostLikesArticle(cursor):
    query = "SELECT a.ArticleID,Count(a.UserID) as 'Like by' " \
            "FROM likedby a,article b " \
            "WHERE a.ArticleID = b.ArticleID group by a.ArticleID order by Count(a.UserID) desc LIMIT 10;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# With Article Title  (FOR SUGGESTION PAGE)
def TopTenMostLikesArticleWithArticleTitle(cursor):
    query = "SELECT a.ArticleID,b.ArticleTitle,Count(a.UserID) as 'Like by' " \
            "FROM likedby a,article b " \
            "WHERE a.ArticleID = b.ArticleID group by a.ArticleID order by Count(a.UserID) desc LIMIT 10;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# Topic:TOP 10 sentiment value for article(list/bar graph)
# Top 10 sentiment if for specific category
def TopTenSentimentForSpecificCategory(cursor):
    query = "SELECT ArticleID,ArticleTitle,sentimentrating " \
            "FROM sql1902698psk.article " \
            "where categoryID = '1' ORDER BY sentimentrating desc limit 10;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# Worst 10 sentiment value for article
def WorstTenSentimentForSpecificCategory(cursor):
    query = "SELECT ArticleID,ArticleTitle,sentimentrating " \
            "FROM sql1902698psk.article " \
            "where categoryID = '1' ORDER BY sentimentrating asc limit 10;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# TOP 10 if for all category
def TopTenSentimentForAllCategory(cursor):
    query = "SELECT ArticleID,ArticleTitle,sentimentrating FROM sql1902698psk.article " \
            "ORDER BY sentimentrating desc limit 10;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result


# this code
# for specifc Agency
def testNested(cursor, agencyname):
    query = "SELECT AgencyID,avg(SentimentRating)" \
            "FROM sql1902698psk.article " \
            "where agencyID = (Select AgencyID From sql1902698psk.Agency WHERE AgencyName = '{0}') " \
            "and ArticleDate >= '2020/10/31' and ArticleDate <= '2020/11/21' group by AgencyID;".format(agencyname)
    cursor.execute(query)
    result = cursor.fetchall()
    return result

#Counting Payment Method
def TopPaymentMethod(cursor):
    args = (0,0,0)
    result = cursor.callproc('Decryptrow',args)
    result = list(result)
    retresult = []
    #PREP DATA FOR CHART JS
    for count in range(3):
        if(count == 0):
            item = ("MASTERS", result[count])
        elif(count == 1):
            item = ("VISA", result[count])
        else:
            item = ("AMEX", result[count])
        retresult.append(item)
    return retresult

#print(TopPaymentMethod(cursor))
#print(TierAnalysis(cursor))

# print(SentimentValueCategory(cursor))
# print(MostArticleLikedAgency(cursor))
# print(SpecificAvgSentimentRating(cursor))
# print(AllAvgSentimentRating(cursor))
# print(NumOfArticlesByAgency(cursor))
# print(NumOfArticlesByAgencyWithName(cursor))
# print(TopTenMostLikesArticle(cursor))
#print(TopTenMostLikesArticleWithArticleTitle(cursor))
# print(TopTenSentimentForSpecificCategory(cursor))
# print(WorstTenSentimentForSpecificCategory(cursor))
# print(TopTenSentimentForAllCategory(cursor))
# print(testNested(cursor,'Today'))