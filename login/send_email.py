import os
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

if __name__ == '__main__':

   subject,from_email,to='来自周立恒的Django学习邮件','chinz01@sina.com','55211409@qq.com'
   text_content='欢迎学习django'
   html_content='<p>欢迎访问<a href="www.sina.com" target=blank>新浪</a>123qweasdzxcdfgsdrfasd</p>'
   msg=EmailMultiAlternatives(subject,text_content,from_email,[to])
   msg.attach_alternative(html_content,'text/html')
   msg.send()