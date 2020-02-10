import json
import math
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

while True:
    mo.click(params['yi_xian_tian_x'], params['yi_xian_tian_y'])
    time.sleep(1)
    mo.click(params['yi_xian_tian_confirm_x'], params['yi_xian_tian_confirm_y'])
    time.sleep(1)
    count = 0
    while True:
        try:
            reco = Recognizer(mo.get_screen_shot())
            table = reco.find()
            path = table.find_path()
            index = 0
            while index < len(path) - 1:
                mo.swipe(path[index][0] + params['main_area_west'], path[index][1] + params['main_area_north'],
                           path[index + 1][0] + params['main_area_west'], path[index + 1][1] + params['main_area_north'])
                index += 1
            time.sleep(1)
            count += 1
            if count >= 30:
                mo.click(params['collect_button_x'], params['collect_button_y'])
                break
            time.sleep(1)
        except Exception as e:
            print(e)
            break





