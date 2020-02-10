import time
import numpy as np

from array import array

import cv2

from MobileOperation import MobileOperation
from table import Block, Table
from Monitor import Monitor


class Recognizer:
    image = None
    operation_image = None

    min_area = 8000  # 最小域面积，用于去除起点块的尾巴围成的区域

    def __init__(self, image, cut=True):
        """
        :param image:图片路径字符串或cv2image
        """
        self.image = cv2.imread(image) if isinstance(image, str) else image
        if cut:
            # 截取作答区域
            import json
            f = open('config.json', 'r', encoding='utf-8')
            text = f.read()
            f.close()
            params = json.loads(text)
            self.image = self.image[params['main_area_north']: params['main_area_south'],
                    params['main_area_west']: params['main_area_east']]
        cv2.imwrite("operation.png", self.image)

    def binarize(self):
        """
        二值化，将无关区域显示为白色，相关区域显示为黑色
        :return: 二值化后的图片
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)  # 取得灰度图片
        ret, im_fixed = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)  # 灰度图片二值化
        self.operation_image = im_fixed
        return im_fixed

    def clear_noise(self):
        """
        消除起点的尾巴和胡须
        :return:
        """
        for rowIndex in range(0, len(self.operation_image)):
            black_count = 0
            for point in self.operation_image[rowIndex]:
                if point == 0:
                    black_count += 1
                    if not black_count < 100:
                        break
            if black_count < 100:
                for colIndex in range(0, len(self.operation_image[rowIndex])):
                    if self.operation_image[rowIndex, colIndex] == 0:
                        self.operation_image[rowIndex, colIndex] = 255
        for colIndex in range(0, len(self.operation_image[0])):
            black_count = 0
            for rowIndex in range(0, len(self.operation_image)):
                if self.operation_image[rowIndex][colIndex] == 0:
                    black_count += 1
                    if not black_count < 100:
                        break
            if black_count < 10:
                for rowIndex in range(0, len(self.operation_image)):
                    if self.operation_image[rowIndex, colIndex] == 0:
                        self.operation_image[rowIndex, colIndex] = 255

    def find(self):
        self.binarize()
        self.clear_noise()
        contours, hierarchy = cv2.findContours(self.operation_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 找出轮廓
        if len(contours) > 100 or len(contours) < 4:
            raise Exception("色块数目异常！ 如确认无误，请修改此处的判断条件！")
        # cv2.drawContours(self.image, contours, -1, (0, 0, 255), 3)  # 显示轮廓
        # cv2.imshow("image2", self.image)

        result = []
        max_area = 0
        begin_index = 0
        current = time.time()*1000
        area_list = []
        for contourIndex in range(0, len(contours)):  # 删除最外层的轮廓
            area = cv2.contourArea(contours[contourIndex])
            if area > 200000:
                tmp = contours[contourIndex]
                contours[contourIndex] = contours[-1]
                contours[-1] = tmp
                contours.pop()
                break
        for contourIndex in range(0, len(contours)):
            area = cv2.contourArea(contours[contourIndex])
            if area > self.min_area:
                area_list.append(area)
        compare_area = sorted(area_list)[-3]  # 中位数
        area_list = []
        for contourIndex in range(0, len(contours)):
            area = cv2.contourArea(contours[contourIndex])
            if area > self.min_area:
                area_list.append(area)
                if area > max_area:
                    max_area = area
                    begin_index = len(result)
                rect = cv2.boundingRect(contours[contourIndex])
                if area - compare_area > 900:  # 通过面积比较判断宝箱
                    print(sorted(area_list))
                    print("compare: %d" % (compare_area,))
                    raise Exception("此关有色块区域不正常，可能是宝箱关卡")
                result.append(Block(rect[0], rect[1], rect[2], rect[3]))
        result[begin_index].mark_begin()
        print("寻找起点耗时 %d ms" % (time.time()*1000 - current))
        table = Table(result, self.image)
        return table


if __name__ == '__main__':
    import json

    f = open('config.json', 'r', encoding='utf-8')
    text = f.read()
    f.close()
    params = json.loads(text)

    image_path = "01.png"
    reco = Recognizer(image_path, True)
    reco.binarize()

    reco.clear_noise()



    cv2.namedWindow("b", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("b", int(reco.operation_image.shape[0] * 0.8), int(reco.operation_image.shape[1] * 0.8))

    contours, hierarchy = cv2.findContours(reco.operation_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 找出轮廓
    for contourIndex in range(1, len(contours)):
        area = cv2.contourArea(contours[contourIndex])
        if area > reco.min_area:
            rect = cv2.boundingRect(contours[contourIndex])
            cv2.putText(reco.operation_image, str(area), (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (111,110, 110), 2)
    cv2.imshow("b", reco.operation_image)
    cv2.waitKey(0)
    table = reco.find()
    table.find_path()







