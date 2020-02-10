import os

from Monitor import Monitor
#


Monitor.show_operation()

# a = os.popen('adb shell "dumpsys window | grep mCurrentFocus"')
# # 此时打开的a是一个对象，如果直接打印的话是对象内存地址
#
# text = a.read()
# # 要用read（）方法读取后才是文本对象
#
# print(text)
