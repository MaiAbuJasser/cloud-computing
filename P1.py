import sqlite3

def convertToBinaryData(fileName) :
	with open(fileName, 'rb') as file :
		blobData = file.read()
	return blobData

connection_obj = sqlite3.connect('P1.db')
cursor_obj = connection_obj.cursor()
sql = """ INSERT INTO images (key, image)
		  VALUES(?, ?) """
empPhoto = convertToBinaryData("./person.png")
data_tuple = (14897, empPhoto)
cursor_obj.execute(sql, data_tuple) 
print("Ready")
connection_obj.commit()
cursor_obj.close()

