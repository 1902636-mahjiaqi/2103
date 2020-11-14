import hashlib
import datetime as dt
import pymongo
import urllib

# client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
# db = client["ICT2103_Project"]

def UserAuth(db, Username, Password):
    #hash Password
    hash = hashlib.sha256()
    hash.update(Password.encode())
    selectedcol = db["Users"]
    #Find username and password
    result = selectedcol.find_one({"UserName": Username,"UserPw": hash.digest()})
    result = [result["_id"], result["UserName"],result["UserPw"],result["TierID"],result["isAdmin"],result["CardNo"],result["CardExpiryDate"]]
    return result
    # query = "SELECT * FROM user WHERE user.UserName = '{0}' AND UserPw = SHA2('{1}',256)".format(Username,Password)
    # cursor.execute(query)
    # result = cursor.fetchone()
    # #Updating to check whether user have expired his paid priveledges
    # if (result[3] == 2):
    #     query = "SELECT OrderDate FROM order_details WHERE order_details.UserID = '{0}' ORDER BY OrderDate LIMIT 1".format(result[0])
    #     cursor.execute(query)
    #     receipt = cursor.fetchone()
    #     print(receipt[0] + dt.timedelta(days = 30))
    #     print(dt.datetime.now())
    #     #If it expires set it as 1 which is a free user
    #     if (receipt[0] + dt.timedelta(days = 30)) < dt.datetime.now().date():
    #         sql = "UPDATE user SET TierID = 1 WHERE UserID = {0}".format(result[0])
    #         cursor.execute(sql)
    #         db.commit()
    #         result = list(result)
    #         result[3] = 1
    # return result

def UserCreate(db, UserName, Password):
    # Getting UserID
    query = {"_id": "userID"}
    selectedcol = db["counters"]
    result = selectedcol.find_one(query)
    #Increment Value of User ID by one
    selectedcol.find_one_and_update(
        query,
        {'$inc': {'sequence_value': 1}}
    )

    #insert user
    #Hash user password
    hash = hashlib.sha256()
    hash.update(Password.encode())
    selectedcol = db["Users"]
    row = {"_id": result["sequence_value"], "UserName": UserName, "UserPw": hash.digest(),"TierID":1,"isAdmin":0,"CardNo":"-","CardExpiryDate":"-"}
    selectedcol.insert_one(row)

def InsertPaymentMethod(db, cursor, UserID, CardNo, CardExpiryDate):
    pass
    # query = "UPDATE user SET CardNo = AES_ENCRYPT(%s,%s), CardExpiryDate = %s WHERE UserID = %s"
    # val = (CardNo,UserID,CardExpiryDate,UserID)
    # cursor.execute(query, val)
    # db.commit()
    # if cursor.rowcount > 0:
    #     return True
    # else:
    #     return False


def SelectUserPayment(cursor, UserID):
    pass
    # query = "SELECT CAST(AES_DECRYPT(CardNo,{0}) as CHAR),CardExpiryDate FROM user WHERE UserID = {0}".format(UserID)
    # cursor.execute(query)
    # result = cursor.fetchone()
    # return result

def SelectLikedArticles(cursor, UserID):
    pass
    # query = "SELECT a.ArticleID, a.ArticleTitle, a.ArticleDate, c.CategoryName, p.AgencyName " \
    #         "FROM likedby l, article a, agency p, articlecategory c " \
    #         "WHERE l.UserID = {0} AND a.ArticleID = l.ArticleID AND a.AgencyID = p.AgencyID AND a.CategoryID = c.CategoryID".format(UserID)
    # cursor.execute(query)
    # result = cursor.fetchall()
    # return result

def Transact(db,cursor,UserID):
    pass
    # try:
    #     #Insert Receipt
    #     query = "INSERT INTO order_details VALUES (%s,%s,%s,%s)"
    #     val = (0, 10, dt.datetime.now().date(),UserID)
    #     cursor.execute(query, val)
    #     #Update the person's tier
    #     query = "UPDATE user SET TierID = 2 WHERE UserID = {0}".format(UserID)
    #     cursor.execute(query)
    #     db.commit()
    #     return True
    # except:
    #     return False

#print(Transact(db,cursor,8))
#print(UserAuth(db,"test","123"))
#print(InsertPaymentMethod(db,cursor,7,"5500 0000 0000 0004","03/21"))
#print (SelectUserPayment(cursor, 7))
#print(UserAuth(cursor,"test","1234"))
#UserCreate(db,"test","123")
#print(SelectLikedArticles(cursor,7))