import threading
from queue import Queue

#首先往queue里扔入原始数据
#触发事件，让worker开始动起来
#每个worker取到一个数据时就开始工作，直到产出结果数据


Q = Queue()
rsDict = dict()
OriginalList = [1,3,4,5,7]

condition = threading.Condition()

def worker():
    originalData = Q.get()
    print(originalData)

def main():
    with condition:
        for i in OriginalList:
            Q.put(i)
        condition.notifyAll()

if __name__ == '__main__':
    main()
