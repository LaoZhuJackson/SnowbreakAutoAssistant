import copy

from app.common.logger import logger
from app.modules.automation import auto

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
            [2, 2, 2, 2]
        ],
        [
            [2],
            [2],
            [2],
            [2]
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
        [
            [0, 5],
            [0, 5],
            [5, 5]
        ]
    ],
    [
        [
            [0, 0, 6],
            [6, 6, 6]
        ],
        [
            [6, 6],
            [0, 6],
            [0, 6]
        ],
        [
            [6, 6, 6],
            [6, 0, 0]
        ],
        [
            [6, 0],
            [6, 0],
            [6, 6]
        ]
    ],
    [
        [
            [0, 7, 0],
            [7, 7, 7]
        ],
        [
            [7, 7, 7],
            [0, 7, 0]
        ],
        [
            [7, 0],
            [7, 7],
            [7, 0]
        ],
        [
            [0, 7],
            [7, 7],
            [0, 7]
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
            [10, 10]
        ],
        [
            [10],
            [10]
        ]
    ],
    [
        [
            [11, 11],
            [11, 0],
        ],
        [
            [11, 11],
            [0, 11],
        ],
        [
            [0, 11],
            [11, 11],
        ],
        [
            [11, 0],
            [11, 11],
        ],
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
            "1": 3,
            "2": 13,
            "3": 10,
            "4": 13,
            "5": 9,
            "6": 33,
            "7": 8,
            "8": 1,
            "9": 1,
            "10": 0,
            "11": 1,
        }
        self.piece_solution = []  # 存储已成功填满的方案
        self.used_pieces = []  # 存储单次方案中已放置的块编号，以及它的旋转状态，放置位置
        self.piece_priority = []

    def run(self):
        self.identify_board()
        if self.board:
            self.update_priority()
            self.fill_board(10)
            # print("填充后的 board:")
            # for row in self.board:
            #     print(row)
            if self.piece_solution:
                # print("最后的solution")
                # print(self.piece_solution)
                for index, solution in enumerate(self.piece_solution):
                    # print(f"-------方案{index + 1}-------")
                    for piece in solution:
                        pass
                        # print(f"Piece {piece[0]} 经过 {piece[1]} 次旋转后放置在行 {piece[2]}, 列 {piece[3]}")
        else:
            logger.error("未识别出对应的地图")

    def identify_board(self):
        """判断当前board是哪个"""
        for i in range(1, 4):
            if auto.find_element(f"app/resource/images/jigsaw/{i}.png", "image", threshold=0.7,
                                 crop=(596 / 1920, 203 / 1080, 901 / 1920, 718 / 1080)):
                self.board = boards[str(i)]
                # 获取board的长宽信息
                self.board_rows = len(self.board)
                self.board_cols = len(self.board[0])

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
        def dfs(now):
            """
            深度优先搜索寻找所有方案，有方案上限控制
            :param now: 当前正在处理board上的哪个位置的指针
            :return:
            """
            # 当指针指到了最后一个格子
            if now == self.board_rows * self.board_cols:
                # 只添加全填满的方案
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
                    self.piece_counts[piece_id] -= 1
                    if dfs(now + 1):
                        return True
                    # 如果下一个dfs返回False，则回退一格
                    self.piece_counts[piece_id] += 1
                    self.place_piece(x, y, int(piece_id) - 1, rotation, False)
            # 如果所有方块都试过了还是到了这里，则返回False再回退一格
            return False

        dfs(0)

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


l = [[['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['6', 0, 2, 2], ['5', 3, 2, 4], ['5', 0, 3, 1]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['6', 1, 2, 4], ['6', 2, 3, 1], ['6', 0, 3, 2]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['6', 1, 2, 4], ['2', 0, 3, 1], ['2', 0, 4, 1]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['6', 1, 2, 4], ['5', 0, 3, 1], ['5', 2, 3, 2]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['6', 1, 2, 4], ['1', 0, 3, 1], ['1', 0, 3, 3]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['4', 0, 2, 3], ['1', 0, 3, 1], ['6', 0, 3, 3]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['3', 1, 2, 3], ['5', 3, 2, 4], ['1', 0, 3, 1]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['1', 0, 2, 4], ['6', 2, 3, 1], ['2', 0, 4, 2]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 0, 1, 0], ['1', 0, 2, 4], ['1', 0, 3, 1], ['5', 0, 3, 3]],
     [['6', 2, 0, 0], ['8', 0, 0, 2], ['9', 0, 0, 4], ['7', 3, 1, 0], ['5', 0, 2, 2], ['6', 1, 2, 4], ['2', 0, 4, 1]]]
