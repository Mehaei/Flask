from flask_wtf import FlaskForm
from wtforms import *
from flask import session
from wtforms.validators import DataRequired,EqualTo,ValidationError
from model import User
from werkzeug.security import check_password_hash
# 登录注册

# 注册
class RegisterForm(FlaskForm):
    account = StringField(
        label='账号',
        description='账号',
        validators=[
            DataRequired('账号不能为空')
        ],
        render_kw={
            'class':'form-control',
            'placeholder':'请输入账户'
        }
    )
    pwd = PasswordField(
        label='密码',
        description='密码',
        validators=[
            DataRequired('密码不能为空')
        ],
        render_kw = {
            'class': 'form-control',
            'placeholder': '请输入密码'
        }
    )
    re_pwd=PasswordField(
        label='确认密码',
        description='确认密码',
        validators=[
            DataRequired('确认密码不能为空'),
            EqualTo('pwd',message='两次密码不一致')
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入确认密码'
        }
    )

    captcha = StringField(
        label='验证码',
        description='验证码',
        validators=[
            DataRequired('验证码不能为空'),
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入验证码'
        }
    )
    submit = SubmitField(
        label='注册',
        description='注册',
        render_kw={
            'class':'btn btn-primary'
        }
    )
    # 验证用户名是否存在
    def validate_account(self,field):
        account = field.data
        num = User.query.filter_by(account=account).count()

        if num > 0:
            # 抛出异常
            raise ValidationError('账户已存在')
    # 验证验证码
    def validate_captcha(self,field):
        # 获取用户输入的验证码
        capt = field.data
        # 判断验证码是否存在session中
        if not session['captcha']:
            raise ValidationError('非法操作')
        # 判断验证码是否正确
        if session['captcha'].lower() != capt.lower():
            raise ValidationError('验证码错误')

# 登录验证
class LoginForm(FlaskForm):
    account = StringField(
        label='账号',
        description='账号',
        validators=[
            DataRequired('账号不能为空')
        ],
        render_kw={
            'class':'form-control',
            'placeholder':'请输入账户'
        }
    )
    password = PasswordField(
        label='密码',
        description='密码',
        validators=[
            DataRequired('密码不能为空')
        ],
        render_kw = {
            'class': 'form-control',
            'placeholder': '请输入密码'
        }
    )
    submit = SubmitField(
        label='登录',
        description='登录',
        render_kw={
            'class':'btn btn-primary'
        }
    )
    # 验证登录
    def validate_password(self,field):
        password = field.data
        user = User.query.filter_by(account=self.account.data).first()
        if user:
            if not user.check_pwd(password):
                raise ValidationError('账户不存在或密码不正确')
        else:
            raise ValidationError('账户不存在或密码不正确')

    # # 验证用户名是否存在
    # def validate_account(self,field):
    #     account = field.data
    #     # print(account)
    #     user = User.query.filter_by(account=account).first()
    #     self.user = user
    #     if not user:
    #         raise ValidationError('账户不存在或密码不正确')
    # # 判断密码是否正确
    # def validate_password(self,field):
    #     user = self.user
    #     password = field.data
    #     if user:
    #         pwd = user.pwd
    #         if check_password_hash(pwd,password) == False:
    #             raise ValidationError('账户不存在或密码不正确')

# 文章添加验证
class ArticleAddFrom(FlaskForm):
    title = StringField(
        description='文章标题',
        label='文章标题',
        validators=[
            DataRequired('文章标题不能为空')
        ],
        render_kw={
            'class':'form-control',
            'placeholder':'请输入文章标题'
        }
    )
    category = SelectField(
        description='分类',
        label='分类',
        choices=[(1,'python'),(2,'Java'),(3,'PHP'),(4,'C++')],
        default=3,
        coerce=int,
        render_kw={
            'class':'form-control'
        }
    )
    logo = FileField(
        description='logo',
        label='logo',
        render_kw={
            'class': 'form-control-file'
        }
    )
    content = TextAreaField(
        description='文章内容',
        label='文章内容',
        validators=[
            DataRequired('内容不能为空')
        ],
        render_kw={
            'style' : 'height:300px',
            'id' : 'content'
        }
    )

    submit = SubmitField(
        description='发布文章',
        label='发布文章',
        render_kw={
            'class' : 'btn btn-primary'
        }
    )

# 文章编辑表单
class ArticleEditFrom(ArticleAddFrom):
    submit = SubmitField(
        description='保存文章',
        label='保存文章',
        render_kw={
            'class' : 'btn btn-primary'
        }
    )