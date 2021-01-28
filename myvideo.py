
import os
import configparser
import requests

import time

import D_mipicamera as Dcam

import ctypes


# read .ini according to section
def read_config(r_cfg_file, section):
    print("Read config from " + os.path.abspath(r_cfg_file))
    config = configparser.ConfigParser()
    config.read(r_cfg_file, encoding='utf-8')
    config_dict = dict(config.items(section))
    # print(config.sections())
    print('{0} = {1}'.format(section, config_dict))
    return config_dict

cfg_file = '/home/pi//raspberrypi/D_mipi_rpi/python_demo/lasercfg.ini'
fj_id = read_config(cfg_file, 'fj_id')
url = read_config(cfg_file, 'http_url')
record_time = read_config(cfg_file, 'record_time')

video_record_time = int(record_time['video_record_time'])
print(video_record_time)
save_dir = read_config(cfg_file,'data_dir')

time_now = str(int(time.time()))

def video_post():
    try:
        #video_url = 'http://192.168.199.124:10001/file/fileUpload/vedio'
        video_url = url['video_url']
        print(video_url)
        file1 = {'fileName': open(videofilename, 'rb')}
        response = requests.post(video_url, files=file1)
        if response.status_code == 200:
            json = response.json()
            print(json)
            os.remove(videofilename)
    except Exception as e:
        print(e)



def callback(data):
    buff = Dcam.buffer(data)
    print("one frame len %d" % buff.length)
    file = buff.userdata
    buff.as_array.tofile(file)
    return 0

try:
    camera = Dcam.mipi_camera()
    print("Open camera...")
    camera.init_camera()
    videofilename = save_dir['datadir']+'video_' + time_now + '_' + fj_id['id'] + '.h264'
    print(videofilename)
    file = open(videofilename, "wb")
    # Need keep py_object reference
    file_obj = ctypes.py_object(file)
    camera.start_video_stream(callback, file_obj)
    time.sleep(video_record_time)
    camera.stop_video_stream()
    file.close()
    print("Close camera...")
    camera.close_camera()
except Exception as e:
    print(e)



