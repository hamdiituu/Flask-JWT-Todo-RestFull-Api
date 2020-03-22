import pymysql.cursors

db = pymysql.connect(       host='remotemysql.com',
                             user='w1oDULvgJe',
                             password='dDMif4qtml',
                             db='w1oDULvgJe',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

conn = db.cursor()

# conn.execute("select * from tblUser")

# users = conn.fetchall()

# for i in users:
#   print(i["Name"])
# query = """
#         insert into tblUser
#         (UserId, Name, NickName, Password)
#         values(%s,%s,%s,%s)
#         """
# values = (2,"Azelya Tuğ","azelyaatuu",121212)


username ="hamdiiuu"

query ="SELECT Count(*) as count FROM tblUser WHERE NickName= %s"

conn.execute(query,(username))
res = conn.fetchone()

print(res["count"])

if res["count"] ==1:
        print(True)
else:
        print(False)


