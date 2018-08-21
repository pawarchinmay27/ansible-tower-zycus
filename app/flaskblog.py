from flask import Flask,render_template,request,url_for,redirect,flash,session
from flask_socketio import SocketIO
import sqlite3
from subprocess import call
import paramiko
import os
from time import gmtime,strftime
from constants import Constants
import time
import subprocess
from threading import Thread
from flask_socketio import SocketIO,emit
app=Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
socket=SocketIO(app)
thread=None
threadFlag=False
class PrintDynamic(Thread):
    def __init__(self,filePath):
        self.filePath=filePath
	super(PrintDynamic,self).__init__()

    def run(self):
	self.background_thread()

    def background_thread(self):
	    ssh=paramiko.SSHClient()
	    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	    ssh.connect("127.0.0.1",username="root",key_filename="/root/.ssh/id_rsa")  		
	    print Constants.LOG_PATH
	    fw=open(Constants.LOG_PATH,"a+")
	    stdin,stdout,stderr=ssh.exec_command(Constants.COMMAND_FOR_ANSIBLE+self.filePath)
	    fw.write("---------------------------------------------------------------------------------")
	    showtime=strftime("%Y-%m-%d %H:%M:%S",gmtime())
	    fw.write("\n"+showtime.encode("ascii","ignore"))
	    fw.write("\n"+self.filePath+"\n")
	    for line in iter(stdout.readline,''):
		fw.write(line.encode("ascii","ignore")+"\n")
		print line.encode("ascii","ignore")+"\n"	
	    	socket.emit('my_response',{'data':line})
	    for line in iter(stderr.readline,''):
		fw.write(line+"\n")
		line.encode("ascii","ignore")+"\n"	
		socket.emit('my_response',{'data':line})
	    	


def loadFiles(username):
   for root,dirs,files in os.walk("/root/training/"+username):
	for name in files:
			if name.startswith("."):
				continue
			playbooks.append(os.path.abspath(os.path.join(root,name)))
 
	

	
def execAnsible(fileName):
			ssh=paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
			ssh.connect("127.0.0.1",username="root",key_filename="/root/.ssh/id_rsa")
			stdin,stdout,stderr=ssh.exec_command(Constants.COMMAND_FOR_ANSIBLE+fileName)
			result=stdout.readlines()
			if result == []:
				result=stderr.readlines()			
			return result

def background_thread():
    filePath=session["fileName"]
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("127.0.0.1",username="root",key_filename="/root/.ssh/id_rsa")  		
    print Constants.LOG_PATH
    fw=open(Constants.LOG_PATH,"a+")
    stdin,stdout,stderr=ssh.exec_command(Constants.COMMAND_FOR_ANSIBLE+filePath)
    showtime=strftime("%Y-%m-%d %H:%M:%S",gmtime())
    fw.write("\n"+showtime.encode("ascii","ignore"))
    fw.write("\n"+filePath+"\n")
    for line in iter(stdout.readline,''):
	fw.write(line.encode("ascii","ignore")+"\n")
	print line.encode("ascii","ignore")+"\n"	
    	socket.emit('my_response',{'data':line})
    for line in iter(stderr.readline,''):
	fw.write(line+"\n")
	line.encode("ascii","ignore")+"\n"	
	socket.emit('my_response',{'data':line})
	

@app.route("/home")
def home():
	if 'logged_in' not in session:
		return render_template('login.html')
	else:
		global playbooks
		playbooks=[]
		loadFiles(session["username"])
		return render_template('home.html',playbooks=playbooks)


@app.route("/changeFile")
def changeFile():
	if 'logged_in' not in session:
		return render_template('login.html')
	else:
		args="git pull"
		path="/root/training"	
		p=subprocess.Popen(args.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=path)
		out,err=p.communicate()	
		global playbooks
		playbooks=[]
		loadFiles(session["username"])
		return render_template('changeFiles.html',playbooks=playbooks)


@app.route("/")
@app.route('/login/',methods = ['POST', 'GET'])
def login():
 if request.method == 'POST':
	username = request.form['username']
	password= request.form['password']
	conn = sqlite3.connect('database/usersDb.db')
	c=conn.cursor()
	c.execute('SELECT * FROM users where username=? and password=?',(username,password))
   	for row in c.fetchall():
   		if(len(row)>0):
			session["username"]=username
			session['logged_in']=True
			Constants.setPath(username)
			print Constants.HOST_PATH
			print Constants.VAR_PATH
   			return redirect(url_for("home"))
 return render_template('login.html')


@app.route("/enterVars/changeFileName")
def enterVars():
	if 'logged_in' not in session:
		return render_template('login.html')
	else:
		print  "Writing To File",request.args["changeFileName"]
		session["changeFileName"]=request.args["changeFileName"]
		with open(session["changeFileName"]) as file:
			lines=file.readlines()
		allVars=""
		for line in lines:
			allVars=allVars+line
		print allVars
 	return render_template('defineVars.html',allVars=allVars)

@app.route('/handleVars',methods=['GET','POST'])
def handleVars():
	lines=request.form["vars"]
	with open(session["changeFileName"],'w') as file:
		for item in  lines.split("\n"):
			file.write(item+"\n")	
	return redirect(url_for("home"))

@app.route("/enterAnsible/fileName")
def enterAnsible():
	if 'logged_in' not in session:
		return render_template('login.html')
	else:
		session["fileName"]=request.args["fileName"]
		filePath=session["fileName"]	
		global thread
		thread=PrintDynamic(filePath)
		print "This is file : ",session["fileName"]
		with open(request.args["fileName"]) as file:
			lines=file.readlines()
		ansibleContent=""
		for line in lines:
			ansibleContent=ansibleContent+line
		print ansibleContent
 	return render_template('defineAnsible.html',ansibleContent=ansibleContent)

@app.route("/loadVarsForm")
def loadVarsForm():
	varsKeys=[]
	varsValues=[]
	with open(Constants.VAR_PATH) as file:
			lines=file.readlines()
	for line in lines:
			varsKeys.append(line.split(":")[0].strip())
	for line in lines:
			varsValues.append(line.split(":")[1].strip())
	varsKeys=filter(None,varsKeys)
	varsValues=filter(None,varsValues)
	print varsKeys
	return render_template('varForm.html',vars=zip(varsKeys,varsValues))
	

@app.route("/processVarsForm",methods=['GET','POST'])
def processVarsForm():
	vars=[]
	with open(Constants.VAR_PATH) as file:
			lines=file.readlines()
	for line in lines:
			vars.append(line.split(":")[0].strip())
	vars=filter(None,vars)
	print vars
	for item in vars:
		print request.form[item]
	file=open(Constants.VAR_PATH,'wb+')
	for item in vars:
		file.write(item+":"+request.form[item]+"\n")
	return redirect(url_for('home'))

@app.route('/handleAnsible',methods=['GET','POST'])
def handleAnsible():
    filePath=session["fileName"]
    if 'logged_in' not in session:
		return render_template('login.html')
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("127.0.0.1",username="root",key_filename="/root/.ssh/id_rsa")
    print Constants.LOG_PATH
    fw=open(Constants.LOG_PATH,"a+")
    stdin,stdout,stderr=ssh.exec_command(Constants.COMMAND_FOR_ANSIBLE+filePath)
    showtime=strftime("%Y-%m-%d %H:%M:%S",gmtime())
    fw.write("\n"+showtime.encode("ascii","ignore"))
    fw.write("\n"+filePath+"\n")
    for line in iter(stdout.readline,''):
	fw.write(line.encode("ascii","ignore")+"\n")	
    	emit('my response',{'data':line})
    for line in iter(stderr.readline,''):
	fw.write(line+"\n")	
	emit('my response',{'data':line})     

    return app.response_class(generate(), mimetype='text/plain')

@app.route("/goDynamic",methods=['GET','POST'])
def goDynamic():
	lines=request.form["ansibleContent"]
    	filePath=session["fileName"]		
    	file=open(session["fileName"],'w')
    	for item in  lines.split("\n"):
    		file.write(item+"\n")
	return render_template('socket-io.html')

@socket.on('connect')
def socketExecute():
    if 'logged_in' not in session:
		return render_template('login.html')
    print "Connected To Socket Io"


@socket.on('begin_exec')
def begin_exec():
	filePath=session["fileName"]
	thread=PrintDynamic(filePath)
	thread.start()


@app.route('/logout',methods=['GET','POST'])
def logout():
	session.pop('logged_in',None)
	return render_template("login.html")

@app.route('/viewHistory',methods=['GET','POST'])
def viewHistory():
	if 'logged_in' not in session:
		return render_template('login.html')
	with open(Constants.LOG_PATH) as file:
		lines=file.readlines()
	history=[]
	for line in lines:
		history.append(line)
	print "History ------>",history
	return render_template('viewHistory.html',history=history)

@app.route('/checktest',methods=['GET','POST'])
def checktest():
	print request.args["username"]
	with open('/root/training/'+request.args["username"]+"log.txt") as file:
		lines=file.readlines()
	history=[]
	for line in lines:
		history.append(line)
	print "History ------>",history
	return render_template('viewHistory.html',history=history)
	
if(__name__=='__main__'):
	app.run(debug=True)
