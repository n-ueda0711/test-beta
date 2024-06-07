from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask import session,redirect,url_for
from app import key
from hashlib import sha256
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

#Flaskアプリケーションとデータベースを設定
app = Flask(__name__)
app.secret_key = key.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/s1319/Documents/Desktop/TCL/models/onegai.db'
db = SQLAlchemy(app)

class OnegaiContent(db.Model):
    __tablename__ = 'onegaicontents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, title=None, body=None):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Title %r>' % (self.title)
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(128), unique=True)
    hashed_password = db.Column(db.String(128))

    def __init__(self, user_name=None, hashed_password=None):
        self.user_name = user_name
        self.hashed_password = hashed_password

    def __repr__(self):
        return '<Name %r>' % (self.user_name)

@app.route("/")
@app.route("/index")
def index():
    #ログイン済ユーザーか確認
    if "user_name" in session:
        name = session["user_name"]
        print("Debug: user_name in session is", name)  #デバッグメッセージ
        all_onegai = OnegaiContent.query.all()
        return render_template("index.html",name=name,all_onegai=all_onegai)
    else:
        #ログイン画面にリダイレクト
        return redirect(url_for("top",status="logout"))

#お願い登録
@app.route("/add",methods=["post"])
def add():
    title = request.form["title"]
    body = request.form["body"]
    content = OnegaiContent(title,body)
    db.session.add(content)
    db.session.commit()
    return index()

#お願い更新
@app.route("/update",methods=["post"])
def update():
    content = OnegaiContent.query.filter_by(id=request.form["update"]).first()
    content.title = request.form["title"]
    content.body = request.form["body"]
    db.session.commit()
    return index()

#お願い削除
@app.route("/delete",methods=["post"])
def delete():
    id_list = request.form.getlist("delete")
    for id in id_list:
        content = OnegaiContent.query.filter_by(id=id).first()
        db.session.delete(content)
    db.session.commit()
    return index()

#ログインページへのルーティング
@app.route("/top")
def top():
    status = request.args.get("status")
    return render_template("top.html",status=status)

#ログイン処理
@app.route("/login",methods=["post"])
def login():
    user_name = request.form["user_name"]
    print("Debug: user_name is", user_name)  #デバッグメッセージ
    user = User.query.filter_by(user_name=user_name).first()
    print("Debug: user is", user)  #デバッグメッセージ
    if user:
        password = request.form["password"]
        hashed_password = sha256((user_name + password + key.SALT).encode("utf-8")).hexdigest() 
        
        #hashed_password をデータベースの値と比較
        if user.hashed_password == hashed_password:
            session["user_name"] = user_name
            return redirect(url_for("index"))
        else:
            return redirect(url_for("top",status="wrong_password"))
    else:
        return redirect(url_for("top",status="user_notfound"))

#新規登録ページへのルーティング
@app.route("/newcomer")
def newcomer():
    status = request.args.get("status")
    return render_template("newcomer.html",status=status)

#ユーザー登録処理
@app.route("/registar",methods=["post"])
def registar():
    user_name = request.form["user_name"]
    user = User.query.filter_by(user_name=user_name).first()
    #既に登録済か確認
    if user:
        return redirect(url_for("newcomer",status="exist_user"))
    else:
        password = request.form["password"]
        hashed_password = sha256((user_name + password + key.SALT).encode("utf-8")).hexdigest()  #hashed_password をデータベースに保存
        user = User(user_name, hashed_password)
        db.session.add(user)
        db.session.commit()
        session["user_name"] = user_name
        return redirect(url_for("index"))

#ログアウト処理
@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return redirect(url_for("top",status="logout"))

if __name__ == "__main__":
    app.run(debug=True)
