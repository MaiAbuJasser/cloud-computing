from typing import Hashable
from PIL import Image
import os
from lib2to3.pytree import convert
import sqlite3
from flask import Flask,render_template,request,flash,redirect, session,url_for, json

app = Flask(__name__)
path = '.\\static\\'

my_hash = {}

@app.route('/')
def main() :
    return render_template("index.html")

@app.route('/request', methods = ['GET','POST'])
def req():
    if request.method == 'POST' :
             key = request.form['key']
             if 'key' in my_hash.keys():
              myimg=my_hash.get(key)
             return render_template('request.html', user_image = ('..\\static\\'+myimg))
             cur.execute("SELECT key FROM images WHERE key = ?", [key])
             isNewKey = len(cur.fetchall()) == 0
            if not isNewKey:
                con=sqlite3.connect("P1.db")
                cur=con.cursor()                    
                name = cur.execute("SELECT image FROM images WHERE key = ?", [key]).fetchall()
                my_hash.put(key,name)
                return render_template('request.html', user_image = ('..\\static\\' + name[0][0]))
            else :
                return 'key is not found !'
                 con.commit()
                 con.close()
    return render_template('request.html')

@app.route('/upload', methods = ['POST','GET']) 
def upload():
    if request.method == 'POST' :
        try:
            print(request.method)
            key = request.form["key1"]
            image=request.files["image"]
            imagePath = request.form["image1"]
            myImg = saveFile(path + image.filename, image.filename, imagePath)
            con=sqlite3.connect("P1.db")
            cur=con.cursor()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            if(isNewKey) :
                cur.execute("INSERT INTO images (key,image) VALUES(?,?)",(key, image.filename))
                my_hash.put(key,"image.filename")
                
            else :
                cur.execute("UPDATE images SET image = ? WHERE key = ?", (image.filename, key))
                my_hash[key]="image.filename"
            con.commit()
            con.close()
        except:
            return 'error'
        finally:
            return render_template('upload.html')
    return render_template('upload.html')

@app.route('/list', methods = ['POST','GET']) 
def keyList():
    if request.method == 'GET' :
        try:
            con=sqlite3.connect("P1.db")
            cur=con.cursor()
            cur.execute("SELECT key FROM images")
            con.commit()
            # con.close()
        except:
            return 'error'
        finally:
            return render_template('KeyList.html', keys = [str(val[0]) for val in cur.fetchall()])
    return render_template('KeyList.html')

def saveFile(savedFile, originalFile, originalFilePath) :
    file = Image.open(os.path.join(originalFilePath, originalFile))
    file.save(savedFile)
    

if __name__ == '__main__':
    app.run(debug = True)
