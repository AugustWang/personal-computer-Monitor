#! /usr/local/bin/python
# -*- coding:utf-8 -*-

# log level:
# 0 : info
# 1 : warning
# 2 : error

import os, smtplib, poplib, email, mimetypes, time, sys, subprocess
from threading              import Thread

from email.mime.text        import MIMEText
from email.mime.image       import MIMEImage 
from email.mime.multipart   import MIMEMultipart
from email.header           import decode_header

#TODO: change the e-mail address which you want to comunicate with monitor
MAIL_LIST   = ["XXXXXX@qq.com"]

#TODO: change the smtp/pop3 server which will serve for the monitor
MAIL_HOST   = "smtp.exmail.qq.com"
MAIL_POP    = "pop.exmail.qq.com"

#TODO: change the email-addr and pwd which the monitor will use
MAIL_USER   = "xxxx@qq.com"
MAIL_PASS   = "xxxxxxxxxx"
MAIL_FROM   = "xxxx@qq.com"

MAIL_TXT    = ""
MAIL_TITLE  = "PC Monitor"

#the reply cmd you can use to control your pc
CMD_SHUTDOWN=('shutdown' , 'exit')

LOG_LEVEL   = \
{
    "0" :   "INFO",
    "1" :   "WARNING",
    "2" :   "ERROR"
}

MAIL_COUNT  = 0

#if true, the screen-shot will work
SCREENSHOT_ENABLE = True

def send_mail(subject, content, filename = None):
    '''
        @returnValue
            True  - send mail successfully
            False - failure   
    '''
    try:
        message = MIMEMultipart()
        message.attach(MIMEText(content))
        message["subject"] = subject
        message["From"]    = MAIL_FROM
        message["To"]      = ";".join(MAIL_LIST)
        if filename!=None and os.path.exists(filename):
            ctype , encoding = mimetypes.guess_type(filename)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype =ctype.split("/",1)
            attachment        = MIMEImage((lambda f: (f.read(), f.close()))(open(filename, "rb"))[0],_subtype = subtype)
            attachment.add_header("Content-disposition","attachment",filename = filename)
            message.attach(attachment)

        smtp = smtplib.SMTP()
        smtp.connect(MAIL_HOST)
        smtp.login(MAIL_USER , MAIL_PASS)
        smtp.sendmail(MAIL_FROM, MAIL_LIST, message.as_string())

        return True
    except Exception, errmsg:

        return False

def receive_mail():
    '''
        @returnValue:
            0 - nothing happened
            1 - fire the 'shutdown' command
    '''
    global MAIL_COUNT
    result         =0
    popServer      =poplib.POP3(MAIL_POP)
    popServer.user(MAIL_USER)
    popServer.pass_(MAIL_PASS)
    mailCount,size =popServer.stat()

    #mail count changed
    if mailCount  != MAIL_COUNT:
        MAIL_COUNT = mailCount

        # reslove new mail
        hdr,message,octet  =popServer.retr(MAIL_COUNT)
        mail               =email.message_from_string('\n'.join(message)) 

        #subject
        subject            =email.Header.decode_header(mail['subject'])[0][0] 
        subcode            =email.Header.decode_header(mail['subject'])[0][1]
        decodedSubJect     =''

        #from
        decodedRevFrom     =email.utils.parseaddr(mail['from'])[1]

        try:
            if subcode is None:
                subcode            = 'utf-8'
                decodedSubJect     =unicode(subject,subcode)
        except Exception, e:
            pass
        
        #make sure the mail came from "PC Monitor"
        if (decodedRevFrom in MAIL_LIST) and (str(decodedSubJect).find(MAIL_TITLE) != -1):
            mailContent_textPlain=parseEmail(mail)['textplain']
            #check is 'shutdown cmd' or not
            for cmdItem in CMD_SHUTDOWN:
                if mailContent_textPlain.find(cmdItem) != -1:
                    result = 1;
                    break
            

    popServer.quit()
    return result


def get_charset(message, default='ascii'):
    return message.get_charset()
    return default

def parseEmail(msg):
    mailContentDict = {}
    fileList        = []
    textplain       =''
    texthtml        =''
    for part in msg.walk():        
        if not part.is_multipart():
            contenttype =  part.get_content_type()     
            filename    =  part.get_filename()
            if filename:
                h                       = email.Header.Header(filename)
                dh                      = email.Header.decode_header(h)
                fname                   = dh[0][0]
                encodeStr               = dh[0][1]
                fname                   = fname.decode(encodeStr,'ignore')
                
                data                    = part.get_payload(decode=True)
                fileDict                = {}
                fileDict["fileName"]    = fname
                fileDict["fileContent"] = data
                fileList.append(fileDict)                
            else:
                content_type =part.get_content_type()
                charset      =get_charset(part)
                if content_type in ['text/plain']:
                    if charset is None:
                        textplain =part.get_payload(decode=True)
                    else:
                        textplain =part.get_payload(decode=True).decode(charset)
                if content_type in ['text/html']:
                    if charset is None:
                        texthtml =part.get_payload(decode=True)
                    else:
                        texthtml =part.get_payload(decode=True).decode(charset)
        else:
            type = msg.get_content_charset()
            if type ==None:
                textplain ==msg.get_payload()
            else:
                try:
                    textplain =unicode(msg.get_payload('base64'),type)
                except UnicodeDecodeError:
                    textplain ='Error'

    mailContentDict["textplain"] = textplain
    mailContentDict['texthtml']  = texthtml
    mailContentDict["fileList"]  = fileList
   
    return  mailContentDict


def init():
    '''
        @desc
            do init, set MAIL_COUNT field
    '''
    global MAIL_COUNT
    try:
        popServer=poplib.POP3(MAIL_POP)
        popServer.user(MAIL_USER)
        popServer.pass_(MAIL_PASS)
        MAIL_COUNT,size=popServer.stat()
        return True
    except Exception, e:
        return False
    

def screenshot():
    global SCREENSHOT_ENABLE
    while True and SCREENSHOT_ENABLE:
        timePart=time.localtime()
        imgName="screenshot_at_{0}-{1}-{2}_{3}_{4}_{5}.jpg".format(timePart[0],timePart[1],timePart[2],timePart[3],timePart[4],timePart[5])

        screenCapture_cmd = \
        "screenCapture -x /usr/local/%s" % imgName
        process=subprocess.Popen(screenCapture_cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
        process.wait()
        time.sleep(30)


if __name__ == '__main__':

    Thread(target=screenshot, args=()).start()

    while True:
        if init():
            break
        else:
            time.sleep(60)

    MAIL_TXT = "the computer has started %s" % time.strftime(' at %c')

    while True:
        if send_mail(MAIL_TITLE, MAIL_TXT):
            break
        else:
            time.sleep(60)

    while True:
        shutdown=receive_mail()
        if shutdown:
            shutdown_cmd ="shutdown -h now"
            print(shutdown_cmd)
            process=subprocess.Popen(shutdown_cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
            process.wait()
        else:
            print("sleep")
            time.sleep(60)      #sleep 60s
