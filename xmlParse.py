#-*- coding:utf-8 -*-
'''
Created on 2017年6月14日

@author: will
'''
import xml.etree.ElementTree as ET
import os, re, time

class UIDump():
    #
    #
    size= [0,]
    def __init__(self):
        self.path = r'e:\\TBD\\newjob\\'
    
    def uidump(self,name):
        #获取当前Activity控件树
        os.popen('adb shell uiautomator dump /sdcard/%s-window_dump.xml' % name)
        os.popen('adb pull /sdcard/%s-window_dump.xml' % name + ' ' + self.path)
        #通过判断保存路径下文件Size是否大于0字节判定是否已Dump成功
        if os.path.getsize(self.path + '%s-window_dump.xml' % name) > 0:
            #清理掉手机存储器中的.xml文件
            self.size.append(os.path.getsize(self.path + '%s-window_dump.xml' % name))
            os.popen('adb shell rm /sdcard/%s-window_dump.xml' % name)
            #print self.size[-1]
        else:
            print 'Dump failed, please check the connection of DUT'
            raise Exception
        xmlTree = ET.parse(self.path + '%s-window_dump.xml' % name)
        xmlTreeIter = xmlTree.iter(tag='node')
        #将xml文件解析后结果回传
        
        return xmlTreeIter
    
    def pageSwipe(self):
        #当前屏幕显示区域找不到Element时下翻屏显
        os.popen('adb shell input swipe 800 1000 800 400')

class Element(object):
    '''
          定位元素，Android 4+
    '''
    def __init__(self):
        '''
        构造初始环境，dump文件本地存储目录，元素坐标为数字故正则提取节点属性中的数字值
        '''
        self.path = r'e:\\TBD\\newjob\\'
        self.pattern = re.compile(r"\d+")
    
    def elementLocate(self, attrib, name, xmlTreeIter):
        #返回元素text及其所占区块中点坐标
           
        for elem in xmlTreeIter:
            if elem.attrib[attrib] == name:
                #获取元素位置边界，左上角坐标&右下角坐标值，xml文件中bounds字段如下
                #示例：bounds="[130,658][242,712]"
                bounds = elem.attrib['bounds']
                coord = self.pattern.findall(bounds)
                print '\nThe bounds of the element %s is:' % name
                print [coord[0], coord[1]] + [coord[2], coord[3]]
                #通过元素起止坐标点计算其中心坐标值
                X = (int(coord[2]) - int(coord[0]))/2 + int(coord[0])
                Y = (int(coord[3]) - int(coord[1]))/2 + int(coord[1])
                print 'The center coord of the element %s is:' % name
                print [X, Y]
                
                return X, Y
                    

    def findElementByName(self, name, xmlTreeIter):
        #通过名称定位元素
        return self.elementLocate('text', name, xmlTreeIter)

class Event(object):
    def __init__(self):
        os.popen('adb wait-for-device')
        
    def touch(self, x, y):
        #模拟点击屏幕(x,y)坐标点
        os.popen('adb shell input tap '+ str(x) + ' ' + str(y))
        time.sleep(1)

if __name__ == '__main__':
    
    page = UIDump()
    element = Element()
    action = Event()
    
    #定义要寻找的元素,可以输入元素的test、resource-id或class-name
    tgName = 'Reset'
    
    while True:
        #执行uiautomator dump，返回解析结果
        dumpResult = page.uidump(tgName)
        if page.size[-1] == page.size[-2]:
            print 'Can not find the el, Please check the name'
            raise Exception
            #break
        #定位元素中心坐标
        #target = element.findElementByName(tgName, dumpResult)
        target = element.findElementByName(tgName, dumpResult)
    
        if target is None:
            page.pageSwipe()
            continue              
        else:
            print 'UIAutomator Dump success , saved as %s-window_dump.xml' % tgName
            print 'Element %s located success' % tgName
            break
        
        #异常场景【待优化】
        #当翻屏到Listview底部仍无法定位到指定元素时抛出异常
        #到底部判断依据：获取dump文件size压入size数组，每次循环比对末尾两个值是否相等
        #该判定依据并不可靠，极有可能出现两次dump文件虽然内容不同但size却相等，此时会误判
        ##比对文件dump文件内容是精准的办法但效率低
        action.touch(target[0],target[1])
