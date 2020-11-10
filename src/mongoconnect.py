import pymongo

myclient = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
mydb = myclient["ICT2103_Project"]
mycol = mydb["counters"]

#mydict = { "_id": "userID", "sequence_value": 0 }
#mycol.insert_one(mydict)

# selectedcol = db["Users"]
# mydict = {"name": "John", "address": "Highway 37"}


