import json
import os
import random
from datetime import datetime
import string
from pathlib import Path
import shutil
writeLogs = True
maxEntryLimit = 30
dateFormat = "%d/%m/%y %H:%M:%S"
# Get Current Path and define all the file names
currentPath = os.getcwd()
studentNamesListFileName = "\\studentList.json"
configFile = "\\configurations.json"
logFileName = "\\log.txt"
sections = []

fixedSetOfFiles = []

# Config variables
config = {
	"sectionCount": 0,
	"studentCount": 0,
	"sections":[],
	"lastUID": 0
}

# Formats for all the data
studentListFormat = {
	"names" : [],
	"uids" : []
}

entryFormat = {"date": "19/10/2020 19:32:19", "pulse": 69, "temperature": 96.0}

studentDataFormat = {
	"name": "Student Name",
	"uid": 1129081231231,
	"standard": 10,
	"division": 'A',
	"entries":[entryFormat, entryFormat]
}

# Data is separated in sections. Each section data is stored in a folder with name in the format "sectionName"
# There is also a single file containing student names and their uids
# Data is stored in json files with name of the student's Unique ID.

# Check if the config file exists, if not create one, and then read all the configurations.
def getConfig():
	empty = False
	with open(currentPath + configFile, "r") as file:
		if file.read() == "": empty = True
	if not os.path.exists(currentPath + configFile) or empty:
		file = open(currentPath + configFile, "w")
		json.dump(config, file)
		file.close()
	with open(currentPath + configFile, "r") as file:
		data = json.load(file)
		config['studentCount'] = data['studentCount']
		config['sectionCount'] = data['sectionCount']
		config['sections'] = data['sections']
		config['lastUID'] = data['lastUID']
		sections = config['sections']
		file.close()
	print(config)


# Check is any of the section folders or studentNameLists are missing or not, also check the number of student Files
def checkMissingFiles():
	listOfMissingFiles = []
	for section in config["sections"]:
		file = currentPath + section + studentNamesListFileName
		if not os.path.exists(file):
			listOfMissingFiles.append(file)
	return listOfMissingFiles

# Create files if they are missing 
def createFiles():
	listOfMissingFiles = checkMissingFiles()
	if len(listOfMissingFiles) > 0:
		for fileName in listOfMissingFiles:
			try:
				with open(fileName, "w") as file:
					json.dump(studentListFormat, file, indent = 4)
					file.close()
			except FileNotFoundError:
				os.mkdir(fileName[:fileName.rindex("\\")])
				with open(fileName, "w") as file:
					json.dump(studentListFormat, file, indent = 4)
					file.close()
			except Exception as e:
				print("We tried")
				print(str(e))
				print("Removing that section from the configurations.")
				config['sections'].remove(fileName[fileName.index("\\") + 1:fileName.rindex("\\")])
				config['sectionCount'] -= 1

				with open(currentPath + sectionName, "w") as file:
					json.dump(config, file, indent = 4)
					file.close()

				print(config)


# Add a student's data, add their entry in the studentNameList for the respective section
# Increase the student count in main configurations
def addStudent(sectionName, studentUID, name, division, standard):
	#Adding Entry in main list and updating config file
	getConfig()
	if not os.path.exists(currentPath + sectionName + studentNamesListFileName):
		return sectionName + " does not exist."
	if os.path.exists(currentPath + sectionName + "\\{}.json".format(str(studentUID))):
		return "Student with UID number {} and name {} already exists in {}".format(studentUID, name, sectionName)
	
	config["studentCount"] += 1
	config["lastUID"] = studentUID
	with open(currentPath + configFile, "r+") as file:
		file.seek(0)
		json.dump(config, file, indent = 4)
		file.truncate()
		file.close()
		
	# Creating student data.
	data = studentDataFormat
	data["name"] = name
	data["uid"] = studentUID
	data["standard"] = standard
	data["division"] = division
	data["entries"] = []

	# Creating student file and adding their data
	with open(currentPath + sectionName + "\\{}.json".format(str(studentUID)), "w") as file:
		json.dump(data, file, indent = 4)
		file.close()

	# Add student name in the section's student name list file
	with open(currentPath + sectionName + studentNamesListFileName, "r+") as file:
		data = json.load(file)
		data["names"].append(name)
		data["uids"].append(studentUID)
		file.seek(0)
		json.dump(data, file, indent = 4)
		file.truncate()
		file.close()

	return "Student with UID number {} is added to {}".format(str(studentUID), sectionName)

# Add a new section, add its folder, add the sectionName in the main configurations.
# Create a studentList file for the particular section
def addSection(sectionName = "\\section"):
	# Create the directrory
	if sectionName[0] != "\\":
		sectionName = "\\" + sectionName
	if not os.path.exists(currentPath + sectionName):
		os.mkdir(currentPath + sectionName)
	else:
		return "The section {} already exists.".format(sectionName)
	config["sections"].append(sectionName)

	# Adding section name to the config file
	with open(currentPath + configFile, "r+") as file:
		data = json.load(file)
		data["sectionCount"] += 1
		data["sections"].append(sectionName)
		file.seek(0)
		json.dump(data, file, indent = 4)
		file.truncate()
		file.close()

	# Creating a student name list
	if not os.path.exists(currentPath + sectionName + studentNamesListFileName):
		with open(currentPath + sectionName + studentNamesListFileName, "w") as file:
			data = studentListFormat
			data['names'] = []
			data['uids'] = []
			json.dump(data, file, indent = 4)
			file.close()
	return "Created a new section with the name {}".format(sectionName)

# Add a new entry for a particular student, maximum entries is 30 
# If entry number exceeds limit, delete the oldest entry
# Need the date in a string format.
def addNewEntry(sectionName, studentUID, pulseRate, temperature, date):
	#Create json data
	data = entryFormat
	try:
		dateTime = datetime.strptime(date, dateFormat)
	except Exception as e:
		print(str(e))
		date = "00/00/0000 00:00:00"
	data["date"] = date
	data["pulse"] = int(pulseRate)
	data["temperature"] = float(temperature)

	anotherSection = False
	wrongSection = sectionName
	if not os.path.exists(currentPath + sectionName + "/{}.json".format(str(studentUID))):
		dataFromUID = getStudentDataFromUIDOnly(studentUID)
		if dataFromUID != "":
			sectionName = "\\" + dataFromUID["standard"] + dataFromUID["division"]
			anotherSection = True

	if not os.path.exists(currentPath + sectionName + "/{}.json".format(str(studentUID))):
		return "Student with UID number {} in {} does not exist".format(str(studentUID), sectionName)

	#Add data entry to student file
	with open(currentPath + sectionName + "/{}.json".format(str(studentUID)), "r+") as file:
		fileData = json.load(file)
		if len(fileData["entries"]) > maxEntryLimit:
			fileData["entries"].pop(0)	
		fileData["entries"].append(data)
		file.seek(0)
		json.dump(fileData, file, indent = 4)
		file.truncate()
		file.close()

	if anotherSection:
		return "New entry added for Student with UID number {} in class {} because student did not exist in {}".format(str(studentUID), sectionName, wrongSection) 
	return "New entry added for Student with UID number {} in class {}".format(str(studentUID), sectionName) 


# Get a students complete data file
def getStudentData(sectionName, studentUID):
	data = studentDataFormat

	if not os.path.exists(currentPath + sectionName + "\\{}.json".format(studentUID)):
		print("Student with uid  " + str(studentUID) + " does not exist in section " + sectionName + ".")
		return getStudentDataFromUIDOnly(studentUID)
	with open(currentPath + sectionName + "\\{}.json".format(studentUID), "r") as file:
		fileData = json.load(file)
		data["name"] = fileData["name"]
		data["uid"] = fileData["uid"]
		data["standard"] = fileData["standard"]
		data["division"] = fileData["division"]
		data["entries"] = fileData["entries"]
		file.close()
	return data
# Get a student's data from uid only
def getStudentDataFromUIDOnly(studentUID):
	data = studentDataFormat
	section = ""

	# Search the student's data file in all sections
	for sectionName in config["sections"]:
		if os.path.exists(currentPath + sectionName + "\\{}.json".format(studentUID)):
			section = sectionName
	if section == "":
		return ""
	with open(currentPath + section + "\\{}.json".format(studentUID), "r") as file:
		fileData = json.load(file)
		data["name"] = fileData["name"]
		data["uid"] = fileData["uid"]
		data["standard"] = fileData["standard"]
		data["division"] = fileData["division"]
		data["entries"] = fileData["entries"]
		file.close()

	return data

def getStudentUIDList(sectionName):
	if sectionName[0] != "\\":
		sectionName = "\\" + sectionName
	studentUIDs = []
	if sectionName in config["sections"]:
		with open(currentPath + sectionName + studentNamesListFileName, "r") as file:
			fileData = json.load(file)
			studentUIDs = fileData["uids"]
	else:
		print(sectionName + " this is not available.")
	return studentUIDs

def getCompleteSection(sectionName):
	#Returns a dicitonary with only an array of studentDataFormats
	uids = getStudentUIDList(sectionName)
	studentDatas = {
		"students":[]
	}
	for uid in uids:
		studentDatas["students"].append(getStudentData(sectionName, uid))
	return studentDatas

# Get a students complete data including all the entries.
def getHealthValues(sectionName, studentUID):
	readingDates = []
	pulseReadings = []
	temperatureReadings = []

	data = getStudentData(sectionName, studentUID)
	for entry in data['entries']:
		readingDates.append(entry['date'])
		pulseReadings.append(entry['pulse'])
		temperatureReadings.append(entry['temperature'])
	testingpurposeprintfunction(data)

	return readingDates, pulseReadings, temperatureReadings

def getSectionList():
	return config['sections']

def testingpurposeprintfunction(data):
	print("Name :", data['name'])
	print("UID :", data['uid'])
	print("Standard :", data['standard'])
	print("Division :", data['division'])


def deleteStudent(studentUID, sectionName):
	studentFile = currentPath + sectionName + "//{}.json".format(studentUID)
	studentName = ""
	if os.path.exists(studentFile):
		os.remove(studentFile)
	else:
		return "Student with UID {} does not exist in section {}.".format(studentUID, sectioName)
	with open(currentPath + sectionName + studentNamesListFileName, "r+") as file:
		data = json.load(file)
		i = data["uids"].index(int(studentUID))
		data["uids"].remove(studentUID)
		studentName = data["names"].pop(i)
		file.seek(0)
		json.dump(data, file, indent = 4)
		file.truncate()
		file.close()

	config["studentCount"] -= 1
	with open(currentPath + configFile, "w") as file:
		json.dump(config, file, indent = 4)
		file.close()

	return "Student {} with UID {} has been deleted from section {}.".format(studentName, str(studentUID), sectionName)

def deleteSection(sectionName):
	if not os.path.exists(currentPath + sectionName):
		return "Section {} does not exist.".format(sectionName)
	try:
		os.chmod(currentPath + sectionName, 0o777)
		shutil.rmtree(currentPath + sectionName)

		config['sectionCount'] -= 1
		config['sections'].remove(sectionName)
		print(config)
		with open(currentPath + configFile, "w") as file:
			json.dump(config, file, indent = 4)
			file.close()

		return "Section {} is deleted from existence.".format(sectionName)
	except Exception as e:
		return str(e)


# VERY DANGEROUS, DELETES ALL DATA
def resetData():
	with open(currentPath + configFile, "r+") as file:
		data = json.load(file)
		for section in data['sections']:
			x = 0
			while True:
				try:
					os.rename(currentPath + section, currentPath + section + "redundant" + str(x))
					break
				except FileNotFoundError:
					print(currentPath + section + " not found.")
					x += 1
					break
		data["sections"] = []
		data['sectionCount'] = 0
		data['studentCount'] = 0
		data['lastUID'] = 0
		file.seek(0)
		json.dump(data, file, indent = 4)
		file.truncate()
		file.close()


def generateUID():
	uid = config['lastUID'] + 1
	return uid

# Function only for testing
def generate4Sections():
	addSection("10A")
	addSection("10B")
	addSection("10C")
	addSection("10D")

# Function only for testing
def generateRandomData():
	for section in config['sections']:
		print(section)
		for lol in range(40):
			newStudent = studentDataFormat
			newStudent['name'] = "".join([random.choice(string.ascii_lowercase) for x in range(13)])
			newStudent['uid'] = generateUID()
			newStudent['standard'] = section[1:-1]
			newStudent['division'] = section[-1]
			addStudent(section, newStudent['uid'], newStudent['name'], newStudent['standard'], newStudent['division'])
			for yay in range(32):
				addNewEntry(section, newStudent['uid'], random.randint(60, 100), random.uniform(80.0, 160.0), 
						"10/23/20 17:39:25")



#resetData()
getConfig()
createFiles()
#generate4Sections()
#generateRandomData()