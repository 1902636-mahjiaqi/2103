import mysql.connector as mysql

db = mysql.connect(
    host ="rm-gs595dd89hu8175hl6o.mysql.singapore.rds.aliyuncs.com",
    user ="ict1902698psk",
    passwd ="KSP8962091",
    database = "sql1902698psk"
)

cursor = db.cursor()
cursor.execute("SELECT* FROM user")
records = cursor.fetchall()

for record in records:
    print(record)

print(db)