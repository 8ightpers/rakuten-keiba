#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time 
import chromedriver_binary
import requests
import numpy as np
import math
import bettime
import random
import boto3
import base64
import sys
import logging
import subprocess
import os

from flask_httpauth import HTTPBasicAuth
from threading import Thread
from subprocess import PIPE
from flask import Markup
from flask import Flask
from flask import Flask, render_template, request
from botocore.exceptions import ClientError
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup

# For Flask:
app = Flask(__name__)
auth = HTTPBasicAuth()

# For Basic Authentication:
users = {
    "8anx": "good",
    "8anxgood": "8anxgood"
}

# loginID   : 楽天会員ログイン ユーザID 
# password  : 上記パスワード
# rakutenpw : 楽天会員用の暗証番号（4桁)
# 
# 例：
# loginID = "foo@hoge.com"
# password = "xGhdkgfiuyg"
# rakutenpw = "5976"

loginID = ""
password = ""
rakutenpw = ""

# 楽天競馬の出馬表のURLより、投票したい競馬場を選び、以下Xの18桁のコードを設定する
# https://keiba.rakuten.co.jp/race_card/list/RACEID/XXXXXXXXXXXXXXXXXX?l-id=top_raceInfoTodayTrackName_raceList_20 

url = "https://keiba.rakuten.co.jp/odds/tanfuku/RACEID/"
baseid = ""
race_list = []
body_text = ""

# Environment(pip)
# Package             Version
# ------------------- --------------
# async-generator     1.10
# attrs               21.4.0
# beautifulsoup4      4.10.0
# boto3               1.21.14
# botocore            1.24.14
# certifi             2021.10.8
# cffi                1.15.0
# charset-normalizer  2.0.12
# chromedriver-binary 99.0.4844.51.0
# click               8.0.4
# cryptography        36.0.1
# Flask               2.0.3
# h11                 0.13.0
# idna                3.3
# importlib-metadata  4.11.3
# itsdangerous        2.1.1
# Jinja2              3.0.3
# jmespath            0.10.0
# MarkupSafe          2.1.1
# numpy               1.21.5
# outcome             1.1.0
# pi                  0.1.2
# pip                 20.1.1
# pycparser           2.21
# pyOpenSSL           22.0.0
# PySocks             1.7.1
# python-dateutil     2.8.2
# requests            2.27.1
# s3transfer          0.5.2
# selenium            3.141.0
# setuptools          47.1.0
# six                 1.16.0
# slackweb            1.0.5
# sniffio             1.2.0
# sortedcontainers    2.4.0
# soupsieve           2.3.1
# trio                0.20.0
# trio-websocket      0.9.2
# typing-extensions   4.1.1
# urllib3             1.26.8
# Werkzeug            2.0.3
# wsproto             1.1.0
# zipp                3.7.0

def getSortOdds(raceid):

    # D E B U G 
    # import pdb; pdb.set_trace()

    # Create BeautifulSoup Object
    res = requests.get(url + raceid)
    soup = BeautifulSoup(res.text,'html.parser')

    # For Loading Page
    time.sleep(2)

    position_data = []
    number_data = []
    name_data = []
    win_data = []
    place_datau = []
    place_datad = []

    # Odds Data
    for single_odds in soup.find_all("tbody", class_="singleOdds"):

        for position in single_odds.find_all("td", class_="position"):
            position_data.append(int(position.get_text()))


        for horce_number in single_odds.find_all("th", class_="number"):
            number_data.append(int(horce_number.get_text()))

        for td in single_odds.find_all("td", class_="horse"):
            for a in td.findAll("a",href=True,target="_blank"): 
                name_data.append(a.text.strip())

        for td in single_odds.find_all("td", class_="win"):
            for win in td.find_all("span"):
                win_data.append(float(win.text.strip())) 

        for td in single_odds.find_all("td", class_="place"):
            i = 1
            for place in td.find_all("span"):
                if i == 1:
                    #print(place)
                    place_datau.append(float(place.text.strip()))
                
                i = i + 1            
    
                if i == 4:
                    #print(place)
                    place_datad.append(float(place.text.strip())) 
                    i = 1 

    # Remove Data            
    posi = math.floor(int(len(position_data))/2)

    del position_data[posi:]
    del number_data[posi:]
    del name_data[posi:]
    del win_data[posi:]
    del place_datau[posi:]
    del place_datad[posi:]

    odds_data = [position_data,number_data,win_data,place_datau,place_datad]
    npodds_data = np.array(odds_data)

    # Sort of HorceNumber
    np_odds_data = npodds_data[npodds_data[:,0].argsort(), :]
    
    return np_odds_data

def getOdds(raceid):

    # D E B U G 
    # import pdb; pdb.set_trace()

    # Create BeautifulSoup Object
    res = requests.get(url + raceid)
    soup = BeautifulSoup(res.text,'html.parser')

    # For Loading Page
    time.sleep(2)

    position_data = []
    number_data = []
    name_data = []
    win_data = []
    place_datau = []
    place_datad = []

    # Odds Data
    for single_odds in soup.find_all("tbody", class_="singleOdds"):

        for position in single_odds.find_all("td", class_="position"):
            position_data.append(position.get_text())


        for horce_number in single_odds.find_all("th", class_="number"):
            number_data.append(horce_number.get_text())

        for td in single_odds.find_all("td", class_="horse"):
            for a in td.findAll("a",href=True,target="_blank"): 
                name_data.append(a.text.strip())

        for td in single_odds.find_all("td", class_="win"):
            for win in td.find_all("span"):
                win_data.append(win.text.strip()) 

        for td in single_odds.find_all("td", class_="place"):
            i = 1
            for place in td.find_all("span"):
                if i == 1:
                    #print(place)
                    place_datau.append(place.text.strip())
            
                i = i + 1                

                if i == 4:
                    #print(place)
                    place_datad.append(place.text.strip()) 
                    i = 1 

    # Remove Data            
    posi = math.floor(int(len(position_data))/2)

    del position_data[posi:]
    del number_data[posi:]
    del name_data[posi:]
    del win_data[posi:]
    del place_datau[posi:]
    del place_datad[posi:]

    odds_data = [position_data,number_data,name_data,win_data,place_datau,place_datad]
    npodds_data = np.array(odds_data)

    # Sort of HorceNumber
    np_odds_data = npodds_data[:, npodds_data[1,:].argsort()]
 
    return np_odds_data

def doRace(raceid):

    # D E B U G 
    #import pdb; pdb.set_trace()

    global body_text 
    res = requests.get(url + raceid)

    # Race Title
    soup = BeautifulSoup(res.text,'html.parser')
    title_text = soup.find('title').get_text()
    print(title_text)

    # Headless Chrome 天候とダート状態抽出
    options = webdriver.ChromeOptions()
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url + raceid) 

    time.sleep(1)

    print("天候： " + driver.find_element_by_xpath('//*[@id="raceInfomation"]/div/div[2]/ul[2]/li[2]/dl/dd[1]').text)
    print("ダ： " + driver.find_element_by_xpath('//*[@id="raceInfomation"]/div/div[2]/ul[2]/li[2]/dl/dd[2]').text)
    body_text = body_text + "天候： " + \
    driver.find_element_by_xpath('//*[@id="raceInfomation"]/div/div[2]/ul[2]/li[2]/dl/dd[1]').text + "<br/>"
    body_text = body_text + "ダ： " + \
    driver.find_element_by_xpath('//*[@id="raceInfomation"]/div/div[2]/ul[2]/li[2]/dl/dd[2]').text + "<br/>"

    # default time 
    betting_time = "18:00"

    # Betting Time
    for bettingTime in soup.find_all("dd", class_="bettingTime"):
        betting_time = bettingTime.get_text()
        #print(betting_time)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("Now time:                        " + now)

    # before 1mitutes
    betting_time = bettime.bettingTime(betting_time)
    bbtime = datetime.now().strftime("%Y-%m-%d")
    bbtime = bbtime + " " + betting_time
    print("Race Start time before 1mitutes: " + bbtime)        
    body_text = body_text + "Race Start time before 1mitutes: " + bbtime + "<br/>"

    # before 2minutes
    betting_time = bettime.bettingTime(betting_time)
    btime = datetime.now().strftime("%Y-%m-%d")
    btime = btime + " " + betting_time
    print("Race Start time before 2minutes: " + btime)
    body_text = body_text + "Race Start time before 2minutes: " + btime + "<br/>" 

    i = 1
    j = 1
    k = 1
    storm = 0

    while True:
        
        if i == 1:
            before_placeu = getOdds(raceid)[4]
            print("#### Progressing....... ")
            body_text = body_text + "#### Progressing....... " + "<br/>"

        time.sleep(random.randint(10,15))

        while True:

            time.sleep(random.randint(10,15))
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            if now == btime and j == 1:
            
                current_placeu = getOdds(raceid)[4]
                placeu_diff = current_placeu.astype(np.float16) - before_placeu.astype(np.float16)

                odds_data = getOdds(raceid)
                npoddsdata = np.insert(odds_data,6,placeu_diff,axis=0)    

                # Sort of Fukusho
                print("#### before 2mitutes Odds   ")
                body_text = body_text + "#### before 2mitutes Odds   " + "<br/>"
                print("[['人気順' '馬番' '馬名' '単勝オッズ' '複勝オッズ' '複勝オッズ'")
                body_text = body_text + "[['人気順' '馬番' '馬名' '単勝オッズ' '複勝オッズ' '複勝オッズ'" + "<br/>"
                print(npoddsdata[:, npoddsdata[4,:].argsort()].T)
                body_text = body_text + str(npoddsdata[:, npoddsdata[4,:].argsort()].T).replace('\n','<br/>') + "<br/>"
                before_placeu = current_placeu    

                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                j = 0

            if now == bbtime and k == 1:

                current_placeu = getOdds(raceid)[4]
                placeu_diff = current_placeu.astype(np.float16) - before_placeu.astype(np.float16)

                odds_data = getOdds(raceid)
                npoddsdata = np.insert(odds_data,6,placeu_diff,axis=0)

                print("#### before 1mitutes Odds   ")
                body_text = body_text + "#### before 1mitutes Odds   " + "<br/>"
                print("[['人気順' '馬番' '馬名' '単勝オッズ' '複勝オッズ' '複勝オッズ'")
                body_text = body_text + "[['人気順' '馬番' '馬名' '単勝オッズ' '複勝オッズ' '複勝オッズ'" + "<br/>"
                print(npoddsdata[:, npoddsdata[4,:].argsort()].T)
                body_text = body_text + str(npoddsdata[:, npoddsdata[4,:].argsort()].T).replace('\n','<br/>') + "<br/>"

                before_placeu = current_placeu
                no_race =  getSortOdds(raceid)

                b = 0 

                for index in range(len(no_race[0,:])):

                    if index == 0:
                        b = no_race[1,index]                    

                    if b > no_race[1,index]:
                        storm = storm + 1

                    if index == len(no_race[0, :]):
                        break

                    b = no_race[1,index]

                print("#### storm: " + str(storm))
                body_text = body_text + "#### storm: " + str(storm) + "<br/>"

                # 天候とダート状態抽出
                strWeather = driver.find_element_by_xpath('//*[@id="raceInfomation"]/div/div[2]/ul[2]/li[2]/dl/dd[1]').text
                strDart = driver.find_element_by_xpath('//*[@id="raceInfomation"]/div/div[2]/ul[2]/li[2]/dl/dd[2]').text

                if len(title_text) == 43:
                    print("#### [NOTICE] Race is END.")
                    body_text = body_text + "[NOTICE] Race is END." + "<br/>"
                    break

                if (strWeather == "雨"):
                    print("#### [NOTICE] Stormy Weather!! No Race!!")
                    body_text = body_text + "[NOTICE] Stormy Weather!! No Race!!" + "<br/>"
                    break

                if (strDart == "不良"):
                    print("#### [NOTICE] Heavy Dart!! No Race!!")
                    body_text = body_text + "[NOTICE] Heavy Dart!! No Race!!" + "<br/>"
                    break

                #body_text = body_text +"raceid[-2]" + str(raceid[-2])
                if str(raceid[-2:]) == "01" or str(raceid[-2:]) == "02"\
                or str(raceid[-2:]) == "03" or str(raceid[-2:]) == "04":
                    print("#### [NOTICE] Freshman Race!! No Race!!")
                    body_text = body_text + "[NOTICE] Freshman Race!! No Race!!" + "<br/>"
                    break

                if len(no_race[0,:]) < 8:
                    print("#### [NOTICE] Less than 8 horse!! No Race!!")
                    body_text = body_text + "[NOTICE] Less than 8 horse!! No Race!!" + "<br/>"
                    break

                if int(storm) > 2 and len(no_race[0,:]) > 12:
                    print("Storm: " + str(storm))
                    print("#### [NOTICE] S.T.O.R.M  No way!! No Race!!")
                    body_text = body_text + "[NOTICE] S.T.O.R.M  No way!! No Race!!" + "<br/>"
                    break

                if int(storm) > 2 and len(no_race[0,:]) > 14:
                    print("Storm: " + str(storm))
                    print("#### [NOTICE] S.T.O.R.M  No way!! No Race!!")
                    body_text = body_text + "[NOTICE] S.T.O.R.M  No way!! No Race!!" + "<br/>"
                    break
                
                fuku_odds = float(npoddsdata[:, npoddsdata[4,:].argsort()].T[0,4])
                betno = str(npoddsdata[:, npoddsdata[4,:].argsort()].T[0,1])
                tan_odds = float(npoddsdata[:, npoddsdata[4,:].argsort()].T[0,3])
                niban_odds = float(npoddsdata[:, npoddsdata[4,:].argsort()].T[1,1])

                if fuku_odds >= 1.1:
                    print("#### [NOTICE] Fukusho High Odds!! No Race!!")
                    body_text = body_text + "[NOTICE] Fukusho High Odds!! No Race!!" + "<br/>"
                    break

                if tan_odds >= 1.7:
                    print("#### [NOTICE] Tansho High Odds!! No Race!!")
                    body_text = body_text + "[NOTICE] Tansho High Odds!! No Race!!" + "<br/>"
                    break

                if tan_odds <= 1.1:
                    print("#### [NOTICE] Tansho LOW Odds!! No Race!!")
                    body_text = body_text + "[NOTICE] Tansho Too LOW ODDS!! No Race!!" + "<br/>"
                    break

                if niban_odds - fuku_odds <= 0.2:
                    print("#### [NOTICE] No.1,2 DeadHeat!! No Race!!")
                    body_text = body_text + "[NOTICE] No.1,2 DeadHeat!! No Race!!" + "<br/>"
                    break

                print("#### Betting....        ")
                body_text = body_text + "#### Betting....        " + "<br/>"

                # BET HORSE
                betHorse(raceid,betno)

                k = 0

                break
        break

    # Slack notify
    reqSlack(title_text,body_text)
    writeLog(title_text,body_text)

    driver.quit()

    strResult = title_text + body_text + "<br/>"

    body_text = ""

    return strResult

def writeLog(title_text,body_text):

    title_text = title_text.replace("<br/>","\n")
    body_text = body_text.replace("<br/>","\n")

    logging.info(title_text)
    logging.info(body_text)

def reqSlack(title_text,body_text):

    title_text = title_text.replace("<br/>","\n")
    body_text = body_text.replace("<br/>","\n")

    # Slack WebHookURLを設定すること
    webhook_url = "https://xxxxxxxxxxxxxxxxxxxxx"
    requests.post(webhook_url,data=json.dumps({"text":title_text + "\n" + body_text,}))

def betHorse(raceid,betno):

    courseID = raceid[-10:-8]
    raceNo = raceid[-2:]

    global body_text

    # D E B U G
    #import pdb; pdb.set_trace()

    # Headless Chrome
    options = webdriver.ChromeOptions()
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    LiteURL = "https://bet.keiba.rakuten.co.jp/bet_lite/RACEID/" + raceid
    driver.get(LiteURL) 
    #print(driver.current_url)

    # 楽天ログイン
    driver.find_element_by_id('loginInner_u').send_keys(loginID)
    driver.find_element_by_id('loginInner_p').send_keys(password)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.find_element_by_name('submit').click()

    # 購入限度額
    str_amount = driver.find_element_by_xpath("//span[@class='amount']").text.replace(",","")
    print("#### 購入限度額: " + str_amount + "円")
    body_text = body_text + "#### 購入限度額: " + str_amount + "円"
    #print(driver.current_url)

    if int(str_amount) >= 100:

        # Bet type : 複勝(2)
        bettype_element = driver.find_element_by_name("betType")
        bettype_select_element = Select(bettype_element)
        bettype_select_element.select_by_value("2")
        print("#### 式別: 複勝")
        body_text  = body_text + "#### 式別: 複勝" + "<br/>"

        # Bet Mode : 通常(16)
        betmode_element = driver.find_element_by_name("betMode")
        betmode_select_element = Select(betmode_element)
        betmode_select_element.select_by_value("16")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_class_name("btn").click()
        print("#### 方式: 通常")
        body_text = body_text + "#### 方式: 通常" + "<br/>"
        time.sleep(1)
        #print(driver.current_url)

        # 投票馬選択 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_xpath("//*[@id='contents']/form/div[1]/div[2]/table/tbody/tr[" + betno  +  "]/td[5]/input").click()
        time.sleep(1)

        # 投票金額 複勝ころがし
        driver.find_element_by_name('buyUnitCount').send_keys(str(math.floor(int(str_amount)/100)))
        driver.find_element_by_name('confirm').click()

        driver.find_element_by_name('cashConfirm').send_keys(str(math.floor(int(str_amount)/100)) + "00")
        driver.find_element_by_name('inputBet').click()
        time.sleep(1)
        print("#### 購入金額: " + str(math.floor(int(str_amount)/100)) + "00" + "円")
        body_text = body_text + "#### 購入金額: " + str(math.floor(int(str_amount)/100)) + "00" + "円" + "<br/>"
        print("#### 購入モード: 複勝ころがし")
        body_text = body_text + "#### 購入モード: 複勝ころがし" + "<br/>"

        print("#### [Success] Betting Complete!! ")
        body_text = body_text + "#### [Success] Betting Complete!! " + "<br/>"
        print("Horce Number is " +  betno)
        body_text = body_text + "Horce Number is " +  betno + "<br/>"
    
    else:
        print("#### Betting Failed!! Lack of funds!!")
        body_text = body_text + "#### [Error] Betting Failed!! Lack of funds!! " + "<br/>"


    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    #print("Now:" + now)
    driver.quit()

def setCookies():

    # Load Cookie Contents
    json_open = open('cookie.txt', 'r')
    cookies = json.load(json_open)
 
    for cookie in cookies:
        tmp = {"name": cookie["name"], "value": cookie["value"]}
        driver.add_cookie(tmp)

def get_secret(secret_name):

    # D E B U G
    #import pdb; pdb.set_trace()

    region_name = "ap-northeast-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return secret

def async_doRace(baseid,race_list):

    # 投票開始
    for raceno in race_list:

        doRace(str(baseid) + raceno)


@app.route("/betHorse", methods=["post"])
def main():

    global loginID
    global password
    global rakutenpw
    global race_list
    global baseid

    # AWS SecretsManagerを使用する場合はコメントを外す
    #loginID = get_secret("horcerace/loginid")
    #password = get_secret("horcerace/loginpw")
    #rakutenpw = get_secret("horcerace/rakutenpw")

    start_no = 1
    end_no = 12
 
    raceid = int(request.form.get("a"))

    if len(request.form.get("b")) > 0 :
        start_no = int(request.form.get("b"))

    if len(request.form.get("c")) > 0 :
        end_no = int(request.form.get("c"))
    
    baseid = raceid

    print("#### baseid: " + str(baseid))
    print("#### start_no: " + str(start_no))
    print("#### end_no: " + str(end_no))

    # RaceNo組み立て
    count = (int(end_no) - int(start_no)) + 1

    for raceno in range(count):

        if int(start_no) < 10:
            race_list.append("0" + str(start_no))
        else:
            race_list.append(str(start_no))

        start_no = int(start_no) + 1

    print("#### race_list: " + str(race_list))

    # 非同期処理
    thread = Thread(target=async_doRace, args=(baseid,race_list,))
    thread.setDaemon(True)
    thread.start()

    strResult = ""
    race_list = []

    # 504BadGateway 対策
    #return render_template('output.html', answer = Markup(strResult))
    return render_template('output.html', answer = "Doing Race!!")

@app.route("/check")
def healthcheck():
    return render_template('check.html')

@app.route("/keiba")
@auth.login_required
def hello():

    # ログ出力設定
    now = datetime.now().strftime("%Y%m%d")
    #logging.basicConfig(filename='/var/log/keiba/betHorse_' + now + '.log', level=logging.DEBUG)
    logging.basicConfig(filename='/var/log/keiba/betHorse.log', level=logging.DEBUG)

    # 今日のレースを表示する
    path = "/home/ec2-user/rakuten_keiba"
    proc = subprocess.run(path + "/getraceidtoday.sh", shell=True, stdout=PIPE, stderr=PIPE, text=True)
    print(proc.stdout)

    # htmlを呼び出す
    return render_template('input.html', title = 'betHorse!!' , raceidtoday = Markup(proc.stdout))

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0')