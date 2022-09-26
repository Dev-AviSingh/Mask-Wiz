from flask import *
import DataBase as db
import json
import os
from datetime import datetime
from getmac import get_mac_address

app = Flask(__name__)
host = "192.168.0.100"
port = "80"

username = "admin"
password = "123456"

currentPath = os.getcwd()
logFilePath = "\\logs.txt"

# Create password file and make a system ot change password from the cli, in the cli file.

global targetPage
targetPage = "mainPage"
if not os.path.exists(currentPath + logFilePath):
	file = open(currentPath + logFilePath, "w")
	file.close()
else:
	with open(currentPath + logFilePath, "a") as file:
		file.write("Server started on " + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + "." + "\n")
		file.close()


global allowAccess
allowAccess = False
def logAccess(log):
	with open(currentPath + logFilePath, "a") as file:
		file.write(log + "\n")
		file.close()
def getMacForIp(ip_):
	mac = get_mac_address(ip=ip_)
	if mac == None:
		return "Not Found"
	return mac

@app.route('/favicon.ico', methods=["GET"])
def favIcon():
	if request.method == "GET":
		return url_for('static', filename="favicon.ico")
	else: 
		return "nope"
@app.route('/')
def mainPage():
	global allowAccess
	global targetPage
	print("YOOOOO, we got a connection = " + request.remote_addr)
	if allowAccess:
		allowAccess = False
		return render_template('DataPage.html')
	else:
		targetPage = "mainPage"
		return redirect(url_for('loginPage'))

@app.route('/login', methods = ["POST", "GET"])
def loginPage():
	global allowAccess
	global targetPage
	if request.method == "POST":
		if request.form["Username"] == username and request.form["Password"] == password:
			allowAccess = True
			with open(currentPath + logFilePath, "a") as file:
				file.write("Client with IP:{} And Mac:{} logged in on ".format(request.remote_addr, getMacForIp(request.remote_addr)) + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + "." + "\n")
				file.write("Logged in with username:{} password:{}.".format(request.form["Username"], request.form["Password"]) + "\n")
				file.close()

			return redirect(url_for(targetPage))
		else:
			with open(currentPath + logFilePath, "a") as file:
				file.write("Client with IP:{} And Mac:{} tried to log in on ".format(request.remote_addr, getMacForIp(request.remote_addr)) + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + "." + "\n")
				file.write("Tried to log in with username:{} password:{}.".format(request.form["Username"], request.form["Password"]) + "\n")
				file.close()
			return "Authentication failed. Wrong ID or Password."
	return render_template('LoginPage.html')

@app.route('/sectionList', methods = ["GET"])
def sectionList():
		print(db.getSectionList())
		return " ".join(x[1:] for x in db.getSectionList())

@app.route('/sectionData/<sectionName>', methods = ["GET"])
def sectionData(sectionName):
	return json.dumps(db.getCompleteSection("\\" + sectionName))

@app.route('/studentList/<sectionName>')
def studentList(sectionName):
	studentList = {
		"uids":[] 
	}
	try:
		studentList["uids"] = db.getStudentUIDList(sectionName)
	except FileNotFoundError as e:
		print(str(e))
		return "This section does not exist."
	jsonifiedArray = json.dumps(studentList)
	print("studentList : " + jsonifiedArray)
	return jsonifiedArray

@app.route('/studentData/<uid>')
def studentData(uid):
	data = json.dumps(db.getStudentDataFromUIDOnly(uid))
	print("data sent for " + str(uid))
	return data

@app.route('/studentDataLatest/<uid>')
def studentDataLatest(uid):
	data = db.getStudentDataFromUIDOnly(uid)
	data = json.dumps(data)
	print("Latest data sent for " + str(uid))
	return data

@app.route('/loadingImage.gif')
def returnLoadingImage():
	return send_file(os.getcwd() + "/static/loading.gif", "mimetype/gif")

@app.route('/addData', methods=["POST", "GET"])
def addData():
	print(request)
	finalMessage = ""
	global allowAccess
	global targetPage
	if request.method == "POST":
		if request.is_json:
			jsonData = request.json
			print(len(jsonData.keys()))
			jsonData["sectionName"] = jsonData["sectionName"].upper() 
			if not 'date' in jsonData:
				print("New Student Request Received")

				# Check is all the values are present or not and send the client which elements are missing.
				missingValues = []
				neededValues = ['sectionName', 'uid', 'standard', 'division', 'name']
				for x in neededValues:
					if not x in jsonData:
						missingValues.append(x)
				
				if len(missingValues) == 0:
					errorMessages = ""

					# Check and verify the data types of all the values and send the error messages respectively.
					if(type(jsonData['sectionName']) is not str):
						errorMessages += "Section Name value is wrong.\n"
					if(type(jsonData['uid']) is not int):
						errorMessages += "UID value is wrong.\n"
					if(type(jsonData['standard']) is not str):
						errorMessages += "Standard value is wrong.\n"
					if(type(jsonData['division']) is not str):
						errorMessages += "Division value is wrong.\n"
					if(type(jsonData['name']) is not str):
						errorMessages += "Name value is wrong.\n"

					if errorMessages == "":
						result = db.addStudent(jsonData['sectionName'], jsonData['uid'], jsonData['name'], jsonData['division'], jsonData['standard'])
						finalMessage = result
					else:
						finalMessage = errorMessages
				else:
					finalMessage = "Values are missing. Missing values = " + ",".join(missingValues)
			
			elif 'date' in jsonData:
				print("New Entry Request Received")

				# Check is all the values are present or not and send the client which elements are missing.
				missingValues = []
				neededValues = ['sectionName', 'uid', 'pulse', 'temperature', 'date']
				for x in neededValues:
					if not x in jsonData:
						missingValues.append(x)
				
				if len(missingValues) == 0:
					errorMessages = ""

					# Check and verify the data types of all the values and send the error messages respectively.
					if(type(jsonData['sectionName']) is not str):
						errorMessages += "Section Name value is wrong.\n"
					if(type(jsonData['uid']) is not int):
						errorMessages += "UID value is wrong.\n"
					if(type(jsonData['pulse']) is not int):
						errorMessages += "Pulse value is wrong.\n"
					if not (type(jsonData['temperature']) is int or type(jsonData['temperature']) is float):
						errorMessages += "Temperature value is wrong.\n"
						print(jsonData['temperature'])
					if(type(jsonData['date']) is not str):
						errorMessages += "Date value is wrong.\n"
						
					if errorMessages == "":
						result = db.addNewEntry(jsonData['sectionName'], jsonData['uid'], jsonData['pulse'], jsonData['temperature'], jsonData['date'])						
						finalMessage = result
					else:
						finalMessage = errorMessages
				else:
					finalMessage = "Values are missing. Missing values = " + ",".join(missingValues)
			
			else:
				finalMessage = "Error, wrong length of dictionary Received. Length = " + str(len(jsonData))
		else:
			finalMessage = "Non JSON data received."
		
		logAccess("Add data query received from IP:{} Mac:{}".format(request.remote_addr, getMacForIp(request.remote_addr)))
		logAccess(finalMessage)
		return finalMessage
	return render_template("AddDataPage.html")


@app.route("/recordsPage")
def recordsPage():
	return render_template('AccessRecordsPage.html')
	global allowAccess
	global targetPage
	if allowAccess:
		allowAccess = False
		return render_template('AccessRecordsPage.html')
	else:
		targetPage = "recordsPage"
		return redirect(url_for('loginPage'))


@app.route('/generateUID')
def generateUIDForSession():
	print(request.data)
	print("Generate and send UID Request Received. " + str(request.data))
	return str(db.generateUID())

@app.route('/getRecords')
def giveRecords():
	data = ""
	with open(currentPath + logFilePath, "r") as file:
		for x in file.readlines():
			data += x + "<br/>"
		file.close()
	return data

@app.route('/addSection', methods=["POST"])
def addNewSection():
	if request.method == "POST":
		section = str(request.data.decode().upper())
		print(request.data)
		result = db.addSection(section)
		logAccess(result)
		return result

@app.route('/deleteStudent', methods=["POST"])
def deleteStudent():
	uid = -1
	try:
		uid = int(request.data.decode())
	except Exception as e:
		return str(e)
	dat = db.getStudentDataFromUIDOnly(uid)
	if dat == "":
		return "Student does not exist."
	print(dat, uid)
	studentSection = "\\" + dat["standard"] + dat["division"]
	res = db.deleteStudent(uid, studentSection)
	logAccess(res)
	return res


@app.route('/deleteSection', methods=["POST"])
def deleteSection():
	section = request.data.decode().upper()
	if section == "":
		return "Empty request sent."
	if not section[0] == "\\":
		section = "\\" + section
	res = db.deleteSection(section)
	logAccess(res)
	return res

@app.route('/lol', methods=["GET", "POST"])
def loll():
	print("Address accessed is :" + request.remote_addr)
	return "Well Done bitch."
if __name__ == "__main__":
	app.run(host, port, debug=True)