import copy
import time

import numpy as np
import pyautogui
import pydirectinput
from qfluentwidgets import InfoBar

from app.common.config import config
from app.common.logger import logger
from app.common.ppOCR import ocr
from app.common.signal_bus import signalBus
from app.modules.automation import auto
from app.modules.automation.screenshot import Screenshot

boards = {
    "1": [[0, 0, 0, 0, 0, -1],
          [0, 0, 0, 0, 0, -1],
          [0, 0, 0, 0, 0, 0],
          [-1, 0, 0, 0, 0, 0],
          [-1, 0, 0, 0, 0, 0]],
    "2": [[-1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, -1],
          [0, 0, 0, 0, 0, 0],
          [-1, 0, 0, 0, 0, 0]],
    "3": [[0, 0, 0, 0, 0, -1],
          [0, 0, 0, 0, -1, 0],
          [0, 0, 0, -1, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
    "4": [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
    "5": [[0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, -1]],
    "6": [[0, 0, 0, 0, 0, 0],
          [0, 0, -1, -1, 0, 0],
          [0, 0, -1, -1, 0, 0],
          [0, 0, -1, -1, 0, 0],
          [0, 0, 0, 0, 0, 0]],
    "7": [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [-1, -1, -1, -1, -1, -1],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]],
    "8": [[0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, -1, -1, 0, 0]],
    "9": [[-1, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, -1]],
    "10": [[0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, -1, 0],
           [0, 0, 0, 0, 0, 0],
           [0, -1, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0]],
    "11": [[-1, 0, 0, 0, 0, 0],
           [-1, 0, 0, 0, 0, 0],
           [-1, 0, 0, 0, 0, 0],
           [-1, 0, 0, 0, 0, 0],
           [-1, 0, 0, 0, 0, 0]],
    "12": [[-1, -1, 0, 0, 0, 0],
           [-1, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, -1],
           [0, 0, 0, 0, -1, -1]],
    "13": [[-1, 0, 0, 0, 0, 0],
           [0, -1, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, -1, 0],
           [0, 0, 0, 0, 0, -1]],
    "14": [[0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, -1],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, -1],
           [0, 0, 0, 0, 0, 0]],
    "15": [[0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, -1, -1, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0]],
    "16": [[0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0]],
}
# 每个拼图块及其旋转变体
pieces = [
    [
        [
            [1, 1],
            [1, 1]
        ]
    ],
    [
        [
            [2],
            [2],
            [2],
            [2]
        ],
        [
            [2, 2, 2, 2]
        ]
    ],
    [
        [
            [3, 3, 0],
            [0, 3, 3]
        ],
        [
            [0, 3],
            [3, 3],
            [3, 0]
        ]
    ],
    [
        [
            [0, 4, 4],
            [4, 4, 0]
        ],
        [
            [4, 0],
            [4, 4],
            [0, 4]
        ]
    ],
    [
        [
            [0, 5],
            [0, 5],
            [5, 5]
        ],
        [
            [5, 0, 0],
            [5, 5, 5]
        ],
        [
            [5, 5],
            [5, 0],
            [5, 0]
        ],
        [
            [5, 5, 5],
            [0, 0, 5]
        ],
    ],
    [
        [
            [6, 0],
            [6, 0],
            [6, 6]
        ],
        [
            [6, 6, 6],
            [6, 0, 0]
        ],
        [
            [6, 6],
            [0, 6],
            [0, 6]
        ],
        [
            [0, 0, 6],
            [6, 6, 6]
        ]
    ],
    [
        [
            [7, 7, 7],
            [0, 7, 0]
        ],
        [
            [0, 7],
            [7, 7],
            [0, 7]
        ],
        [
            [0, 7, 0],
            [7, 7, 7]
        ],
        [
            [7, 0],
            [7, 7],
            [7, 0]
        ]
    ],
    [
        [
            [0, 8, 0],
            [8, 8, 8],
            [0, 8, 0]
        ]
    ],
    [
        [
            [9]
        ]
    ],
    [
        [
            [10],
            [10]
        ],
        [
            [10, 10]
        ]
    ],
    [
        [
            [11, 0],
            [11, 11]
        ],
        [
            [11, 11],
            [11, 0]
        ],
        [
            [11, 11],
            [0, 11]
        ],
        [
            [0, 11],
            [11, 11]
        ]
    ]
]


class JigsawModule:
    def __init__(self):
        self.board_cols = None
        self.board_rows = None
        self.eight_piece_placed = None
        self.board = []
        self.display_solution_board = []
        self.piece_counts = {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0,
            "6": 0,
            "7": 0,
            "8": 0,
            "9": 0,
            "10": 0,
            "11": 0,
        }
        self.piece_solution = []  # 存储已成功填满的方案
        self.used_pieces = []  # 存储单次方案中已放置的块编号，以及它的旋转状态，放置位置
        self.piece_priority = []
        self.solutions_score = [0] * config.SpinBox_max_solutions.value  # 存储每个方案的得分
        self.board_top_left = []  # 拼图板左上角坐标
        self.board_bottom_right = []  # 拼图板右下角坐标

    def run(self):
        for i in range(3):
            self.identify_board()
            if self.board:
                self.update_pieces_num()
                self.update_priority()
                self.fill_board(config.SpinBox_max_solutions.value)
                if self.piece_solution:
                    best_solution = self.give_score_and_display_best()
                    if len(self.piece_solution) < config.SpinBox_max_solutions.value:
                        logger.warn(
                            f'目前总共只有{len(self.piece_solution)}种能填满全部格子的方案，不足{config.SpinBox_max_solutions.value}')
                    if self.place_jigsaw(best_solution):
                        if self.after_place():
                            if auto.click_element("继续", "text", include=True, max_retries=3, action="move_click"):
                                continue
                            else:
                                auto.click_element("退出", "text", include=True, max_retries=3, action="move_click")
                                break
                        else:
                            break
                    else:
                        logger.error("未能正确拼完，可以按照给出的最优方案手动拼完")
                        break
                else:
                    logger.warn("没有找到能填满全部格子的方案")
            else:
                logger.error("未识别出对应的地图")
                break

    def identify_board(self):
        """判断当前board是哪个"""
        for i in range(1, 17):
            try:
                result = auto.find_element(f"app/resource/images/jigsaw/{i}.png", "image", threshold=0.7,
                                           crop=(596 / 1920, 203 / 1080, 901 / 1920, 718 / 1080))
                if result:
                    # 更新左上角坐标
                    self.board_top_left, self.board_bottom_right = result
                    # 需要deepcopy,不然下次不更新
                    self.board = copy.deepcopy(boards[str(i)])
                    # 获取board的长宽信息
                    self.board_rows = len(self.board)
                    self.board_cols = len(self.board[0])
                    break
            except Exception as e:
                pass

    def place_piece(self, x, y, piece_id: int, rotation: int, mark: bool):
        """
        在 board 的指定位置放置 piece
        :param x:
        :param y:
        :param piece_id:
        :param rotation:
        :param mark: 判断是放入还是取出
        :return:
        """
        # 取出对应拼图块
        piece = pieces[piece_id][rotation]
        offset = next((index for index, value in enumerate(piece[0]) if value), None)
        y -= offset
        # 更新单次方案
        if mark:
            self.used_pieces.append([str(piece_id + 1), rotation, x, y])
            # print("加入")
            # print(self.used_pieces)
        else:
            # 如果存在放置步骤则弹出最后一个
            if self.used_pieces:
                self.used_pieces.pop()
                # print("弹出")
                # print(self.used_pieces)
        for i in range(len(piece)):
            for j in range(len(piece[0])):
                if piece[i][j]:
                    self.board[x + i][y + j] = piece[i][j] if mark else 0

    def can_place_piece(self, x, y, piece_id: int, rotation):
        """
        判断能否在x,y处放下对应piece，考虑了旋转和空值偏移
        :param x: now_x
        :param y: now_y
        :param piece_id:
        :param rotation:
        :return:
        """
        # 取出对应拼图块
        piece = pieces[piece_id][rotation]
        # 找出拼图块第一行中第一个非0元素并标记为横向偏移量,next 函数会从生成器表达式中取出第一个符合条件的索引 i，也就是第一个非零元素的列位置
        offset = next((index for index, value in enumerate(piece[0]) if value), None)
        # 说明当前第一行全是0，无非0元素
        if offset is None:
            return False
        # 使放置piece时整体向左偏移offset个单位
        y -= offset
        # 如果向左偏移后now位置越出左边界
        if y < 0:
            return False
        # 判断piece中的每个块能否放入对应位置
        for i in range(len(piece)):
            for j in range(len(piece[0])):
                if piece[i][j] and (
                        x + i >= self.board_rows or y + j >= self.board_cols or self.board[x + i][y + j] != 0):
                    return False
        return True

    def fill_board(self, max_solutions):
        if self.piece_counts["8"] > 0:
            need_place_8 = True
        else:
            need_place_8 = False
        place_8_count = 0

        def dfs(now):
            """
            深度优先搜索寻找所有方案，有方案上限控制
            :param now: 当前正在处理board上的哪个位置的指针
            :return:
            """
            nonlocal need_place_8
            nonlocal place_8_count
            # 当指针指到了最后一个格子
            if now == self.board_rows * self.board_cols:
                # 只添加全填满的方案
                if need_place_8:
                    if not any(0 in r for r in self.board) and place_8_count > 0:
                        # 需要用.copy()浅拷贝创建一个新列表对象，不然更新不成功，会一直append最开始的第一个
                        self.piece_solution.append(self.used_pieces.copy())
                        self.display_solution_board.append(copy.deepcopy(self.board))
                        logger.info(f"成功找到第{len(self.piece_solution)}个方案")
                        # print(self.display_solution_board)
                else:
                    if not any(0 in r for r in self.board):
                        # 需要用.copy()浅拷贝创建一个新列表对象，不然更新不成功，会一直append最开始的第一个
                        self.piece_solution.append(self.used_pieces.copy())
                        self.display_solution_board.append(copy.deepcopy(self.board))
                        logger.info(f"成功找到第{len(self.piece_solution)}个方案")
                        # print(self.display_solution_board)
                if len(self.piece_solution) >= max_solutions:
                    return True  # 已达到指定方案数量，停止搜索
                # 没找够，返回False继续找
                return False
            # 通过now直接得到当前所在的行和列，避免两层循环，例如divmod(11,3)会返回（3,2），其中3是商，2是余数，并且允许从0下标开始
            x, y = divmod(now, self.board_cols)
            # 判断是否是可放置区域，-1和其他数字都表示不可放置，如果可放置则往if之后走
            if self.board[x][y] != 0:
                # 开始递归下一个位置
                if dfs(now + 1):
                    return True
                return False
            # 取出的piece_id是int类型
            for piece_id in self.piece_priority:
                # 如果数量等于0则跳过这次循环
                if not self.piece_counts[piece_id]:
                    continue
                for rotation in range(len(pieces[int(piece_id) - 1])):
                    # 如果当前形状放不下则尝试旋转
                    if not self.can_place_piece(x, y, int(piece_id) - 1, rotation):
                        continue
                    self.place_piece(x, y, int(piece_id) - 1, rotation, True)
                    if piece_id == "8":
                        place_8_count += 1
                    self.piece_counts[piece_id] -= 1
                    if dfs(now + 1):
                        return True
                    # 如果下一个dfs返回False，则回退一格
                    self.piece_counts[piece_id] += 1
                    if piece_id == "8":
                        place_8_count -= 1
                    self.place_piece(x, y, int(piece_id) - 1, rotation, False)
            # 如果所有方块都试过了还是到了这里，则返回False再回退一格
            return False

        dfs(0)

    def update_pieces_num(self):
        config_data = config.toDict()
        piece_counts = config_data["pieces_num"]
        for key, value in piece_counts.items():
            piece_id = key.split("_")[-1]
            self.piece_counts[piece_id] = int(value)
        # print(f"{self.piece_counts=}")

    def update_priority(self):
        # 如果8号方块的数量大于0，则将其添加到优先级列表中
        if self.piece_counts["8"] > 0:
            self.piece_priority.append("8")

        # 然后按数量和其他优先级添加剩余的方块
        self.piece_priority.extend(sorted(
            [k for k in self.piece_counts.keys() if k != "8"],  # 排除8号
            key=lambda k: (self.piece_counts[k], int(k) not in [11, 10]),  # 11号和10号的优先级低于其他
            reverse=True
        ))

    def give_score_and_display_best(self):
        """
        给每个方案打分，并将最优方案传给界面
        :return: 得分最大的方案
        """
        result_score = 0
        score_list = self.piece_priority[::-1]
        score_dic = {value: index for index, value in enumerate(score_list)}
        score_dic["8"] = 30
        # print(f"{score_dic=}")
        for index, solution in enumerate(self.piece_solution):
            for piece in solution:
                # print(f"Piece {piece[0]} 经过 {piece[1]} 次旋转后放置在行 {piece[2]}, 列 {piece[3]}")
                result_score += score_dic[piece[0]]
            self.solutions_score[index] = result_score
            result_score = 0
            print(f"-------方案{index + 1}，得分：{self.solutions_score[index]}-------")
            for r in self.display_solution_board[index]:
                print(r)
        best_score_index = self.solutions_score.index(max(self.solutions_score))
        print(f"最优方案为：方案{best_score_index + 1}")
        signalBus.jigsawDisplaySignal.emit(self.display_solution_board[best_score_index])
        return self.piece_solution[best_score_index]

    def place_jigsaw(self, best_solution):
        path_dict = {
            "1": ["app/resource/images/jigsaw/piece_1_0.png"],
            "2": ["app/resource/images/jigsaw/piece_2_0.png", "app/resource/images/jigsaw/piece_2_1.png",
                  "app/resource/images/jigsaw/piece_2_2.png", "app/resource/images/jigsaw/piece_2_3.png"],
            "3": ["app/resource/images/jigsaw/piece_3_0.png", "app/resource/images/jigsaw/piece_3_1.png",
                  "app/resource/images/jigsaw/piece_3_2.png", "app/resource/images/jigsaw/piece_3_3.png"],
            "4": ["app/resource/images/jigsaw/piece_4_0.png", "app/resource/images/jigsaw/piece_4_1.png",
                  "app/resource/images/jigsaw/piece_4_2.png", "app/resource/images/jigsaw/piece_4_3.png"],
            "5": ["app/resource/images/jigsaw/piece_5_0.png", "app/resource/images/jigsaw/piece_5_1.png",
                  "app/resource/images/jigsaw/piece_5_2.png", "app/resource/images/jigsaw/piece_5_3.png"],
            "6": ["app/resource/images/jigsaw/piece_6_0.png", "app/resource/images/jigsaw/piece_6_1.png",
                  "app/resource/images/jigsaw/piece_6_2.png", "app/resource/images/jigsaw/piece_6_3.png"],
            "7": ["app/resource/images/jigsaw/piece_7_0.png", "app/resource/images/jigsaw/piece_7_1.png",
                  "app/resource/images/jigsaw/piece_7_2.png", "app/resource/images/jigsaw/piece_7_3.png"],
            "8": ["app/resource/images/jigsaw/piece_8_0.png"],
            "9": ["app/resource/images/jigsaw/piece_9_0.png"],
            "10": ["app/resource/images/jigsaw/piece_10_0.png", "app/resource/images/jigsaw/piece_10_1.png"],
            "11": ["app/resource/images/jigsaw/piece_11_0.png", "app/resource/images/jigsaw/piece_11_1.png",
                   "app/resource/images/jigsaw/piece_11_2.png", "app/resource/images/jigsaw/piece_11_3.png"],
        }

        def calculate_grid_centers(top_left, bottom_right, grid_size=128):
            x1, y1 = top_left
            x2, y2 = bottom_right
            # 计算网格的行数和列数
            num_rows = (y2 - y1) // grid_size
            num_cols = (x2 - x1) // grid_size

            # 创建二维列表存储每个网格的中心点
            grid_centers = []

            # 逐行逐列计算每个网格的中心点坐标
            for row in range(num_rows):
                row_centers = []
                for col in range(num_cols):
                    center_x = x1 + col * grid_size + grid_size // 2
                    center_y = y1 + row * grid_size + grid_size // 2
                    row_centers.append((center_x, center_y))
                grid_centers.append(row_centers)

            return grid_centers

        def find_and_click(p_id, state):
            """找到当前步骤需要拖拽的拼图块，并点击选中，为接下来旋转做准备"""
            for index, path in enumerate(path_dict[p_id]):
                if auto.click_element(path, "image", threshold=0.75,
                                      crop=(76 / 1920, 128 / 1080, 338 / 1920, 855 / 1080),
                                      action="move"):
                    now_rotation_state = index
                    # 计算需要点击的旋转次数,+len确保非负
                    if (p_id == "2" or p_id == "3" or p_id == "4") and now_rotation_state == 3:
                        times = (state - 1 + len(path_dict[p_id])) % len(path_dict[p_id])
                    elif (p_id == "2" or p_id == "3" or p_id == "4") and now_rotation_state == 4:
                        times = (state - 2 + len(path_dict[p_id])) % len(path_dict[p_id])
                    else:
                        times = (state - now_rotation_state + len(path_dict[p_id])) % len(path_dict[p_id])
                    return times, now_rotation_state
            return None, None

        def drag_piece(end_x, end_y, id, rotation_state):
            """根据id和移动状态给出对应的偏移后坐标后拖动"""
            grid_size = 128
            offset_dict = {
                "1": [[0.5, 0.5]],
                "2": [[0.25, 1.5], [1.5, 0]],
                "3": [[1.25, 0.5], [0.5, 1.25]],
                "4": [[1, 0.5], [0.5, 1.25]],
                "5": [[0.5, 1], [1.25, 0.5], [0.5, 1], [1.25, 0.5]],
                "6": [[0.5, 1], [1.5, 0.5], [0.5, 1], [1.5, 0.5]],
                "7": [[1, 0.5], [0.75, 1.75], [1, 0.5], [0.75, 0.25]],
                "8": [[1.25, 1]],
                "9": [[0.25, 0]],
                "10": [[0, 0.5], [0.5, 0]],
                "11": [[0.5, 0.5], [0.5, 0.5], [0.5, 0.5], [0.5, 0.5]]
            }
            # 加入偏移量
            end_x += offset_dict[id][rotation_state][0] * grid_size
            end_y += offset_dict[id][rotation_state][1] * grid_size
            now_point = pyautogui.position()
            time.sleep(0.5)
            pydirectinput.mouseDown()
            pyautogui.moveTo(now_point.x + 250, now_point.y, duration=2)
            pyautogui.moveTo(end_x - 50, end_y)
            pyautogui.moveRel(50, 0, duration=2)
            time.sleep(0.5)
            pydirectinput.mouseUp()

        # print("最优方案放置方法：")
        # for piece in best_solution:
        #     print(f"Piece {piece[0]} 经过 {piece[1]} 次旋转后放置在行 {piece[2]}, 列 {piece[3]}")
        grid_point = calculate_grid_centers(self.board_top_left, self.board_bottom_right)
        for piece in best_solution:
            piece_id = piece[0]
            # 滚动鼠标滚轮调整到对应位置
            auto.click_element("00", "text", include=True, crop=(148 / 1920, 70 / 1080, 69 / 1920, 37 / 1080),
                               offset=(65, 369), action="move")
            time.sleep(0.5)
            if piece_id == "11":
                auto.mouse_scroll(1, -500)
                # pyautogui.dragRel(0, -300, button="left", duration=1)
            else:
                # pyautogui.dragRel(0, 300, button="left", duration=1)
                auto.mouse_scroll(1, 500)
            need_rotation_state = piece[1]
            place_row = piece[2]
            place_col = piece[3]
            click_times, now_state = find_and_click(piece_id, need_rotation_state)
            print(f"piece{piece_id}旋转次数:{click_times},当前状态：{now_state}")
            # 旋转到对应状态
            if click_times is not None:
                threshold = 0.75
                # 旋转到需要的状态
                if click_times > 0:
                    for i in range(click_times):
                        # print(f"当前状态：{now_state}")
                        while not auto.find_element(
                                f"app/resource/images/jigsaw/piece_{piece_id}_{(now_state + 1) % len(path_dict[piece_id])}.png",
                                "image",
                                threshold=threshold, crop=(76 / 1920, 128 / 1080, 338 / 1920, 855 / 1080)):
                            auto.click_element(f"app/resource/images/jigsaw/piece_{piece_id}_{now_state}.png", "image",
                                               threshold=0.75, crop=(76 / 1920, 128 / 1080, 338 / 1920, 855 / 1080),
                                               action="move_click")
                        now_state = (now_state + 1) % len(path_dict[piece_id])
                        time.sleep(0.3)
                else:
                    pass
                # 拖到对应位置
                drag_piece(grid_point[place_row][place_col][0], grid_point[place_row][place_col][1], piece_id,
                           now_state)
            else:
                logger.error(f"未识别出旋转状态：piece_{piece_id}_{need_rotation_state},跳过该拼图块")
                continue

        if auto.find_element("00", "text", include=True, crop=(1652 / 1920, 160 / 1080, 144 / 1920, 79 / 1080),
                             max_retries=2):
            return True
        return False

    def after_place(self):
        if auto.click_element("完美研析", "text", include=True, max_retries=3,
                              crop=(1667 / 1920, 1008 / 1080, 150 / 1920, 43 / 1080), action="move_click"):
            auto.click_element("确定", "text", include=True, max_retries=3,
                               crop=(1355 / 1920, 732 / 1080, 198 / 1920, 70 / 1080), action="move_click")
            if auto.click_element("领取", "text", include=True, max_retries=3,
                                  crop=(894 / 1920, 940 / 1080, 149 / 1920, 56 / 1080), action="move_click"):
                auto.press_key("esc")
                return True
        return False
