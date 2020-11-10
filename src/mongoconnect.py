import pymongo
import urllib

myclient = pymongo.MongoClient("mongodb://root:" +urllib.parse.quote("ict@2103")+ "mdb@dds-gs5174a84c2af8841124-pub.mongodb.singapore.rds.aliyuncs.com:3717,dds-gs5174a84c2af8842921-pub.mongodb.singapore.rds.aliyuncs.com:3717/admin?replicaSet=mgset-303122826")
mydb = myclient["yueheng_db"]
mycol = mydb["customers"]

mydict = { "name": "John", "address": "Highway 37" }

x = mycol.insert_one(mydict)