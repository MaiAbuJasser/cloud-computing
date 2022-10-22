from PIL import Image
import os
import sqlite3
from flask import Flask,render_template,request
import random
from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler

def insertCacheTableData() :
    global policyy, hitRate, missRate, capacity, memcache
    con = sqlite3.connect("P1.db")
    cur = con.cursor()    
    cur.execute("INSERT INTO cache (policy,hitRate,missRate,capacity,items) VALUES(?,?,?,?,?)",(policyy, hitRate, missRate, capacity, len(memcache)))
    con.commit()
    con.close()

sched = BackgroundScheduler(daemon=True)
sched.add_job(insertCacheTableData,'interval',seconds=5)
sched.start()

# atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)
path = '.\\static\\'
memcache = OrderedDict()
hit = 0
miss = 0
hitRate = 0
missRate = 0
policyy = '1'
totalSize = 0
capacity = 1000000

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
                con.commit()
            else :
                miss = miss + 1
                missRate = missRate + (miss / (hit + miss))
                con.commit()
                cur.execute("SELECT key FROM images WHERE key = ?", [key])
                isNewKey = len(cur.fetchall()) == 0
                if not isNewKey :
                    name = cur.execute("SELECT image FROM images WHERE key = ?", [key]).fetchall()[0][0]
                    memcache[key] = name
                    leastRecentlyUsed(key)
                else :
                    return render_template('request.html', keyCheck = "key not found !")

                return render_template('request.html', user_image = ('..\\static\\' + name))
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
            cur = con.cursor() 
            key = request.form["key1"]
            image = request.files["image"]
            imagePath = request.form["image1"]
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            saveFile(path + image.filename, image.filename, imagePath)
            sizeInBytes = os.stat(path + image.filename).st_size
            totalSize = totalSize + sizeInBytes
            if(isNewKey) :
                cur.execute("INSERT INTO images (key,image,size) VALUES(?,?,?)",(key, image.filename))            
                done = "Upload Successfully"
            else :
                cur.execute("UPDATE images SET image = ?,size = ? WHERE key = ?", (image.filename, key))
                done = "Update Successfully"
            con.commit()
            con.close()
            miss = miss + 1
            missRate = missRate + (miss / (hit + miss))
            randomPolicy(key) if policyy == '1' else leastRecentlyUsed(key)
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
                con.commit()       
       except:
            return 'error'
       finally:
            return render_template('configure.html')
    return render_template('configure.html')

@app.route('/static', methods = ['POST','GET']) 
def statistic():
    global miss, hit, policyy, hitRate, missRate, memcache, totalSize, capacity
    return render_template('statistic.html', freeSpace = (capacity - totalSize), fullSpace = capacity, hitRate = hitRate, missRate = missRate)

def randomPolicy(key) :
    global capacity, totalSize
    if totalSize > capacity:
        totalSize = totalSize - os.stat(path + memcache[key]).st_size
        memcache.popitem(random.choice(list(memcache.values())))

def leastRecentlyUsed(key) :
    global memcache, totalSize
    memcache.move_to_end(key)
    if totalSize > capacity:
        totalSize = totalSize - os.stat(path + memcache[key]).st_size
        memcache.popitem(last = False)

# NEED EDIT
def totalImagesSize() :
    global memcache, totalSize
    con = sqlite3.connect("P1.db")
    cur = con.cursor()    
    totalSize = cur.execute("SELECT SUM(size) FROM images").fetchall()[0][0]
    con.close()

if __name__ == '__main__':
    app.run(debug = True)
