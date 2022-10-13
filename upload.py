import base64
import sqlite3
from flask import Flask,render_template,request,flash,redirect, session,url_for, json

app = Flask(__name__)

@app.route('/')
def main() :
    return render_template("index.html")

@app.route('/request', methods = ['GET','POST'])
def req():
    if request.method == 'POST' :
        try:
            key = request.form['key']
            con=sqlite3.connect("P1.db")
            cur=con.cursor()
            img = cur.execute("SELECT image FROM images WHERE key = ?", [key]).fetchall()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            print(img[0][0])
            isNewKey = len(cur.fetchall()) == 0
            if not isNewKey :
                return render_template('request.html', user_image = img[0][0])
            else :
                return 'error'
        except:
            return("error in adding")
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
            myImg = imagePath + '\\' + image.filename
            con=sqlite3.connect("P1.db")
            cur=con.cursor()
            cur.execute("SELECT key FROM images WHERE key = ?", [key])
            isNewKey = len(cur.fetchall()) == 0
            if(isNewKey) :
                cur.execute("INSERT INTO images (key,image) VALUES(?,?)",(key,myImg))
            else :
                cur.execute("UPDATE images SET image = ? WHERE key = ?", (myImg, key))
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
            return render_template('KeyList.html', keys = cur.fetchall())
    return render_template('KeyList.html')

if __name__ == '__main__':
    app.run(debug=True)