
#删除文件夹下面的所有文件(只删除文件,不删除文件夹)
import os
import shutil
#python删除文件的方法 os.remove(path)path指的是文件的绝对路径,如：
# os.remove(r"E:\code\practice\data\1.py")#删除文件
# os.rmdir(r"E:\code\practice\data\2")#删除文件夹（只能删除空文件夹）
# shutil.rmtree(r"E:\code\practice\data\2")#删除文件夹
# path_data = "E:\code\practice\data"#
def del_file(path_data):
    for i in os.listdir(path_data) :# os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data  + i#当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:#os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)
path_data ='/home/pi/data/'
del_file(path_data)



import serial
import time
serial = serial.Serial('/dev/ttyAMA0','115200',timeout=0.5)
print(serial.port)
time_now = str(int(time.time()))
time1 = int(time.time())
fj_id = "yepian-status-116"
laser_filename = '/home/pi/data/'+'laser_'+time_now+'_'+ fj_id+'.txt'
print(laser_filename)
try:
    while True:
        Byte_H = serial.read(1)
        Byte_L = serial.read(1)

        res = (ord(Byte_H) & 0x7f) * 128 + (ord(Byte_L) & 0x7f)
        #print(res)
        ss = str(res) + '\n'
        with open(laser_filename, 'a') as f:
            f.write(ss)
        time2 = int(time.time())
        #print(time2 - time1)
        collectTime = 30
        #print(collectTime)
        if (time2 - time1 == collectTime):
            print('close')

            serial.close()
            print(serial.isOpen())

except Exception as e:
    print(e)

import numpy as np
import matplotlib.pylab as plt
import itertools

from collections import OrderedDict

frequency = 1250

per_qian = 0.2
per_zhong = 0.4
per_hou = 1 - per_qian - per_zhong

# 原始数据
data = []
# 这里是读取文件中的数据
#file = open(r"C:\Users\DeepForest\Desktop\112d.txt")
file = open(laser_filename)
for line in file.readlines():
    data.append(float(line.split()[0]))
# print(len(data))
# plt.scatter(range(len(data)),data)
# plt.show()

da = []
for i in data:
    if i < 8000 and i > 1000:
        da.append(i)
    if i >= 8000 or i <= 1000:
        da.append(16000)

# da1=[]
# for i, val in enumerate(da[:-2]):
#     if val !=16000:
#         da1.append(val)
#     if val==16000 :
#         da1.append(min([da[i-1]/2+da[i+1]/2,da[i-2]/2+da[i+1]/2,da[i-2]/2+da[i+2]/2,da[i-1]/2+da[i+2]/2]))

# print(min(da1))
# print(np.average(da))

num = 15
per = 0.5

# plt.scatter(range(len(da1)),da1)
# plt.show()

# data[0*num:0*num+num]=[16000 for i in data[0*num:0*num+num]]
data_new = []
count = 0
for i in np.arange(int(len(da) / num)):

    datai = sorted(da[i * num:i * num + num])
    minstd = 100000
    for n in range(int(num * per)):
        if np.std(datai[n:len(datai) - int(num * per) + n]) < minstd:
            minstd = np.std(datai[n:len(datai) - int(num * per) + n])
            aver = np.average(datai[n:len(datai) - int(num * per) + n])
    # print(minstd)

    if minstd >= 500 or aver >= 10000:
        count = count + 1
    if minstd < 500 and aver < 10000:

        if count * num > 100:
            data_new.append(count * num + 16000)

        for k in da[i * num:i * num + num]:
            data_new.append(k)
        count = 0

data_neww = []
for i, val in enumerate(data_new[:-2]):
    if val != 16000:
        data_neww.append(val)
    if val == 16000:
        for m in data_new[i::-1]:
            if m < 16000:
                pre = m
                break
        for n in data_new[i::]:
            # print(n)
            if n < 16000:
                aft = n
                break
        try:
            data_neww.append((pre + aft) / 2)
        except NameError:
            data_neww.append(aft / 2)
        # data_neww.append(min([data_new[i-1]/2+data_new[i+1]/2,data_new[i-2]/2+data_new[i+1]/2,data_new[i-2]/2+data_new[i+2]/2,data_new[i-1]/2+data_new[i+2]/2]))
data_neww_aver = np.average(data_neww)
data_neww_std = np.std(data_neww)

data_f = np.array(data_neww)

index = np.sort(np.append(np.where(((data_f > np.average(data_f[data_f < 16000]) - 3 * np.std(
    data_f[data_f < 16000])) & (data_f < np.average(data_f[data_f < 16000]) + 3 * np.std(data_f[data_f < 16000])))),
                          np.where(data_f > 16000)))
# print(index)

data_ff = data_f[index]
data_f = data_ff
# data_ff=[]
# for i in data_f:
#     if (i>np.average(data_f[data_f<16000])-3*np.std(data_f[data_f<16000]) and   i<np.average(data_f[data_f<16000])+3*np.std(data_f[data_f<16000])) or i>16000:
#         data_ff.append(i)

data_ff = data_f

# print(np.average(data_f[data_f<16000]),np.std(data_f[data_f<16000]))
# plt.scatter(range(len(data_ff)), data_ff)
#
# plt.show()

# print(min(data_ff))

line = np.where(data_f > 16000)[0]

# plt.scatter(np.arange(len(data_new)),data_new)

# print(line)
# print(line[0:-3])
# print(line[0:-3:3])

data11 = []
data22 = []
data33 = []

for i, val in enumerate(line[0:-3:3]):
    # print(data_f[line[0::3][i]:line[0::3][i]
    # print(val)
    # print(line[3*i:3*i+4])

    data1 = data_f[line[3 * i] + 1:line[3 * i + 1]]
    data2 = data_f[line[3 * i + 1] + 1:line[3 * i + 2]]
    data3 = data_f[line[3 * i + 2] + 1:line[3 * i + 3]]

    data11.extend(data1)
    data22.extend(data2)
    data33.extend(data3)

    max_len = max(len(data1), len(data2), len(data3))
    # if i !=3:
    #     plt.scatter(np.linspace(0, max_len, len(data1)), data1, c='r', label='一号叶片')
    #     plt.scatter(np.linspace(0, max_len, len(data2)), data2, c='b', label='二号叶片')
    #     plt.scatter(np.linspace(0, max_len, len(data3)), data3, c='g', label='三号叶片')
    # if i==3:
    #     plt.scatter(np.linspace(0, max_len, len(data1)), data1, c='r', label='一号叶片')
    #     plt.scatter(np.linspace(0, max_len, len(data2)), data2, c='b', label='二号叶片')

max_len1 = max(len(data11), len(data22), len(data33))

#
# print(np.average(data11),np.average(data22),np.average(data33))
# print(np.std(data11),np.std(data22),np.std(data33))
standar_min1 = np.min([np.min(data11), np.min(data22), np.min(data33)])
standar_max1 = np.max([np.max(data11), np.max(data22), np.max(data33)])

data11 = (data11 - standar_min1) / (standar_max1 - standar_min1)
data22 = (data22 - standar_min1) / (standar_max1 - standar_min1)
data33 = (data33 - standar_min1) / (standar_max1 - standar_min1)

# print(np.average(data11),np.average(data22),np.average(data33))
# print(np.std(data11),np.std(data22),np.std(data33))

# for i, val in enumerate(line[0:]):
#     print(line[i])

# print(data_f[line[i]+1:line[i+1]])
# print(data_f[line[i+1]+1:line[i + 2]])

data123 = [[] for i in range(3)]
aver123 = [[] for i in range(3)]
std = []

aver1 = []
aver2 = []
aver3 = []

std1 = []
std2 = []
std3 = []

standar_aver1 = []
standar_aver2 = []
standar_aver3 = []

inter1 = []
inter2 = []
inter3 = []

standar_inter1 = []
standar_inter2 = []
standar_inter3 = []

qian_aver1 = []
qian_aver2 = []
qian_aver3 = []

zhong_aver1 = []
zhong_aver2 = []
zhong_aver3 = []

hou_aver1 = []
hou_aver2 = []
hou_aver3 = []

qian = []
zhong = []
hou = []

ii = 2
for i in data_f:
    if i <= 16000:
        data123[ii].append(i)
    if i > 16000:
        if ii == 2:
            ii = 0

            try:
                if len(data123[0]) != 0 and len(data123[1]) != 0 and len(data123[2]) != 0:
                    std1.append(np.std(data123[0]))
                    std2.append(np.std(data123[1]))
                    std3.append(np.std(data123[2]))

                    aver1.append(np.average(data123[0]))
                    aver2.append(np.average(data123[1]))
                    aver3.append(np.average(data123[2]))

                    max_len = np.max([len(data123[0]), len(data123[1]), len(data123[2])])

                    inter1.append(
                        (sum(data123[0]) * 2 - data123[0][0] - data123[0][-1]) * max_len / 2 / len(data123[0]))
                    inter2.append(
                        (sum(data123[1]) * 2 - data123[1][0] - data123[1][-1]) * max_len / 2 / len(data123[1]))
                    inter3.append(
                        (sum(data123[2]) * 2 - data123[2][0] - data123[2][-1]) * max_len / 2 / len(data123[2]))

                    standar_min = np.min([np.min(data123[0]), np.min(data123[1]), np.min(data123[2])])
                    standar_max = np.max([np.max(data123[0]), np.max(data123[1]), np.max(data123[2])])

                    data123[0] = (data123[0] - standar_min) / (standar_max - standar_min)
                    data123[1] = (data123[1] - standar_min) / (standar_max - standar_min)
                    data123[2] = (data123[2] - standar_min) / (standar_max - standar_min)

                    qian_aver1.append(np.average(data123[0][0:int(per_qian * len(data123[0]))]))
                    qian_aver2.append(np.average(data123[1][0:int(per_qian * len(data123[1]))]))
                    qian_aver3.append(np.average(data123[2][0:int(per_qian * len(data123[2]))]))

                    zhong_aver1.append(np.average(
                        data123[0][int(per_qian * len(data123[0])):int((per_qian + per_zhong) * len(data123[0]))]))
                    zhong_aver2.append(np.average(
                        data123[1][int(per_qian * len(data123[1])):int((per_qian + per_zhong) * len(data123[1]))]))
                    zhong_aver3.append(np.average(
                        data123[2][int(per_qian * len(data123[2])):int((per_qian + per_zhong) * len(data123[2]))]))

                    hou_aver1.append(np.average(data123[0][int((per_qian + per_zhong) * len(data123[0])):]))
                    hou_aver2.append(np.average(data123[1][int((per_qian + per_zhong) * len(data123[1])):]))
                    hou_aver3.append(np.average(data123[2][int((per_qian + per_zhong) * len(data123[2])):]))

                    qian.append(np.max([qian_aver1[-1], qian_aver2[-1], qian_aver3[-1]]) - np.min(
                        [qian_aver1[-1], qian_aver2[-1], qian_aver3[-1]]))
                    zhong.append(np.max([zhong_aver1[-1], zhong_aver2[-1], zhong_aver3[-1]]) - np.min(
                        [zhong_aver1[-1], zhong_aver2[-1], zhong_aver3[-1]]))
                    hou.append(np.max([hou_aver1[-1], hou_aver2[-1], hou_aver3[-1]]) - np.min(
                        [hou_aver1[-1], hou_aver2[-1], hou_aver3[-1]]))

                    standar_aver1.append(np.average(data123[0]))
                    standar_aver2.append(np.average(data123[1]))
                    standar_aver3.append(np.average(data123[2]))

                    # print(sum(data123[0]),sum(data123[1]),sum(data123[2]))

                    standar_inter1.append(
                        (sum(data123[0]) * 2 - data123[0][0] - data123[0][-1]) * max_len / 2 / len(data123[0]))
                    standar_inter2.append(
                        (sum(data123[1]) * 2 - data123[1][0] - data123[1][-1]) * max_len / 2 / len(data123[1]))
                    standar_inter3.append(
                        (sum(data123[2]) * 2 - data123[2][0] - data123[2][-1]) * max_len / 2 / len(data123[2]))

                    std.append(min([np.std(data123[0]), np.std(data123[1]), np.std(data123[2])]) / max(
                        [np.std(data123[0]), np.std(data123[1]), np.std(data123[2])]))
            except RuntimeWarning:
                pass
            # print([np.std(data123[0]),np.std(data123[1]),np.std(data123[2])])
            data123 = [[] for i in range(3)]
        else:
            ii = ii + 1

# print(np.average(qian_aver1),np.average(qian_aver2),np.average(qian_aver3))
# print(np.average(zhong_aver1),np.average(zhong_aver2),np.average(zhong_aver3))
# print(np.average(hou_aver1),np.average(hou_aver2),np.average(hou_aver3))

huiwu = np.max(zhong)
niuzhuan1 = np.max(qian)
niuzhuan2 = np.max(hou)

kongxi = data_f[line] - 16000

if (len(line) - 1) % 3 == 0:
    rpm = 60 * frequency * len(qian) / (sum(kongxi[1:]) + len(data11) + len(data22) + len(data33))
if (len(line) - 1) % 3 != 0:
    rpm = 60 * frequency * len(qian) / (
                sum(kongxi[1:-((len(line) - 1) % 3)]) + len(data11) + len(data22) + len(data33))


print(huiwu, niuzhuan2, niuzhuan1, rpm)

import requests
import json



url = 'http://192.168.34.116:12521/laser-data/laserDatasupload.do'
# url1 = url.encode('url-8')
OriginData = {
    "createTime": time_now,
    "sensorId": fj_id,
    "huiwu": huiwu,
    "niuzhuan1": niuzhuan1,
    "niuzhuan2": niuzhuan2,
    "rpm": rpm
}
print(OriginData)
resp = requests.post(url, json=OriginData, timeout=5)
print(resp.json())


