import hashlib
import datetime as dt
import pymongo
import urllib
import base64
from Crypto.Cipher import AES
from Crypto import Random

# client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
# db = client["ICT2103_Project"]

class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def UserAuth(db, Username, Password):

    #hash Password
    hash = hashlib.sha256()
    hash.update(Password.encode())
    selectedcol = db["Users"]
    #Find username and password
    result = selectedcol.find_one({"UserName": Username,"UserPw": hash.digest()})
    if result == None:
        return result
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
    row = {"_id": result["sequence_value"], "UserName": UserName, "UserPw": hash.digest(),"isAdmin":0, "TierID": 1,
            "CardNo":"-","CardExpiryDate":"-",
            "Order":[],"ArticleAccess": 1, "WordCloud": 0, "BarCharts": 0, "Sentiment": 1
           }
    selectedcol.insert_one(row)
    result = selectedcol.find().sort("_id", -1).limit(1)
    result = result[0]
    result = [result["_id"], result["UserName"], result["UserPw"], result["TierID"], result["isAdmin"],
              result["CardNo"], result["CardExpiryDate"]]
    return result

def InsertPaymentMethod(db, UserID, CardNo, CardExpiryDate):

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

def SelectLikedArticles(db, UserID):
    query = {"likeList": {"$in": [UserID]}}
    selectedcol = db["Articles"]
    results = selectedcol.find(query)
    LikeArticleArray = []
    if results == None:
        return results
    for result in results:
        result = [result["_id"],result["ArticleTitle"],result["ArticleDate"],result["CategoryName"],result["AgencyName"]]
        LikeArticleArray.append(result)
    return LikeArticleArray


def Transact(db,UserID):
    insertdict = {"Price": 10,
                  "OrderDate": dt.datetime.today()}
    print(dt.datetime.today())
    values = {"$set": {"TierID": 2},"$push": {"Order": insertdict}}
    query = {"_id": int(UserID)}
    selectedcol = db["Users"]
    result = selectedcol.update_one(query,values)
    if result.matched_count > 0:
        return True
    else:
        return False

#print(Transact(db,21))
#print(UserAuth(db,"test","123"))
#print(InsertPaymentMethod(db,cursor,7,"5500 0000 0000 0004","03/21"))
#print (SelectUserPayment(cursor, 7))
#print(UserAuth(db,"test2","123"))
#print(UserCreate(db,"test","123"))
#print(SelectLikedArticles(db,21))
#x = AESCipher("1234")
#print(x.decrypt(x.encrypt("data")))
