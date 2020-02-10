import json
import os
import time

from MobileOperation import MobileOperation
from Recognizer import Recognizer
# 载入配置文件
f = open('config.json', 'r', encoding='utf-8')
text = f.read()
f.close()
params = json.loads(text)
mo = MobileOperation()


def restart_app():
    mo.open("com.lx.jdhg", "com.lx.jdhg/com.ly.lxdr.AppActivity")
    time.sleep(4)
    mo.click(params['skip2_x'], params['skip2_y'])
    mo.click(params['skip_x'], params['skip_y'])
    mo.click(params['start_button_x'], params['start_button_y'])


while True:
    current = time.time()*1000
    p = os.popen('adb shell "dumpsys window | grep mCurrentFocus"')  # 启动前检测是否在正确的页面
    result = str(p.read())
    if not result[:-1].endswith("com.lx.jdhg/com.ly.lxdr.AppActivity}"):
        restart_app()
        continue
    reco = Recognizer(mo.get_screen_shot())
    try:
        table = reco.find()
        path = table.find_path(True)
        step_time = time.time()*1000
        index = 0
        while index < len(path) - 1:
            mo.swipe(path[index][0] + params['main_area_west'], path[index][1] + params['main_area_north'],
                     path[index+1][0] + params['main_area_west'], path[index+1][1] + params['main_area_north'])
            index += 1
        print("滑动耗时 %d ms" % (time.time() * 1000 - step_time,))
        mo.click(params['collect_button_x'], params['collect_button_y'])
        time.sleep(0.5)
        mo.click(params['next_x'], params['next_y'])
        time.sleep(0.5)
    except Exception as e:
        print(e)
        restart_app()
    print("本关耗时 %d ms" % (time.time()*1000 - current,))


