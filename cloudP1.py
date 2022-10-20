from asyncio.windows_events import NULL
from email import policy
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
con=sqlite3.connect("P1.db")
cur=con.cursor()
cur.execute("INSERT INTO cache (id,policy,hitrate,missrate,capacity,items) VALUES(?,?,?,?,?,?)",(1,'random',0,0,0,0)
con.commit()


@app.route('/')
def main() :
    return render_template("index.html")

@app.route('/request', methods = ['GET','POST'])
def req():  
    global miss, hit, policyy, hitRate, missRate, memcache,totalSize
    if request.method == 'POST' :
        try:
            key = request.form['key']
            con=sqlite3.connect("P1.db")
            cur=con.cursor()
            if key in memcache.keys() :
                name = memcache[key]
                 hit = hit + 1
                 hitRate += hit / (hit + miss)
                 if(max_capacity < totalSize):
                  if policyy == '2' :
                      leastRecentlyUsed(key)
                      totalSize = cur.execute("SELECT SUM(sizeinBytes) FROM images")
                      cur.execute("UPDATE cahce SET policy = ?, capacity = ? WHERE id = ?", ('random',totalSize,1))
                      cur.execute("UPDATE cahce SET hitrate = ? WHERE id = ?", (hitRate, 1))
                      con.commit()
                return render_template('request.html', user_image = ('..\\static\\' + name))
            miss = miss + 1
            missRate += miss / (hit + miss)
            cur.execute("UPDATE cahce SET missrate = ? WHERE id = ?", (missRate, 1))
            con.commit()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            if not isNewKey :
                name = cur.execute("SELECT image FROM images WHERE key = ?", [key]).fetchall()
                if policyy == '2' :
                    leastRecentlyUsed(key)
                    cur.execute("UPDATE cahce SET policy = ? WHERE id = ?", ('LRU', 1))
                    con.commit()
                return render_template('request.html', user_image = ('..\\static\\' + name[0][0]))
            else :
                return render_template('request.html', keyCheck = "key not found !")
        except:
            return("error occur")
        finally:
            con.commit()
            con.close()
    return render_template('request.html')

@app.route('/upload', methods = ['POST','GET']) 
def upload():
    global miss, hit, policyy, hitRate, missRate, memcache,totalSize
    if request.method == 'POST' :
        try:
            key = request.form["key1"]
            image=request.files["image"]
            imagePath = request.form["image1"]
            saveFile(path + image.filename, image.filename, imagePath)
            sizeinBytes = os.path.getsize(imagePath)
            totalSize += sizeinBytes
            con=sqlite3.connect("P1.db")
            cur=con.cursor()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            if(isNewKey) :
                cur.execute("INSERT INTO images (key,image,size) VALUES(?,?,?)",(key, image.filename,sizeinBytes))
                miss += miss
                missRate += miss / (hit+miss)
                if(max_capacity < totalSize):
                  memcache.put('key','image.filename')
                  cur.execute("UPDATE cahce SET missrate = ?,capacity = ? WHERE id = ?", (missRate,totalSize,1))
                  con.commit()
                  done = "Upload Successfully"
                else:
                  print('you have exceeded the max capacity you entered !') 
                
            else :
                cur.execute("UPDATE images SET image = ?,size = ? WHERE key = ?", (image.filename,sizeinBytes, key))
                done = "Update Successfully"
                con.commit()
            if policyy == '1' :
                randomPolicy()
                totalSize = cur.execute("SELECT SUM(sizeinBytes) FROM images")
                cur.execute("UPDATE cahce SET policy = ?, capacity = ? WHERE id = ?", ('random',totalSize,1))
                con.commit()
            else :
                leastRecentlyUsed(key)
                totalSize = cur.execute("SELECT SUM(sizeinBytes) FROM images")
                cur.execute("UPDATE cahce SET policy = ?, capacity = ? WHERE id = ?", ('LRU',totalSize,1))
                con.commit()
            con.close()
            memcache[key] = image.filename
            
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
    

@app.route('/configure', methods = ['POST','GET']) 
def config():
    global miss, hit, policyy, hitRate, missRate, memcache,totalSize
    if request.method == 'POST' :
       try:
            key = request.form["key"]
            global max_capacity
            max_capacity = request.form["Capacity in MB"]
            policyy = request.form["policy"]

            if request.form["clear"] == 'Clear' :
                del memcache[key]
            elif request.form["clearAll"] == 'Clear All' :
                memcache.clear()
                cur.execute("UPDATE cahce SET capacity = ?, items = ? WHERE id = ?", (0,0,1))
                con.commit()
       
       except:
            return 'error'
       finally:
            return render_template('configure.html')
    return render_template('configure.html')

def randomPolicy() :
    global miss, hit, policyy, hitRate, missRate, memcache,totalSize
    if len(memcache) > capacity:
        random.choice(list(memcache.values()))

def leastRecentlyUsed(key) :
    global miss, hit, policyy, hitRate, missRate, memcache
    memcache.move_to_end(key)
    if len(memcache) > capacity:
        memcache.popitem(last = False)

if __name__ == '__main__':
    app.run(debug = True)
