# -*- coding: utf-8 -*-

# Cloud Fiarestoreのドキュメントも合わせて参照
# https://firebase.google.com/docs/firestore/quickstart?hl=ja#python
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import time # sleep関数を使うため
import RPi.GPIO as GPIO
import smbus
import datetime
import json
import os #環境変数をセットするため
import BME280 #温度センサモジュール

#秘密鍵のファイルを環境変数にセットする．
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/pi/syspro_firebase_secret.json"

#firestoreの事前準備
cred = credentials.Certificate('/home/pi/syspro_firebase_secret.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

i2c = smbus.SMBus(1)
address = 0x48

GPIO.setmode(GPIO.BCM) #GPIO.BCM を指定した場合，ポートはGPIO番号で指定する
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.HIGH)
time.sleep(1)

# firestoreのコールバック関数を作成
def on_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        print(u'New cmd: {}'.format(change.document.id))
        led = change.document.to_dict()["led"]
        print(u'LED: {}'.format(led))
    if led == "ON":
        print "ON"
        # TODO1 LEDをON(GPIO14をHIGH)にする処理
        GPIO.output(14, GPIO.HIGH)

    elif led == "OFF":
        print "OFF"
        # TODO1 LEDをOFF(GPIO14をLOW)にする処理
        GPIO.output(14, GPIO.LOW)


# コレクションled_status の中のドキュメントledの変更を監視する
# ドキュメントledの内容に変更があった場合はコールバック関数on_snapshotが呼ばれる
doc_ref = db.collection('led_status').document(u'led')
doc_watch = doc_ref.on_snapshot(on_snapshot)

# 温度湿度気圧センサから値を取得してFirestoreに送信する部分
# 「'''」で囲まれた部分はコメントアウトされているので，参考にすること．


BME280.setup()
BME280.get_calib_param()

try:
    while True:
        #TODO2 温度，湿度，気圧の値を取得する
        temp = BME280.readTemp()
        humi = BME280.readHumi()
        pres = BME280.readPres()

        print("Temperature:%6.2f" %(temp))
        print("Humidity:%6.2f" %(humi))
        print("Pressure:%6.2f" %(pres))
        data = {"temp": temp, "humi": humi, "pres":pres}
        db.collection('temperature').document(str(datetime.datetime.now())).set(data)
        time.sleep(3)
except KeyboardInterrupt:
    print('KeyboardInterrupt')
    GPIO.cleanup()


# 温度センサと接続できないうちはこの無限ループを使う
# 上記の温度センサのループを有効にした場合は，こちらをコメントアウトすること．
try:
    while 1:
        pass
except KeyboardInterrupt:
    print('KeyboardInterrupt')
    GPIO.cleanup()

