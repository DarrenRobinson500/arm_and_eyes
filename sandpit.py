from sql import *
from datetime import datetime, timedelta
now = datetime.now
from item import *


# id, i1, x1, y1, i2, x2, y2
boxes_0 = [[1, 1, 287, 207, 2, 210, 345]]
boxes_1 = [[1, 1, 287, 207, 2, 211, 345], [2, 3, 316, 151, 4, 351, 316]]

nums = [1, 1, 2, 2, 3]

my_set = {n for n in nums}
print(my_set)