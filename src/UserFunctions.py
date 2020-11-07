import hashlib
import mysql.connector as mysql
import datetime as dt
#
# db = mysql.connect(
#     host ="rm-gs595dd89hu8175hl6o.mysql.singapore.rds.aliyuncs.com",
#     user ="ict1902698psk",
#     passwd ="KSP8962091",
#     database = "sql1902698psk"
# )
# cursor = db.cursor()

def UserAuth(db, cursor, Username, Password):
    query = "SELECT * FROM user WHERE user.UserName = '{0}' AND UserPw = SHA2('{1}',256)".format(Username,Password)
    cursor.execute(query)
    result = cursor.fetchone()
    #Updating to check whether user have expired his paid priveledges
    if (result[3] == 2):
        query = "SELECT OrderDate FROM order_details WHERE order_details.UserID = '{0}' ORDER BY OrderDate LIMIT 1".format(result[0])
        cursor.execute(query)
        receipt = cursor.fetchone()
        print(receipt[0] + dt.timedelta(days = 30))
        print(dt.datetime.now())
        #If it expires set it as 1 which is a free user
        if (receipt[0] + dt.timedelta(days = 30)) < dt.datetime.now().date():
            sql = "UPDATE user SET TierID = 1 WHERE UserID = {0}".format(result[0])
            cursor.execute(sql)
            db.commit()
            result = list(result)
            result[3] = 1
    return result

def UserCreate(db, cursor, UserName, Password):
    try:
        query = "INSERT INTO user VALUES (%s, %s, SHA2(%s,256), DEFAULT(TierID), DEFAULT(isAdmin),DEFAULT,DEFAULT)"
        val = (0, UserName,Password)
        cursor.execute(query, val)
        db.commit()
        return True
    except:
        return False


def InsertPaymentMethod(db, cursor, UserID, CardNo, CardExpiryDate):
    query = "UPDATE user SET CardNo = AES_ENCRYPT(%s,%s), CardExpiryDate = %s WHERE UserID = %s"
    val = (CardNo,UserID,CardExpiryDate,UserID)
    cursor.execute(query, val)
    db.commit()
    if cursor.rowcount > 0:
        return True
    else:
        return False


def SelectUserPayment(cursor, UserID):
    query = "SELECT CAST(AES_DECRYPT(CardNo,{0}) as CHAR),CardExpiryDate FROM user WHERE UserID = {0}".format(UserID)
    cursor.execute(query)
    result = cursor.fetchone()
    return result

def SelectLikedArticles(cursor, UserID):
    query = "SELECT a.ArticleID, a.ArticleTitle, a.ArticleDate, c.CategoryName, p.AgencyName " \
            "FROM likedby l, article a, agency p, articlecategory c " \
            "WHERE l.UserID = {0} AND a.ArticleID = l.ArticleID AND a.AgencyID = p.AgencyID AND a.CategoryID = c.CategoryID".format(UserID)
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def Transact(db,cursor,UserID):
    try:
        #Insert Receipt
        query = "INSERT INTO order_details VALUES (%s,%s,%s,%s)"
        val = (0, 10, dt.datetime.now().date(),UserID)
        cursor.execute(query, val)
        #Update the person's tier
        query = "UPDATE user SET TierID = 2 WHERE UserID = {0}".format(UserID)
        cursor.execute(query)
        db.commit()
        return True
    except:
        return False

#print(Transact(db,cursor,8))
#print(UserAuth(db,cursor,"test1","123"))
#print(InsertPaymentMethod(db,cursor,7,"5500 0000 0000 0004","03/21"))
#print (SelectUserPayment(cursor, 7))
#print(UserAuth(cursor,"test","1234"))
#UserCreate(db,cursor,"","1234")
#print(SelectLikedArticles(cursor,7))