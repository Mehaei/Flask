from model import *
from flask import render_template,flash,redirect,Response,session,request
from froms import *
from werkzeug.security import generate_password_hash,check_password_hash
from captcha import Captcha
import os,uuid
from functools import wraps
from sqlalchemy import or_

# 定义装饰器判断是否登录
def login_req(n):
    @wraps(n)
    def req(*args,**kwargs):
        if 'username' in session:
            return n(*args,**kwargs)
        else:
            return redirect('/login/')
    return req

# 登录页面
@app.route('/login/',methods=['GET','POST'])
def login():
    session.permanent= True
    # 实例化表单对象
    form = LoginForm()
    # 判断提交是否正确
    if form.validate_on_submit():
        # 获取表单中的数据
        data = form.data
        # 将用户名存入session
        session['username'] = data['account']
        # 制作一闪 到base页面
        flash('登录成功，请遨游知识的海洋吧！')
        #重定向     跳转到登录页
        return redirect('/art/list/1/')
    return render_template('login.html',title='登录',form=form)


#注册页面
@app.route('/register/',methods=['GET','POST'])
def register():
    # 实例化表单对象
    form = RegisterForm()
    # 如果表单中的数据没有问题 则返回true
    if form.validate_on_submit():
        # 获取表单中的数据
        data = form.data
        # print(data)
        # 进行用户添加操作
        user = User(
            account = data['account'],
            pwd = generate_password_hash(data['pwd'])
        )
        db.session.add(user)
        db.session.commit()

    #     制作一闪 到base页面
        flash('注册成功，请登录')
    #     跳转到登录页
        return redirect('/login/')
    return render_template('register.html', title='注册',form=form)

# 退出登录
@app.route('/logout/')
def logout():
    # 从session中删除用户信息
    session.pop('username')
    return redirect('/login/')

#文章添加
@app.route('/art/add/',methods=['GET','POST'])
@login_req
def art_add():
    # print(app.config['base_dir'])
    form = ArticleAddFrom()
    if form.validate_on_submit():
        #文章添加操作，获取提交的数据
        data = form.data

        #判断是否有文件上传
        if data['logo']:
            #获取文件名
            photoname = form.logo.data.filename
            logo = picname(photoname)

            # 上传指定的文件夹
            up_dir = os.path.join(app.config['base_dir'],'static/uploads/')
            #判断文件夹是否存在
            if not os.path.exists(up_dir):
                os.makedirs(up_dir)

            #存储文件到指定目录
            form.logo.data.save(up_dir + logo)
        else:
            logo = "default_art_logo.jpg"

    #     将数据添加到数据库
    #     获取当前登录用户的id
        user = User.query.filter_by(account=session['username']).first()
        uid = user.id
        article = Article(
            title = data['title'],
            category=data['category'],
            uid = uid,
            logo = logo,
            content = data['content']
        )

        db.session.add(article)
        db.session.commit()
    #     制作一闪  将一闪分类
        flash('发布文章成功',category='article')

        return redirect('/art/list/1/')

    return render_template('art_add.html', title='添加文章',form=form)


# 生成图片名
def picname(name):
    info = os.path.splitext(name)
    name = str(uuid.uuid4()) + info[-1]
    return name



# 文章列表
@app.route('/art/list/<int:page>/',methods=['GET'])
@login_req
def art_list(page):
    #获取登录用户的详细信息
    user = User.query.filter_by(account=session['username']).first()
    # 定义分类搜索列表
    category = { 'python':1, 'Java':2,  'PHP':3, 'C++':4}
    # 获取参数的值
    types = request.values.get('types','')
    keys = request.values.get('keys','a')
    # print(type(keys))
    # 判断是否进行了搜索
    if types:
        if types == 'all':
            # return '全部搜索'
            pagination = Article.query.filter(
                or_(Article.title.like("%" + keys + "%") if keys is not None else "",
                    Article.category.like("%" + keys + "%") if keys is not None else "",
                    Article.content.like("%" + keys + "%") if keys is not None else "",
                    Article.add_time.like("%" + keys + "%") if keys is not None else "")
            ).order_by(Article.add_time.desc()).paginate(page,per_page=2)
            # print(pagination)
        elif types == 'title':
            pagination = Article.query.filter(Article.title.like("%" + keys + "%") if keys is not None else "").order_by(Article.add_time.desc()).paginate(page,per_page=2)
            # return '标题搜索'

        elif types == 'classs':
            # 判断输入的关键字在哪个键中
            for i in category.keys():
                if keys in i:
                    keys = str(category[i])

            # pagination = Article.query.filter(Article.category.like("%" + category[keys] + "%") if keys is not None else "").order_by(Article.add_time.desc()).paginate(page,per_page=2)
            pagination = Article.query.filter_by(category=keys).order_by(Article.add_time.desc()).paginate(page,per_page=2)

            # print(pagination)
            # return '分类搜索'
        elif types == 'addtime':
            pagination = Article.query.filter(Article.title.like("%" + keys + "%") if keys is not None else "").order_by(Article.add_time.desc()).paginate(page,per_page=2)
            # return '创建时间搜索'
    else:
    # article_list = user.arts
        pagination = Article.query.filter_by(uid = user.id).order_by(Article.add_time.desc()).paginate(page,per_page=2)

    # print(category[1])
    # print(type(article_list[0].category))
    category = {1: 'python', 2: 'Java', 3: 'PHP', 4: 'C++'}
    return render_template('art_list.html', title='文章列表',pagination=pagination,category=category)



#文章修改
@app.route('/art/edit/<int:id>/',methods=['GET','POST'])
@login_req
def art_edit(id):
    form = ArticleEditFrom()
    # 获取编辑对象
    article = Article.query.get_or_404(id)
    #判断提交方式
    if request.method == 'GET':
        # 输入框中的内容为表中的内容
        form.title.data = article.title
        form.category.data = article.category
        form.content.data = article.content
    # 如果编辑表单验证没有问题
    elif form.validate_on_submit():
        data = form.data
        # 判断时候有文件提交
        if data['logo']:
            #获取文件名
            photoname = form.logo.data.filename
            logo = picname(photoname)

            # 上传指定的文件夹
            up_dir = os.path.join(app.config['base_dir'],'static/uploads/')
            #判断文件夹是否存在
            if not os.path.exists(up_dir):
                os.makedirs(up_dir)

            #存储文件到指定目录
            form.logo.data.save(up_dir + logo)
        else:
            # 如果没有新文件上传 图片还为原图片
            logo = article.logo
        # 重新写入修改后的数据
        article.title = data['title']
        article.category = data['category']
        article.content = data['content']
        article.logo = logo
        db.session.add(article)
        db.session.commit()
        flash('保存文章成功')
        return redirect('/art/list/1/')
    return render_template('art_edit.html', title='编辑文章',form=form,article=article)


# 删除文章
@app.route('/art/del/<int:id>/')
@login_req
def art_del(id):
    article = Article.query.get(id)
    # print(article)
    db.session.delete(article)
    db.session.commit()
    return redirect('/art/list/1/')

# 验证码

@app.route('/captcha/')
def captcha():
    c = Captcha()
    info = c.create_captcha()
    image = os.path.join(app.config['base_dir'],'static/captcha/') + info['image_name']
    #     读取验证码
    with open(image,'rb') as f:
        image = f.read()
    # 获取验证码具体字母和数字
    session['captcha'] = info['captcha']
    # print(session['captcha'])
    return Response(image,mimetype='jpeg')




if __name__=='__main__':
    app.run()