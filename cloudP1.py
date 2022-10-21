from asyncio.windows_events import NULL
from glob import glob
from re import S
from PIL import Image
import os
from lib2to3.pytree import convert
import sqlite3
from flask import Flask,render_template,request,flash,redirect, session,url_for, json
import random
from collections import OrderedDict


app = Flask(__name__)
path = '.\\static\\'
memcache = {}
hit = 0
miss = 0
hitRate = 0
missRate = 0
policyy = '1'
totalSize = 0
capacity = 100000
sql = []
con = sqlite3.connect("P1.db")
cur = con.cursor()    
cur.execute("INSERT INTO cache (policy,hitRate,missRate,capacity,items) VALUES(?,?,?,?,?)",(policyy, hitRate, missRate, capacity, len(memcache)))
con.commit()
con.close()

@app.route('/')
def main() :
    return render_template("index.html")

@app.route('/request', methods = ['GET','POST'])
def req():  
    global miss, hit, policyy, hitRate, missRate, memcache, totalSize, con, cur
    if request.method == 'POST' :
        try:
            con = sqlite3.connect("P1.db")
            cur = con.cursor()    
            key = request.form['key']
            if key in memcache.keys() :
                name = memcache[key]
                leastRecentlyUsed(key)
                hit = hit + 1
                hitRate = hitRate + ( hit / (hit + miss))
                cur.execute("UPDATE cache SET hitRate = ? WHERE id = ?", (hitRate,1))
                con.commit()
                return render_template('request.html', user_image = ('..\\static\\' + name))
            miss = miss + 1
            missRate = missRate + (miss / (hit + miss))
            cur.execute("UPDATE cache SET missRate = ? WHERE id = ?", (missRate, 1))
            con.commit()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            if not isNewKey :
                name = cur.execute("SELECT image FROM images WHERE key = ?", [key]).fetchall()
                memcache.put(key, name[0][0])
                leastRecentlyUsed(key)
                return render_template('request.html', user_image = ('..\\static\\' + name[0][0]))
            else :
                return render_template('request.html', keyCheck = "key not found !")
        except:
            return("error occur")
        finally:
            con.close()
    return render_template('request.html')

@app.route('/upload', methods = ['POST','GET']) 
def upload():
    global miss, hit, policyy, hitRate, missRate, memcache, totalSize
    if request.method == 'POST' :
        try:
            con = sqlite3.connect("P1.db")
            curr = con.cursor() 
            key = request.form["key1"]
            image = request.files["image"]
            imagePath = request.form["image1"]
            sizeInBytes = os.path.getsize(imagePath)
            totalSize = totalSize + sizeInBytes
            curr.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(curr.fetchall()) == 0
            if(isNewKey) :
                curr.execute("INSERT INTO images (key,image,size) VALUES(?,?,?)",(key, image.filename, sizeInBytes))            
                curr.execute("UPDATE cache SET missRate = ?,capacity = ? WHERE cache.id", (missRate, totalSize))
                done = "Upload Successfully"
            else :
                curr.execute("UPDATE images SET image = ?,size = ? WHERE key = ?", (image.filename, sizeInBytes, key))
                done = "Update Successfully"
            con.commit()
            con.close()
            miss = miss + 1
            missRate = missRate + (miss / (hit + miss))
            totalImagesSize()
            randomPolicy() if policyy == '1' else leastRecentlyUsed(key)
            memcache[key] = image.filename
            print(memcache)
        except:
            return 'error'
        finally:
            return render_template('upload.html', done = done)
    return render_template('upload.html')

@app.route('/list', methods = ['POST','GET']) 
def keyList():
    global miss, hit, policyy, hitRate, missRate, memcache
    if request.method == 'GET' :
        try:
            con = sqlite3.connect("P1.db")
            cur = con.cursor()    
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
    

@app.route('/config', methods = ['POST','GET']) 
def config():
    global miss, hit, policyy, hitRate, missRate, memcache, totalSize, capacity
    if request.method == 'POST' :
       try:
            con = sqlite3.connect("P1.db")
            cur = con.cursor()    
            key = request.form["key"]
            capacity = request.form["Capacity in MB"] * 1000
            policyy = request.form["policy"]

            if request.form["clear"] == 'Clear' :
                del memcache[key]
            elif request.form["clearAll"] == 'Clear All' :
                memcache.clear()
                cur.execute("UPDATE cache SET capacity = ?, items = ? WHERE cache.id", (0, len(memcache)))
                con.commit()
       
       except:
            return 'error'
       finally:
            return render_template('configure.html')
    return render_template('configure.html')

def randomPolicy() :
    global capacity, totalSize
    if totalSize > capacity:
        memcache.popitem(random.choice(list(memcache.values())))

def leastRecentlyUsed(key) :
    global memcache, totalSize
    memcache.move_to_end(key)
    if totalSize > capacity:
        memcache.popitem(last = False)

def totalImagesSize() :
    global memcache, totalSize
    con = sqlite3.connect("P1.db")
    cur = con.cursor()    
    totalSize = cur.execute("SELECT SUM(size) FROM images").fetchall()[0][0]
    con.close()

if __name__ == '__main__':
    app.run(debug = True)
