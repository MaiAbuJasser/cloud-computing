import sqlite3
from flask import Flask,render_template,request,flash,redirect, session,url_for, json

app = Flask(__name__)
def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
       myImg = new_func(file)
    return myImg

def new_func(file):
    myImg = file.read()
    return myImg

@app.route('/')
def main() :
    return render_template("upload.html")

# @app.route('/register',methods=['GET','POST'])
# def register():
#     if request.method == 'POST' :
#         try:
#             name=request.form['name']
#             password=request.form['password']
#             con=sqlite3.connect("test1.db")
#             cur=con.cursor()
#             cur.execute("insert into customers (name,password) values(?,?)",(name,password))
#             con.commit()
#             con.close()
            
            

#         except:
#          return("error in adding")
#         finally:
#          return ('success')
#     else:
         
#      return render_template('register.html')

     
@app.route('/upload', methods = ["POST", "GET"]) 
def upload():
    if (request.method == "POST") :
        try:
            key = request.form["Enter Key"]
            image = request.form["Choose File"]
            myImg = convertToBinaryData(image)
            con = sqlite3.connect("P1.db")
            cur = con.cursor()
            cur.execute("INSERT INTO images (key, image) VALUES(?, ?)",(key, myImg))
            con.commit()
            cur.close()
        except:
            return 'error'
        finally:
            return 'success'
    else:
     return render_template('upload.html')










if __name__ == '__main__':
    app.run(debug=True)