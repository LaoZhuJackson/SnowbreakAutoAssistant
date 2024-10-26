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

pieces = {
    "1": [[1, 1],
          [1, 1]],
    "2": [[1],
          [1],
          [1],
          [1]],
    "3": [[1, 1, 0],
          [0, 1, 1]],
    "4": [[0, 1, 1],
          [1, 1, 0]],
    "5": [[0, 1],
          [0, 1],
          [0, 1],
          [1, 1]],
    "6": [[1, 0],
          [1, 0],
          [1, 0],
          [1, 1]],
    "7": [[1, 1, 1],
          [0, 1, 0]],
    "8": [[0, 1, 0],
          [1, 1, 1],
          [0, 1, 0]],
    "9": [[1]],
    "10": [[1],
           [1]],
    "11": [[1, 0],
           [1, 1]]
}


class JigsawModule:
    def __init__(self):
        # 当前拼图板
        self.board = None
        self.piece_counts = {
            "1": 3,
            "2": 15,
            "3": 10,
            "4": 11,
            "5": 8,
            "6": 30,
            "7": 9,
            "8": 1,
            "9": 9,
            "10": 0,
            "11": 1,
        }
        self.piece_solution = []  # 存储已放置的 piece
        self.piece_priority = []

    def run(self):
        self.identify_board()
        if self.board:
            self.update_priority()
            self.fill_board()
            print("填充后的 board:")
            for row in self.board:
                print(row)
            if self.piece_solution:
                print("放置的 pieces:")
                for piece in self.piece_solution:
                    print(f"Piece {piece[0]} 经过 {piece[1]} 次旋转后放置在行 {piece[2]}, 列 {piece[3]}")
        else:
            logger.error("未识别出对应的地图")

    def identify_board(self):
        """判断当前board是哪个"""
        for i in range(1, 4):
            if auto.find_element(f"app/resource/images/jigsaw/{i}.png", "image", threshold=0.7,
                                 crop=(596 / 1920, 203 / 1080, 901 / 1920, 718 / 1080)):
                self.board = boards[str(i)]

    def rotate_piece(self, piece):
        """逆时针旋转拼图块90度"""
        # 对整个list进行反转，然后*解包成matrix[0], matrix[1], matrix[2]，最后zip按列组合，类型转换为list后完成转置
        return [list(row) for row in zip(*piece[::-1])]

    def can_place_piece(self, piece, row, col):
        """检查是否可以在 board 的指定位置放置 piece"""
        rows, cols = len(piece), len(piece[0])

        # 如果 piece 超出了 board 的边界
        if row + rows > len(self.board) or col + cols > len(self.board[0]):
            return False

        # 检查该区域是否为空
        for r in range(rows):
            for c in range(cols):
                if piece[r][c] == 1 and self.board[row + r][col + c] != 0:
                    return False
        return True

    def place_piece(self, piece, row, col, mark):
        """放置或移除方块。mark为True表示放置，False表示移除。"""
        for i in range(len(piece)):
            for j in range(len(piece[0])):
                if piece[i][j] == 1:
                    self.board[row + i][col + j] = 1 if mark else 0

    def fill_board(self):
        """尝试填充整个board并返回所有解决方案。"""

        def backtrack(used_pieces):
            # 找到下一个空白位置
            for row in range(len(self.board)):
                for col in range(len(self.board[0])):
                    if self.board[row][col] == 0:  # 为空位置
                        for piece_id in self.piece_priority:
                            # 取出拼图
                            piece = pieces[piece_id]
                            for rotations in range(4):
                                # print(self.can_place_piece(piece, row, col),self.piece_counts[piece_id])
                                if self.can_place_piece(piece, row, col) and self.piece_counts[piece_id] > 0:
                                    self.place_piece(piece, row, col, True)
                                    self.piece_counts[piece_id] -= 1  # 减少方块数量
                                    # 更新所使用的方案
                                    used_pieces.append((piece_id, rotations, row, col))
                                    # 递归调用
                                    backtrack(used_pieces)
                                    # 撤回放置
                                    self.place_piece(piece, row, col, False)
                                    self.piece_counts[piece_id] += 1  # 恢复方块数量
                                    # 移除记录的方块及旋转次数
                                    used_pieces.pop()
                                # 旋转方块
                                piece = self.rotate_piece(piece)
                        # 回溯后退出
                        return
            # 遍历完成，表示已填满
            self.piece_solution.append(used_pieces.copy())

        backtrack([])

    def update_priority(self):
        # 如果8号方块的数量大于0，则将其添加到优先级列表中
        if self.piece_counts["8"] > 0:
            self.piece_priority.append("8")

        # 然后按数量和其他优先级添加剩余的方块
        self.piece_priority.extend(sorted(
            [k for k in pieces.keys() if k != "8"],  # 排除8号
            key=lambda k: (self.piece_counts[k], int(k) not in [11, 10]),  # 11号和10号的优先级低于其他
            reverse=True
        ))
