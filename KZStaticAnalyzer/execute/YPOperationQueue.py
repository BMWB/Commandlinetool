#!/usr/bin/env python3
#_*_ coding: utf-8 _*_

'operation queue module'

_author_ = 'Yaping Liu'

"""
custom operation function:
def testTaskFunc(taskInfo):
    use taskInfo.currentTask to do....

create ypqueue object:
opq = OperationQueue(operationFunc=testTaskFunc)

start operation tasks
opq.startOperation(tasks=[])

"""

import sys
import os
import queue
import threading
import time
import inspect

# _g_queueLock = threading.Lock()

class TaskInfo():
    def __init__(self, threadID, name):
        self._currentTask = None
        self.threadID = threadID
        self.name = name
    
    @property
    def currentTask(self):
        return self._currentTask
    

    @currentTask.setter
    def currentTask(self, value):
        self._currentTask = value



class OperationThread(threading.Thread):
    def __init__(self, threadID, name, queue, operationFunc):
        threading.Thread.__init__(self)
        self.__taskInfo = TaskInfo(threadID, name)
        self.__queue = queue
        self.__operationFunc = operationFunc


    def run(self):
        while True:
            if self.__queue.empty():
                break
            try:
                task = self.__queue.get()
                self.__taskInfo.currentTask = task
                self.__operationFunc(self.__taskInfo)
            finally:
                self.__queue.task_done()



class OperationQueue():
    def __init__(self, threadsCount = 1, operationFunc = None):
        self.__enable = True
        if not inspect.isfunction(operationFunc):
            print("`operationFunc` must be a function!")
            self.__enable = False
            return
        elif len(inspect.getfullargspec(operationFunc).args) != 1:
            print("`operationFunc` must have only one param!")
            self.__enable = False
            return

        self.__workQueue = queue.Queue()
        self.__threads = []
        
        #creat threads
        if threadsCount < 1:
            threadsCount = 1
        threadNames = []
        for i in range(0, threadsCount):
            tn = 'T%d' % i
            threadNames.append(tn)
        threadID = 0
        for tn in threadNames:
            t = OperationThread(threadID, tn, self.__workQueue, operationFunc)
            t.daemon = True
            self.__threads.append(t)
            threadID += 1
        

    def startOperation(self, tasks = []):
        if not self.__enable or len(tasks) < 1:
            print("Can't start opetation!")
            return

        #put in work queue
        for t in tasks:
            self.__workQueue.put(t)

        #thread start
        for pert in self.__threads:
            pert.start()

        #wait all tasks complete
        self.__workQueue.join()
        


def testMethod():
    def testTaskFunc(taskInfo):
        print('Doing task:%s,  name:%s,   ID:%s\n' % (taskInfo.currentTask, taskInfo.name, taskInfo.threadID))
        time.sleep(1)
    
    opq = OperationQueue(threadsCount=8,operationFunc=testTaskFunc)
    
    tasks = []
    for num in range(0,10):
        ttt = 'Task_%d' % num
        tasks.append(ttt)
    opq.startOperation(tasks)



def main():
    testMethod()
    

if __name__ == "__main__":
    main()






