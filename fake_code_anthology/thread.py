#并行执行一个函数fn, 并保存返回值

import threading
rsDict = dict()

def fn(arg):
	rsDict[arg] = arg * 2

L = [1, 3, 4, 7, 9]
threadList = list()

for i in L:
	t = threading.Thread(target=fn, args = (i,))
	threadList.append(t)

for t in threadList:
	t.start()

for t in threadList:
	t.join()

print(rsDict)

