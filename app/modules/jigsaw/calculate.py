blocks = [
    [[[1, 1], [1, 1]]],
    [[[2, 2, 2, 2]], [[2], [2], [2], [2]]],
    [[[3, 3, 0], [0, 3, 3]], [[0, 3], [3, 3], [3, 0]]],
    [[[0, 4, 4], [4, 4, 0]], [[4, 0], [4, 4], [0, 4]]],
    [
        [[5, 0, 0], [5, 5, 5]],
        [[5, 5], [5, 0], [5, 0]],
        [[5, 5, 5], [0, 0, 5]],
        [[0, 5], [0, 5], [5, 5]],
    ],
    [
        [[0, 0, 6], [6, 6, 6]],
        [[6, 6], [0, 6], [0, 6]],
        [[6, 6, 6], [6, 0, 0]],
        [[6, 0], [6, 0], [6, 6]],
    ],
    [
        [[0, 7, 0], [7, 7, 7]],
        [[7, 7, 7], [0, 7, 0]],
        [[7, 0], [7, 7], [7, 0]],
        [[0, 7], [7, 7], [0, 7]],
    ],
    [[[0, 8, 0], [8, 8, 8], [0, 8, 0]]],
    [[[9]]],
    [[[10, 10]], [[10], [10]]],
    [
        [[11, 11], [11, 0]],
        [[11, 11], [0, 11]],
        [[0, 11], [11, 11]],
        [[11, 0], [11, 11]],
    ],
]

res = []
m = n = a = l = None


def solve(arr, num):
    global m, n, a, l, res
    res = []
    m = len(arr)
    n = len(arr[0])

    a = [[arr[i][j] for j in range(n)] for i in range(m)]
    l = num[:]

    dfs(0)

    # 按照不同元素数量排序，若相同则按最大元素值排序
    res.sort(
        key=lambda A: (
            -len(set(sum(A, []))),
            -max(l[x - 1] for x in sum(A, []) if x > 0),
        )
    )

    return res


def can_place_block(x, y, b, d):
    pat = blocks[b][d]
    offset = 0
    while pat[0][offset] == 0:
        offset += 1
    y -= offset
    if y < 0:
        return False
    for i in range(len(pat)):
        for j in range(len(pat[0])):
            if pat[i][j] and (x + i >= m or y + j >= n or a[x + i][y + j] != -1):
                return False
    return True


def place_block(x, y, b, d, v):
    pat = blocks[b][d]
    offset = 0
    while pat[0][offset] == 0:
        offset += 1
    y -= offset
    for i in range(len(pat)):
        for j in range(len(pat[0])):
            if pat[i][j]:
                a[x + i][y + j] = v


def dfs(p):
    if p == m * n:
        x = [[a[i][j] for j in range(n)] for i in range(m)]
        res.append(x)
        if len(res) >= 10000:
            print("方案数太多，仅计算前一万种。减少一些方块吧~")
            return True
        return False

    x, y = divmod(p, n)

    if a[x][y] != -1:
        return dfs(p + 1)

    for b in range(len(blocks)):
        if not l[b]:
            continue
        for d in range(len(blocks[b])):
            if not can_place_block(x, y, b, d):
                continue
            place_block(x, y, b, d, b + 1)
            l[b] -= 1
            if dfs(p + 1):
                return True
            l[b] += 1
            place_block(x, y, b, d, -1)

    return False
