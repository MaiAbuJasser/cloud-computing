from asyncio.windows_events import NULL
from PIL import Image
import os
from lib2to3.pytree import convert
import sqlite3
from flask import Flask,render_template,request,flash,redirect, session,url_for, json

app = Flask(__name__)
path = '.\\static\\'
memcache = {}
hit=0
miss=0
hitrate=0
missrate=0


@app.route('/')
def main() :
    return render_template("index.html")

@app.route('/request', methods = ['GET','POST'])
def req():
    if request.method == 'POST' :
        try:
            key = request.form['key']
            con = sqlite3.connect("P1.db")
            if key in memcache.keys() :
                print("memcache")
                name = memcache[key]
                hit+=hit
                hitrate+=hit/(hit+miss)
                return render_template('request.html', user_image = ('..\\static\\' + name))
            miss+=miss
            missrate+=miss/(hit+miss)
            cur = con.cursor()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            if not isNewKey :
                name = cur.execute("SELECT image FROM images WHERE key = ?", [key]).fetchall()
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
    if request.method == 'POST' :
        try:
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
                memcache.put(key,"image.filename")
                miss+=miss
                missrate+=miss/(hit+miss)
                done = "Upload Successfully"
                
            else :
                cur.execute("UPDATE images SET image = ? WHERE key = ?", (image.filename, key))
                done = "Update Successfully"
            memcache[key] = image.filename
            con.commit()
            con.close()
            
        except:
            return 'error'
        finally:
            return render_template('upload.html', done = done)
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
    

@app.route('/config', methods = ['POST','GET']) 
def config():
    if request.method == 'POST' :
       try:
            key = request.form["key"]
            if request.form["clear"] == 'Clear' :
                del memcache[key]
            elif request.form["clearAll"] == 'Clear All' :
                memcache.clear()
       
       except:
            return 'error'
       finally:
            return render_template('configure.html')
    return render_template('configure.html')

if __name__ == '__main__':
    app.run(debug = True)
