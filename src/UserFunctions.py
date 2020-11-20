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
    agr = [
        #find row with this id
        { "$match" : {"_id": result["_id"]}},
        #unpack arrays in row
        { "$unwind": '$Order' },
        #sort descending
        { "$sort": {"Order.OrderDate": -1}},
        #select only order
        { "$project":{"Order.OrderDate": 1}}]
    date = list(selectedcol.aggregate(agr))
    date = date[0]["Order"]["OrderDate"]
    #If plan expires
    if date + dt.timedelta(days = 30) < dt.datetime.now():
        result["TierID"] = 1
        query = {"_id": result["_id"]}
        values = {"$set": {"TierID" : 1}}
        selectedcol.update_one(query,values)
    result = [result["_id"], result["UserName"], result["UserPw"], result["TierID"], result["isAdmin"],
              result["CardNo"], result["CardExpiryDate"]]
    return result

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
    Crypt = AESCipher(str(UserID))
    enc_msg = Crypt.encrypt(str(CardNo))
    # Getting UserID
    query = {"_id": UserID}
    selectedcol = db["Users"]
    value = {"$set": { "CardNo": enc_msg, "CardExpiryDate": CardExpiryDate}}
    selectedcol.update_one(query, value)

def SelectUserPayment(db, UserID):
    Crypt = AESCipher(str(UserID))
    # Getting UserID
    query = {"_id": UserID}
    selectedcol = db["Users"]
    result = selectedcol.find_one(query)
    if result == None:
        return result
    dec_msg = Crypt.decrypt(result["CardNo"])
    return [dec_msg,result["CardExpiryDate"]]

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
                  "OrderDate": dt.datetime.today()-dt.timedelta(days = 60)}
    #print(dt.datetime.today())
    values = {"$set": {"TierID": 2},"$push": {"Order": insertdict}}
    query = {"_id": int(UserID)}
    selectedcol = db["Users"]
    result = selectedcol.update_one(query,values)
    if result.matched_count > 0:
        return True
    else:
        return False

#print(Transact(db,23))
#print(InsertPaymentMethod(db,21,"5500 0000 0000 0004","03/21"))
#print(SelectUserPayment(db, 21))
#print(UserAuth(db,"test3","123"))
#print(UserCreate(db,"test3","123"))
#print(SelectLikedArticles(db,21))
#x = AESCipher("1234")
#print(x.decrypt(x.encrypt("data")))
