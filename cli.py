import DataBase as db
import os
import shutil
import json

def changeAuthentication():
    print("You chose to change the authentication")
def removeStudent():
    print("You chose to remove a student.")
def removeSection():
    print("You chose to remove a section.")
def backupDatabase():
    print("You chose to backup the database.")

while True:
    print("What do you want to do???")
    print("1.Change username and password.")
    print("2.Remove a student from the database.")
    print("3.Remove a complete section.")
    print("4.Reset Database.(You should back up the database.)")
    print("5.Back up the database.")
    print("Press CTRL + K to close or escape the program.")

    option = input("Your option ::::>")
    
    if option == 1:
        changeAuthentication()
    elif option == 2:
        removeStudent()
    elif option == 3:
        removeSection()
    elif option == 4:
        resetDatabase()
    elif option == 5:
        backupDatabase()
    else:
        print("Please choose an option from 1 to 5.")
