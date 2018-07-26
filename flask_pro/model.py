from flask import Flask
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime,timedelta

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(20)

# 项目根路径
app.config['base_dir'] = os.path.dirname(__file__)

# session过期时间
app.permanent_session_lifetime = timedelta(hours=2)


# 配置上传路径
app.config['uploads'] = os.path.join(os.path.dirname(__file__),'uploads/')

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@127.0.0.1:3306/project?charset=utf8"
# 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'cms_user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    account = db.Column(db.String(20),nullable=False)
    pwd = db.Column(db.String(100),nullable=False)
    add_time = db.Column(db.DATETIME,default=datetime.now)
    arts = db.relationship('Article',backref='user',cascade='all,delete,delete-orphan')

    def __repr__(self):
        return self.account

    # 检查密码是否正确
    def check_pwd(self,pwd):
        # 返回true密码正确  返回false密码错误
        return check_password_hash(self.pwd,pwd)

class Article(db.Model):
    __tablename__='cms_article'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(100),nullable=False)
    category = db.Column(db.Integer,nullable=True)

    # 外键
    uid = db.Column(db.Integer,db.ForeignKey('cms_user.id'))

    logo = db.Column(db.String(100),nullable=True)
    content = db.Column(db.Text,nullable=False)
    add_time = db.Column(db.DATETIME,default=datetime.now,nullable=True)

    # def __repr__(self):
    #     return self.title

if __name__ == '__main__':
    db.create_all()