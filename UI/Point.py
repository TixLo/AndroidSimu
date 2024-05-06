class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # 加法運算
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    # 減法運算
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    # 定義打印函數
    def __str__(self):
        return f"({self.x}, {self.y})"
