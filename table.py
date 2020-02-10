import copy
import math
import time

import cv2
from functools import cmp_to_key



class Block:
    center = (0, 0)  # 中心点
    width = 0
    height = 0
    x = 0  # 左上角x
    y = 0
    origin = False

    @staticmethod
    def compare(block1, block2):
        unit_length = block1.height + 15
        if round(block1.y / unit_length) > round(block2.y / unit_length):
            return 1
        if round(block1.y / unit_length) == round(block2.y / unit_length):
            return block1.x - block2.x
        if round(block1.y / unit_length) < round(block2.y / unit_length):
            return -1

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.center = (int(x + w / 2), int(y + h / 2))

    def mark_begin(self):  # 标记为起点
        self.origin = True

    def __str__(self):
        return "x:%d y:%d" % (self.center[0], self.center[1])


class Table:
    image = None  # 原始图像
    blocks = []  # 所有方块
    block_map = {}  # hanshmap k为block v为在blocks中的下标
    block_width = -1
    interval = 15  # 方块的间距
    block_table = []  # 表格形式存储
    begin_index = 0
    matrix = []  # 邻接矩阵

    south_index = 0  # 最北的方块下标
    north_index = 0
    east_index = 0
    west_index = 0

    def __init__(self, blocks, image):
        self.blocks = sorted(blocks, key=cmp_to_key(Block.compare))
        for itemIndex in range(0, len(blocks)):
            self.block_map[self.blocks[itemIndex]] = itemIndex
        self.image = image
        self.__get_average_block_width()

    def __get_average_block_width(self):  # 获取方块尺寸的平均值
        if self.block_width > 0:
            return self.block_width
        else:
            total = 0
            for item in self.blocks:
                if item.origin == False:
                    total += item.width
            self.block_width = math.ceil(total / (len(self.blocks) - 1))
        return self.block_width

    def __get_size(self):  # 计算求解区域是几行几列
        self.south_index = 0
        self.north_index = 0
        self.east_index = 0
        self.west_index = 0
        for itemIndex in range(0, len(self.blocks)):
            if self.blocks[itemIndex].center[0] < self.blocks[self.west_index].center[0]:
                self.west_index = itemIndex
            if self.blocks[itemIndex].center[1] < self.blocks[self.north_index].center[1]:
                self.north_index = itemIndex
            if self.blocks[itemIndex].center[0] > self.blocks[self.east_index].center[0]:
                self.east_index = itemIndex
            if self.blocks[itemIndex].center[1] > self.blocks[self.south_index].center[1]:
                self.south_index = itemIndex

        row_num = int((self.blocks[self.south_index].center[1] - self.blocks[self.north_index].center[1]) / (
                self.block_width + self.interval) + 2)
        col_num = int((self.blocks[self.east_index].center[0] - self.blocks[self.west_index].center[0]) / (
                self.block_width + self.interval) + 2)
        # print("%d行 %d列" % (row_num, col_num))
        return row_num, col_num

    def generate_process_data(self):
        """
        根据行列尺寸生成二维数组形式的数据结构
        :return:
        """
        cv2.imwrite("operation.png", self.image)
        row_num, col_num = self.__get_size()
        self.block_table = [[None] * col_num for i in range(0, row_num)]
        for itemIndex in range(0, len(self.blocks)):
            cv2.circle(self.image, self.blocks[itemIndex].center, 3, (0, 0, 255))
            cv2.imwrite("operation.png", self.image)
            row = round((self.blocks[itemIndex].center[1] - self.blocks[self.north_index].center[1]) / (
                    self.block_width + self.interval))
            col = round((self.blocks[itemIndex].center[0] - self.blocks[self.west_index].center[0]) / (
                    self.block_width + self.interval))
            self.block_table[row][col] = self.blocks[itemIndex]
            if self.blocks[itemIndex].origin:
                self.begin_index = itemIndex
        return self.block_table

    def generate_adjacency_matrix(self):
        """
        生成邻接矩阵
        :param table: 二维数组表示的节点分布
        :param node_num: 节点数
        :return:
        """
        table = self.block_table
        node_num = len(self.blocks)
        matrix = [[None] * node_num for i in range(0, node_num)]
        for rowIndex in range(0, len(table)):
            for colIndex in range(0, len(table[rowIndex])):
                if table[rowIndex][colIndex] is not None :
                    if rowIndex != 0:  # 上节点存在
                        if table[rowIndex - 1][colIndex] is not None:
                            matrix[self.block_map[table[rowIndex][colIndex]]][
                                self.block_map[table[rowIndex - 1][colIndex]]] = table[rowIndex - 1][colIndex]
                    if rowIndex != len(table) - 1:  # 下节点存在
                        if table[rowIndex + 1][colIndex] is not None:
                            matrix[self.block_map[table[rowIndex][colIndex]]][
                                self.block_map[table[rowIndex + 1][colIndex]]] = table[rowIndex + 1][colIndex]
                    if colIndex != 0:  # 左节点存在
                        if table[rowIndex][colIndex - 1] is not None:
                            matrix[self.block_map[table[rowIndex][colIndex]]][
                                self.block_map[table[rowIndex][colIndex - 1]]] = table[rowIndex][colIndex - 1]
                    if colIndex != len(table[0]) - 1:
                        if table[rowIndex][colIndex + 1] is not None:
                            matrix[self.block_map[table[rowIndex][colIndex]]][
                                self.block_map[table[rowIndex][colIndex + 1]]] = table[rowIndex][colIndex + 1]
        self.matrix = matrix
        return matrix

    def find_path(self, optimize=True):
        """
        dfs+回溯 递归求解
        :param optimize: 是否对最终结果进行优化，优化可有效减少滑动次数，但模拟滑动操作可能会不稳定
        :return:
        """
        current = time.time() * 1000
        self.generate_process_data()
        self.generate_adjacency_matrix()
        visited = []
        visited.append( self.blocks[self.begin_index])
        self.find_path_fun(visited, self.blocks[self.begin_index])
        for index in range(0, len(visited)-1):
            cv2.line(self.image, visited[index].center, visited[index+1].center, (0, 255, 0), 2)
            cv2.putText(self.image, str(index), visited[index].center, cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            cv2.imwrite("operation.png", self.image)
        path = []
        for item in visited:
            path.append((item.center[0], item.center[1]))
        print("求解耗时 %d ms" % (time.time()*1000 - current,))
        return path if not optimize else self.optimize_path(path)

    def find_path_fun(self, visited, start):
        for item in self.matrix[self.block_map[start]]:
            if item is not None and item not in visited:
                visited.append(item)
                if len(visited) == len(self.blocks):
                    return True
                if self.find_path_fun(visited, item):
                    return True
                else:
                    visited.pop()
        return False

    def optimize_path(self, paths):
        newPath = []
        for item in paths:
            if len(newPath) <= 2:
                newPath.append(item)
            elif abs(item[0]-newPath[-1][0]) < 10 and abs(newPath[-1][0] - newPath[-2][0]) < 10:
                newPath.pop()
                newPath.append(item)
            elif abs(item[1]-newPath[-1][1]) < 10 and abs(newPath[-1][1] - newPath[-2][1]) < 10:
                newPath.pop()
                newPath.append(item)
            else:
                newPath.append(item)
        return newPath

    @staticmethod
    def block_in(b, _list):
        if isinstance(b, Block):
            for item in _list:
                if b.x == item.x and b.y == item.y:
                    return True
        return False


