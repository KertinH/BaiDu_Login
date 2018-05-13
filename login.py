# -*- coding: utf-8 -*-

import requests
import execjs
import time
import re
import base64
import http.cookiejar as cookielib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
gid = ''
token = ''
key = ''


def get_js():
    '''通过gid.js生成gid'''
    f = open("gid.js", 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    ctx = execjs.compile(htmlstr)
    return ctx


def get_basicCookie():
    '''获取初始cookie'''
    session.get('https://www.baidu.com/',
                              headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'})
    session.cookies.save()
    session.cookies.load(ignore_discard=True)


def get_token():
    '''获取token'''
    global gid
    get_basicCookie()
    gid = get_js()
    url = 'https://passport.baidu.com/v2/api/?getapi'
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'referer':'https://www.baidu.com/'
    }
    data = {
        'getapi': '',
        'tpl': 'mn',
        'apiver': 'v3',
        'tt': str(int(time.time()*1000)),
        'class': 'login',
        'gid': gid,
        'loginversion': 'v4',
        'logintype': 'dialogLogin',
        'traceid': '',
        'callback': 'bd__cbs__pivyke',
    }
    response = session.get(url, headers=header, params=data)
    return re.match('.*"token" : "([0-9a-zA-Z]+)".*', response.text).group(1)


def publicKey():
    '''获取公钥'''
    global key
    global token
    url = 'https://passport.baidu.com/v2/getpublickey'
    token = get_token()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'referer': 'https://www.baidu.com/'
    }
    data = {
        'token': token,
        'tpl': 'mn',
        'apiver': 'v3',
        'tt': str(int(time.time()*1000)),
        'gid': gid,
        'loginversion': 'v4',
        'traceid': '',
        'callback': 'bd__cbs__h02h0j'
    }
    response = session.get(url, headers=header, params=data)
    key = re.match('.*"key":\'([0-9a-zA-Z]+)\'', response.content.decode('utf-8')).group(1)
    return response.content.decode('utf-8').split('"pubkey":\'')[1].split('\',"key"')[0].replace('\\n', '\n').replace('\\', '')


def get_password(password):
    '''生成rsa加密的账户密码'''
    pubkey = publicKey()
    rsakey = RSA.importKey(pubkey)
    cipher = PKCS1_v1_5.new(rsakey)
    password = base64.b64encode(cipher.encrypt(password.encode()))
    return password.decode('utf-8')


def login():
    '''登录'''
    user_name = input('账号：')
    password = input('密码：')
    url = 'https://passport.baidu.com/v2/api/?login'
    password = get_password(password)
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'referer': 'https://www.baidu.com/'
    }

    data = {
        'staticpage': 'https://www.baidu.com/cache/user/html/v3Jump.html',
        'charset': 'UTF-8',
        'token': token,
        'tpl': 'mn',
        'subpro': '',
        'apiver': 'v3',
        'tt': str(int(time.time()*1000)),
        'codestring': '',
        'safeflg': '0',
        'u': 'https://www.baidu.com/',
        'isPhone': 'false',
        'detect': '1',
        'gid': gid,
        'quick_user': '0',
        'logintype': 'dialogLogin',
        'logLoginType': 'pc_loginDialog',
        'idc': '',
        'loginmerge': 'true',
        'splogin': 'rate',
        'username': user_name,
        'password': password,
        'rsakey': key,
        'crypttype': '12',
        'ppui_logintime': 254896,
        'countrycode': '',
        'fp_uid': '08cc104e76b697a29930f9afdcdbdf8a0',
        'fp_info': '08cc104e76b697a29930f9afdcdbdf8a002~~~j-jjnTfCHkdUvit_~jjavfBv5ci8WJ-8rC_ffBv5ci8WJ-viQ_ajhJuXjhJuFjjuKjhL2Rf0SjQqlV8KRlXrtSv5nRv5CSv2d4Qq7iXyviX5mT8imRv5nRMy-i85a6X5miv2yRMdv782yl8rnkviyRMdQI8rCT85nTX5d4QklV3z0LQkc_w~jusfCvryUvm__I~jmU~jmz~juQf0t~ck~FakeTaK3dGz7~QkJIXp-lQrmLcqjINq0xAqHnAk8SAEHUNn3FQzS~NZ70Az0xAqHiHkdy3K3BAzHLOE8dAW8dQk3FQWuLaKdxaE8fAk3tHnSvaKHyOEwFNzdy3EjrAkR63ER69x~k3KsiOEjUXrnU8Z--9rnlvryB908DAk8fNk0k3c3LaK8DvryUvbtlJf0Tx3qHzaKHLNbRrAkSeNERBak06OEjUQTRrvz8yvqsd8idr8q0xX5drv5JSaicRX2nSv2CT8kn-vrakvzGr85miXqHx85Q785mR8E3rar~xaEcRaimk3q3~MzGd3z0SAbG4akjeAKHUOE8~NqdFAW84Xqa-3rudXEsd323zvzal85cTaEciaE3yar3r35ur3ztTvrdx3zHzXqt7v5cRvzsx85aTa5yivka7vqsd8rCI3J__y~juO~jux~juB~juYjjtrfC1zJeC6-_CfBNERfAzjTAJ__j~juMjjmZ~jmE~jmg~jmG~jmH~jmlfa95nU82t782C-X2tiX2Q68it68C__',
        'loginversion': 'v4',
        'dv': 'tk0.43083294066104651525942832352@oop0d-sGFb6mgFCFYuF3psLelCFehN6rhNLihP8isi7io34k5gsk5KNkT~4kqbJ0pDBeohrJlNFpsCL~0jLeljALs~QKl-Hmj-6rFK6LjKDmjj4pBhr3QECFeNLehrFpfg6plN82p~8iQa8UCb6G0is~Qfs~qb6mgFCFYuF3psLelCFehN6rhNLihP8isi7io34k5-6kqeNk0j61jj4pBhr3QECFeNLehrFpfg6plN82p~8iQa8UCb6G6-6ksfrp0Wr6r3-4kFjDmjwsr0~4ujw6r5bsr6y4k3~6~0bNk0-61j~6~qb6rT~6rCbJ0pDBeohrJlNFpsCL~0jLeljALs~QKl-Hujg6k5b6~8-4k0YsG0w4pBhr3QECFeNLehrFpfg6plNHUl-7Lj~s~Tb6~AK4k5ws~3Y4pBhr3QECFeNLehrFpfg6plNHUl-7Lj_-~~Mz~CjRqlMhCph6Ej-4kA~wplQ2bj4GC~6kT~6G3w6kAK6rqwsGFgsr5eDrC-Dk6-6~F-hplMuBw8u6V4-liQi8IAUpcHuFIAKld4-ge7UBXHUXIH9C_ypt6mjj4k0-6r5bs~CK4k0e6~AbDkAw4k0e6~Ab6rF~s1jy6~8_',
        'traceid': '',
        'callback': 'parent.bd__pcbs__oxzeyj'
    }

    while True:
        # print(data)
        response = session.post(url, headers=header, data=data)
        # print(response.content.decode('utf-8'))

        url_ = re.match('.*href \+= "(.*)"\+accounts', response.content.decode('utf-8').split('\n')[13]).group(1) +'&accounts='
        # print(url_)
        err = re.match('.*href \+= "([^&]+).*', response.content.decode('utf-8').split('\n')[13]).group(1)

        if err == 'err_no=0':
            print('登录成功！')
            session.cookies.save()
            session.cookies.load(ignore_discard=True)

            response = session.get('http://i.baidu.com/', headers=header)
            print(response.content.decode('utf-8'))
            break

        elif err == 'err_no=6'or err == 'err_no=257':
            codestring = re.match('.*codeString=([a-zA-Z0-9]+)&.*', url_).group(1)
            data['codestring'] = codestring
            captcha = session.get('https://passport.baidu.com/cgi-bin/genimage?{}'.format(codestring), headers=header, params={'{}'.format(codestring): ''})
            # print('https://passport.baidu.com/cgi-bin/genimage?{}'.format(codestring))

            with open('captcha.jpg', 'wb') as f:
                f.write(captcha.content)
                f.close()

            verifycode = input('验证码：')
            data['verifycode'] = verifycode

            check_data ={
                'checkvcode': '',
                'token': token,
                'tpl': 'mn',
                'apiver': 'v3',
                'tt': time.time(),
                'verifycode': verifycode,
                'loginversion': 'v4',
                'codestring': codestring,
                'traceid': '',
                'callback': 'bd__cbs__3olniu'
            }
            session.get('https://passport.baidu.com/v2/?checkvcode', headers=header, params=check_data)

        else:
            print('错误类型：', err)
            exit()


login()
