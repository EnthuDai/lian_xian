import os
import time


class MobileOperation:
    @staticmethod
    def open(corp_name, package_name):
        """
        通过包名打开App，
        :parameter corp_name app的公司名称
        :parameter package_name app的包名
        手动打开App后通过 adb shell "dumpsys window | grep mCurrentFocus" 命令可获得以上两个参数
        eg: mCurrentFocus=Window{2805af6 u0 com.lx.jdhg/com.ly.lxdr.AppActivity} 中corp_name 为 com.lx.jdhg，
        package_name 为 com.lx.jdhg/com.ly.lxdr.AppActivity
        :return:void
        """
        os.system("adb shell am force-stop " + corp_name)  # 强制关闭
        time.sleep(2)
        os.system("adb shell am start -n " + package_name)  # 启动

    @staticmethod
    def click(x, y):
        """
        模拟点击， x，y坐标，xy坐标可以开启手机开发者选项中 指针位置 选项后获得，或者通过 Sdk\tools\monitor.bat 获得
        :param x: x坐标
        :param y: y坐标
        """
        cmd = str('adb shell input tap %d %d' % (x, y))
        os.system(cmd)
        print("自动点击-> x:%d, y:%d" % (x, y))

    @staticmethod
    def get_screen_shot():
        """
        获得当前页面截图
        :return 截图在电脑中的地址
        """
        os.system('adb shell screencap -p /sdcard/01.png')
        os.system('adb pull /sdcard/01.png')
        return "01.png"

    @staticmethod
    def swipe(x1, y1, x2, y2):
        """手机模拟滑动"""
        t = (abs(x1-x2) + abs(y1-y2)) // 2
        os.system('adb shell input swipe %d %d %d %d %d' % (x1, y1, x2, y2, t))
        print("自动滑动: %d, %d -> %d,%d" % (x1, y1, x2, y2))


if __name__ == '__main__':
    MobileOperation.get_screen_shot()
