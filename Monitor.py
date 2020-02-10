import time

import cv2


class Monitor:
    id = ""
    scale = 1

    def __init__(self):
        pass

    def show(self, image, sleep_time=0):
        """
        显示图片
        :param image: 图片的路径或者是img对象
        :param sleep_time: 显示时间，0代表一直显示
        :return:
        """
        if self.id == "":
            self.id = "image"
            cv2.namedWindow(self.id, cv2.WINDOW_NORMAL)
        if isinstance(image, str):
            image = cv2.imread(image)
        cv2.resizeWindow(self.id, image.shape[0] * self.scale, image.shape[1] * self.scale)
        cv2.imshow(self.id, image)
        cv2.waitKey(sleep_time)

    def show_grey(self, image, sleep_time=0):
        if isinstance(image, str):
            image = cv2.imread(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.show(gray, sleep_time)

    @staticmethod
    def show_operation():
        cv2.namedWindow("operation", cv2.WINDOW_NORMAL)
        while True:
            try:
                operation_image = cv2.imread("operation.png")
                cv2.resizeWindow("operation", int(operation_image.shape[0] * 0.5), int(operation_image.shape[1] * 0.5))
                cv2.imshow("operation", operation_image)
                cv2.waitKey(25)
            except BaseException:
                time.sleep(1)


if __name__ == '__main__':
    import json
    f = open('config.json', 'r', encoding='utf-8')
    text = f.read()
    f.close()
    params = json.loads(text)

    image_path = "01.png"
    save_path = "01_grey.png"
    monitor = Monitor()
    image = cv2.imread(image_path)[params['main_area_north']: params['main_area_south'],
        params['main_area_west']: params['main_area_east']]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite(save_path, gray)
    ret, im_fixed = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    monitor.show(im_fixed)
