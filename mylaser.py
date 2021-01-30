# cython: language_level=3
'''
    1.激光测距(√)
    2.数据上传(√)
    3.激光计算(√)
    4.视频录像(√)
    5.视频计算
    6.视频上传(√)
    7.挑选最大值上传
'''

import threading

import numpy as np

import os
import configparser
import requests
import csv

import time
import math

import serial

thread_laser_record = None
thread_laser_jisuan = None
thread_laser_post = None

event_laser_record = threading.Event()
event_laser_jisuan = threading.Event()
event_laser_post = threading.Event()


# read .ini according to section
def read_config(r_cfg_file, section):
    print("Read config from " + os.path.abspath(r_cfg_file))
    config = configparser.ConfigParser()
    config.read(r_cfg_file, encoding='utf-8')
    config_dict = dict(config.items(section))
    # print(config.sections())
    print('{0} = {1}'.format(section, config_dict))
    return config_dict

def set_config(w_cfg_file, section, key, value):
    print("Save config to " + os.path.abspath(w_cfg_file))
    config = configparser.ConfigParser()
    config.read(w_cfg_file, encoding='utf-8')
    config.set(section, key, value)
    with open(w_cfg_file, 'w', encoding='utf-8') as cfgfile:
        config.write(cfgfile)

is_exit = False

cfg_file = '/home/pi//raspberrypi/D_mipi_rpi/python_demo/lasercfg.ini'
fj_id = read_config(cfg_file, 'fj_id')
url = read_config(cfg_file, 'http_url')
com_cfg = read_config(cfg_file, 'com_cfg')
port = com_cfg['port']
bsp = com_cfg['bsp']
record_time = read_config(cfg_file, 'record_time')

time_now = ''

de = []  # 距离差异指标
health = []  # 健康指标
health_filename = ''
de_filename = ''

collectRange = int(record_time['collect_range'])
print(collectRange)
collectTime = int(record_time['collect_time'])
print(collectTime)
uploadTime = int(record_time['update_time'])
print(uploadTime)

yuzhi = float(record_time['yuzhi'])
print(yuzhi)

# serial = serial.Serial('/dev/ttyUSB0', '115200', timeout=0.5)
# serial = serial.Serial('/dev/ttyAMA0', '115200', timeout=0.5)
serial = serial.Serial(port, bsp, timeout=0.5)
laser_filename = ''

save_dir = read_config(cfg_file,'data_dir')


def postmydata(datatype,datavalue):
    global uploadTime
    global collectRange
    global collectTime
    try:
        def wirtedata(datatype,datavalue):
            headers = ['type', 'value', 'createTime', 'sensorId']
            rows = [
                datatype,
                datavalue,
                time_now,
                fj_id['id']
            ]
            print('rows',rows)
            with open('/home/pi/laser/python_demo/data.csv', 'a')as f:
                f_csv = csv.writer(f)
                #f_csv.writerow(headers)
                f_csv.writerow(rows)


        json_url = url['laserres_url']
        #url = 'http://192.168.199.124:12521/laser-data/laserDataupload.do'
        #url1 = url.encode('url-8')
        OriginData = {
                "createTime": time_now,
                "sensorId": fj_id['id'],
                "value": datavalue,
                "type" : datatype
            }
        print(OriginData)
        resp = requests.post(json_url, json = OriginData,timeout=5)

        if(resp.status_code == 200):
            json = resp.json()
            print(json)
            collectTime = json['data']['collectTime']
            collectRange = json['data']['collectRange']
            uploadTime = json['data']['uploadTime'] * 10
            print('\033[1;33m post k = {0}\033[0m'.format(uploadTime))
            print('RECORD_SECONDS', collectTime)
            print('sleep_time', collectRange)

            set_config(cfg_file,'record_time','collect_time')
            set_config(cfg_file, 'record_time','collect_range')
            set_config(cfg_file, 'record_time', 'update_time')

        else:
            #upload failed ,save data to csv
            print('\033[1;35mupload failed ,save to csv \033[0m')
            wirtedata(datatype,datavalue)
    except :

        print('weizhiyichang')
        print('\033[1;35mupload failed ,save to csv \033[0m')
        wirtedata(datatype, datavalue)

def laser_record():
    global laser_filename
    global time_now
    print('laser record...')
    time_now = str(int(time.time()))
    print(serial.port)
    #file_dir = "./"
    laser_filename = save_dir['datadir']+'laser_'+time_now+'_'+ fj_id['id']+'.txt'
    print(laser_filename)
    time1 = int(time.time())
    #laser_record_time = 5
    if not serial.is_open:
        print('open')
        serial.open()
    try:
        while True:
            Byte_H = serial.read(1)
            Byte_L = serial.read(1)

            res = (ord(Byte_H) & 0x7f) * 128 + (ord(Byte_L) & 0x7f)
            print(res)
            ss = str(res) + '\n'
            with open(laser_filename, 'a') as f:
                f.write(ss)
            time2 = int(time.time())
            #print(time2)
            #print(time1)
            print(time2 - time1)
            if (time2 - time1 == collectTime):
                print('close')

                serial.close()
                print(serial.isOpen())

    except Exception as e:
        print(e)


def laser_jisuan():
    global am_ratio
    global am_diff


    # 原始数据
    data = []

    # 这里是读取文件中的数据
    #file = open("/home/pi/laser/python_demo/laser_1603765204_sdrc54350.txt")
    file = open(laser_filename)
    for line in file.readlines():
        data.append(float(line.split()[0]))

    f = 312.66  # 频率hz
    Lt = 15590  # 距离阈值
    Lt_ = 4000  # 距离下阈值

    filt_per = 0.2  # 头尾数据过滤百分比

    quan_di = 0.8
    quan_zh = 0.6
    quan_ga = 0.6  # 低中高风速下的权重

    di_w = 10
    zh_w = 8
    ga_w = 6  # 低中高转速临界值

    # 叶片原始距离数据
    data123 = []
    data12 = []
    data1 = []
    data2 = []
    data3 = []
    # 清洗后的叶片距离数据
    data11 = []
    data22 = []
    data33 = []
    # 叶片转速
    w1 = []
    w2 = []
    w3 = []
    # 叶片均值
    la1 = []
    la2 = []
    la3 = []
    # 叶片标准差
    ld1 = []
    ld2 = []
    ld3 = []
    # 叶片振幅
    am1 = []
    am2 = []
    am3 = []

    index1 = []  # 一号叶片
    index2 = []  # 二号叶片
    index3 = []  # 三号叶片

    # print(np.where(np.array(data12)<Lt))

    for index, value in enumerate(data[:-2]):
        if value > Lt:
            data12.append(value)
        if value < Lt and value > Lt_:
            if np.min([data[index - 2], data[index - 1], data[index + 1], data[index + 2]]) < Lt:
                data12.append(value)

    # 筛选阈值以内的数据
    b = np.where(np.array(data12) < Lt)

    # 一些初始参数
    k = 1
    t3 = b[0][0]
    m3 = 0
    m2 = 0
    q1 = []
    q2 = []
    q3 = []

    am_ratio = []  # 最大幅值与最小之比
    am_diff = []  # 幅值之差

    for index, value in enumerate(b[0]):
        # print(value,b[0][index])

        data123.append(data12[value])

    print(data123)

    for index, value in enumerate(b[0]):
        if b[0][index] - b[0][index - 1] > 3:
            if k == 1:
                t1 = value
                m1 = index
                w_1 = 1 / 3 * 60 * f / (t1 - t3)
                w1.append(w_1)
                recount1 = int((m1 - m3 + 1) * filt_per)  # 设置去掉头尾的数据，剩余的用来求均值和方差
                x1max = np.mean(data123[m3 + recount1:m1 - recount1]) + 2 * np.std(
                    data123[m3 + recount1:m1 - recount1])  # 2倍σ以下
                x1min = np.mean(data123[m3 + recount1:m1 - recount1]) - 2 * np.std(
                    data123[m3 + recount1:m1 - recount1])  # 2倍σ以上
                d1new = list(filter(lambda x: (x < x1max or x == x1max) and (x > x1min or x == x1min), data123[m3:m1]))

                aam1 = np.max(d1new) - np.min(d1new)
                am1.append(aam1)

                data11.extend(d1new)

                q1.append(len(data11))
                # print(data11)
                # qqq.append(len(data11))
                # print(np.median(data1))
                # print(np.std(data1))

                # la1.append(np.average(list(filter(lambda x : x < np.median(data123[m3:m1])+3*np.std(data123[m3:m1]) ,data123[m3:m1]))))
                la1.append(np.average(d1new))
                ld1.append(np.std(d1new))

                # print(t1,m1)
            if k == 2:
                t2 = value

                m2 = index

                w_2 = 1 / 3 * 60 * f / (t2 - t1)
                w2.append(w_2)

                recount2 = int((m2 - m1 + 1) * filt_per)  # 设置去掉头尾部分的数据，剩余的用来求均值和方差
                x2max = np.mean(data123[m1 + recount2:m2 - recount2]) + 2 * np.std(
                    data123[m1 + recount2:m2 - recount2])  # 2倍σ以下
                x2min = np.mean(data123[m1 + recount2:m2 - recount2]) - 2 * np.std(
                    data123[m1 + recount2:m2 - recount2])  # 2倍σ以上

                print(recount2, x2max, x2min)

                d2new = list(filter(lambda x: (x < x2max or x == x2max) and (x > x2min or x == x2min), data123[m1:m2]))
                # print(d2new)

                aam2 = np.max(d2new) - np.min(d2new)
                am2.append(aam2)

                data22.extend(d2new)
                q2.append(len(data22))

                la2.append(np.average(d2new))
                ld2.append(np.std(d2new))

                # print(t2,m2)
            if k == 3:
                t3 = value

                m3 = index

                w_3 = 1 / 3 * 60 * f / (t3 - t2)
                w3.append(w_3)

                recount3 = int((m3 - m2 + 1) * filt_per)  # 设置去掉头尾部分的数据，剩余的用来求均值和方差
                x3max = np.mean(data123[m2 + recount3:m3 - recount3]) + 2 * np.std(
                    data123[m2 + recount3:m3 - recount3])  # 2倍σ以下
                x3min = np.mean(data123[m2 + recount3:m3 - recount3]) - 2 * np.std(
                    data123[m2 + recount3:m3 - recount3])  # 2倍σ以上
                d3new = list(filter(lambda x: (x < x3max or x == x3max) and (x > x3min or x == x3min), data123[m2:m3]))

                aam3 = np.max(d3new) - np.min(d3new)
                am3.append(aam3)

                data33.extend(d3new)

                q3.append(len(data33))

                la3.append(np.average(d3new))
                ld3.append(np.std(d3new))

                amm_ratio = np.max([aam1, aam2, aam3]) / np.min([aam1, aam2, aam3])
                am_ratio.append(amm_ratio)

                amm_diff = np.max([aam1, aam2, aam3]) - np.min([aam1, aam2, aam3])
                am_diff.append(amm_diff)

                w_mean = (w_1 + w_2 + w_3) / 3

                quan = np.select([w_mean >= ga_w, w_mean >= zh_w, w_mean >= di_w],
                                 [quan_ga, quan_zh, quan_di])  # 低中高风速下的权重

                # print(t3,m3)
            k = 1 if k == 3 else k + 1
        if k == 1:
            index1.append(value)
            data1.append(data[value])

        if k == 2:
            index2.append(value)
            data2.append(data[value])
        if k == 3:
            index3.append(value)
            data3.append(data[value])

    # print(data11)
    # print(la1)
    # print(la2)
    # print(w1,w2,w3)
    ytickmin = int((np.min([np.min(data11), np.min(data22), np.min(data33)])))
    ytickmax = math.ceil((np.max([np.max(data11), np.max(data22), np.max(data33)])))


def laser_record_thread():
    while not is_exit:
        try:
            if event_laser_record.is_set():
                event_laser_record.clear()

                laser_record()

                event_laser_jisuan.set()

            else:
                event_laser_record.wait()
        except ValueError as e:
            print("record error")
            event_laser_jisuan.clear()

def laser_jisuan_thread():
    while not is_exit:
        try:
            if event_laser_jisuan.is_set():
                event_laser_jisuan.clear()
                print('laser jisuan start！')
                laser_jisuan()
                print('laser jisuan ok!')
                event_laser_post.set()
            else:
                event_laser_jisuan.wait()
        except BaseException as e:
            print(e)
            event_laser_post.clear()


# when upload setted,start http upload
def laser_post_thread():
    global collectRange
    global collectTime
    global count
    global uploadTime
    ''' 文件上传'''
    #30一次post laser 原始文件
    laser_count = 0
    while not is_exit:
        try:

            if event_laser_post.is_set():
                event_laser_post.clear()

                print('upload')
                postmydata("ratio",am_ratio)
                postmydata("diff",am_diff)
                print("post res ok!")
                # upload

                #laser_url = 'http://192.168.199.124:10001/file/fileUpload/laser'
                laser_url = url['laser_url']
                print(laser_url)

                #上传原始文件
                laser_count = laser_count + 1
                print('\033[1;33m laser post count = {0}/{1}\033[0m'.format(laser_count,uploadTime))
                if laser_count == uploadTime:
                    #喂狗
                    laser_count = 0

                    file3 = {'fileName': open(laser_filename, 'rb')}
                    response = requests.post(laser_url, files=file3)
                    if response.status_code == 200:
                        json = response.json()
                        print(json)
                        collectTime = json['data']['collectTime']
                        collectRange = json['data']['collectRange']
                        uploadTime = json['data']['uploadTime'] * 10
                        print('\033[1;33m post k = {0}\033[0m'.format(uploadTime))
                        print('RECORD_SECONDS', collectTime)
                        print('sleep_time', collectRange)
                        os.remove(laser_filename)



                # event_video_record.set()
                else:
                    event_laser_post.wait()

        except BaseException as e:
            print(e)
            event_laser_post.clear()



# start record thread . manified target.
def laser_record_thread_start():
    global thread_laser_record
    if thread_laser_record is None:
        print("laser_record_thread_start")
        thread_audio_record = threading.Thread(target=laser_record_thread)
        thread_audio_record.setDaemon(True)
        thread_audio_record.start()

# start post thread . manified target .
def laser_jisuan_thread_start():
    global thread_laser_jisuan
    if thread_laser_jisuan is None:
        print("laser_jisuan_thread_start")
        thread_laser_jisuan = threading.Thread(target=laser_jisuan_thread)
        thread_laser_jisuan.setDaemon(True)
        thread_laser_jisuan.start()

# start post thread . manified target .
def laser_post_thread_start():
    global thread_laser_post
    if thread_laser_post is None:
        print("laser_post_thread_start")
        thread_laser_post = threading.Thread(target=laser_post_thread)
        thread_laser_post.setDaemon(True)
        thread_laser_post.start()



#if __name__ == '__main__':
def run():

    laser_record_thread_start()
    laser_jisuan_thread_start()
    laser_post_thread_start()

    while not is_exit:
        # start record
        event_laser_record.set()
        #event_laser_jisuan.set()
        print('sleep for ', collectRange)
        time.sleep(collectRange)

run()


