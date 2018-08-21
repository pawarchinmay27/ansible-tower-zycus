import sqlite3

conn = sqlite3.connect('usersDb.db')
print "Opened database successfully";
c=conn.cursor()

def create_table():
	c.execute('CREATE TABLE users (username TEXT, password TEXT)')

def data_enter():
	c.execute("INSERT INTO users VALUES('chinmay.pawar','4545')")
	conn.commit()

def read_from_db():
	username="chinmay.pawar"
	password="4545"
	c.execute('SELECT * FROM users where username=? and password=?',(username,password))
	data=c.fetchall()
	for row in data:
		print row[0]
		print row[1]

create_table()
data_enter()
read_from_db()
conn.close()
