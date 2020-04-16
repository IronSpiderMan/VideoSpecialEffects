import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart      # 一封邮件


def sendMail(msg):
    sender = 'sockwz@163.com'
    to_list = [
        '2930777518@qq.com'
    ]
    subject = '视频制作情况'

    # 创建邮箱
    em = MIMEMultipart()
    em['subject'] = subject
    em['From'] = sender
    em['To'] = ",".join(to_list)

    # 邮件的内容
    content = MIMEText(msg)
    em.attach(content)

    # 发送邮件
    # 1、连接服务器
    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com')
    # 2、登录
    smtp.login(sender, '1998121wzw')
    # 3、发邮件
    smtp.send_message(em)
    # 4、关闭连接
    smtp.close()