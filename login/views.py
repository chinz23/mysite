from django.shortcuts import render,redirect
# Create your views here.
from . import models
from . import forms
import hashlib
import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def hash_code(s,salt='mysite'):
    h=hashlib.sha256()
    s+=salt
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    code=hash_code(user.name,now)
    models.ConfirmString.objects.create(code=code,user=user,)
    return code

def send_email(email,code):
    subject='来自某某网站注册业的确认邮件'
    text_content='感谢注册本网站，专注于django学习！'
    html_content='''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                    这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    msg=EmailMultiAlternatives(subject,text_content,settings.EMAIL_HOST_USER,[email])
    msg.attach_alternative(html_content,'text/html')
    msg.send()

def User_confirm(request):
    code =request.GET.get('code',None)
    message=''
    try:
        confirm=models.ConfirmString.objects.get(code=code)
    except:
        message='无效确认信息！'
        return render(request,'login/confirm.html',locals())

    c_time=confirm.c_time
    now=datetime.datetime.now()

    if now>c_time+datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message='确认时间已过期！'
        return render(request,'login/confirm.html',locals())
    else:
        confirm.user.has_confirm=True
        confirm.user.save()
        confirm.delete()
        message='您已注册成功！'
        return render(request,'login/confirm.html',locals())


def index(request):
    pass
    return render(request,'login/index.html')

def login(request):
    if request.session.get('is_login',None):
        return redirect('/index/')
    if request.method == "POST":
        login_form=forms.UserForm(request.POST)
        message = "所有字段都必须填写！"
        if login_form.is_valid():  # 确保用户名和密码都不为空
            username = login_form.cleaned_data['username']
            userpassword=login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirm:
                    message='还未进行邮件确认！'
                    return render(request,'login/login.html',locals())
                if user.password == hash_code(userpassword):
                    request.session['is_login']=True
                    request.session['user_id']=user.id
                    request.session['user_name']=user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'login/login.html',locals())
    login_form=forms.UserForm()
    return render(request, 'login/login.html',locals())

def logout(request):

    request.session.flush()
    return redirect('/index/')

def register(request):
    if request.session.get('is_login',None):
        return redirect('/index/')

    if request.method=='POST':
        register_form=forms.RegisterForm(request.POST)
        message='内容有误！'
        if register_form.is_valid():
            username=register_form.cleaned_data['username']
            pwd1=register_form.cleaned_data['password1']
            pwd2=register_form.cleaned_data['password2']
            email=register_form.cleaned_data['email']
            sex=register_form.cleaned_data['sex']

            if pwd1!=pwd2:
                message='密码不一致!'
                return render(request,'login/register.html',locals())
            else:
                same_username=models.User.objects.filter(name=username)
                if same_username:
                    message='用户名已存在！'
                    return render(request,'login/register.html',locals())
                same_email=models.User.objects.filter(email=email)
                if same_email:
                    message='该邮箱已注册！'
                    return render(request,'login/register.html',locals())

                new_user=models.User()
                new_user.name=username
                new_user.password=hash_code(pwd2)
                new_user.email=email
                new_user.sex=sex
                new_user.save()

                code=make_confirm_string(new_user)
                send_email(email,code)
                message='请确认邮件！'
                return render(request,'login/confirm.html',locals())


    register_form=forms.RegisterForm()
    return render(request,'login/register.html',locals())

