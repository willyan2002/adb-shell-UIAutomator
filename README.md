# Adroid listView 组件内容自动遍历查找元素
需求
Android自动化测试需要通过Resource-id\XPath等属性进行定位，之后才可以传递点击、输入等动作事件，listView是比较特殊的组件，内部显示的内容通常会超过一屏需要通过拖动屏幕才能展示完，如果需要对其内部元素进行操作而该元素又恰恰没显示在靠近顶部的位置，实现起来就有些困难，因uiautomator每次只能抓取当前屏幕的内容，本例用于解决该问题。

思路
adb shell uiautomator dump 获取当前activity当前屏显区域的控制树xml文件；
python 解析xml遍历查找，如找到元素则计算其所在区域中心坐标值并返回，如未找到则向上拖动屏幕重新dump并解析后遍历查找；

实例
某Android手机设置成英语界面，Settings中第一屏中有 WLAN 元素，下翻三屏有Reset元素，分别尝试自动查找并点击。

代码及注释
【代码模拟在Android手机 设置页面中查找某个元素，如 Reset】
#-*- coding:utf-8 -*-
'''
Created on 2017年6月14日

@author: will
'''
import xml.etree.ElementTree as ET
import os, re, time

class UIDump():
      '''
      执行adb shell uiautomator dump指令，将生成的xml文件下载到本地并从手机内存中清除
      '''
    #存放取回本地的xml文件size值，用于判定dump及取回本地动作是否成功
    size= [0,]
    def __init__(self):
        #定义xml文件本地存放路径
        self.path = r'e:\\TBD\\newjob\\'
    
    def uidump(self,name):
        #获取当前Activity控件树，以当前查找元素名称命名，如WLAN-window_dump.xml
        os.popen('adb shell uiautomator dump /sdcard/%s-window_dump.xml' % name)
        os.popen('adb pull /sdcard/%s-window_dump.xml' % name + ' ' + self.path)
        
        #通过判断保存路径下文件Size是否大于0字节判定是否已Dump成功
        if os.path.getsize(self.path + '%s-window_dump.xml' % name) > 0:
            #清理掉手机存储器中的.xml文件
            self.size.append(os.path.getsize(self.path + '%s-window_dump.xml' % name))
            os.popen('adb shell rm /sdcard/%s-window_dump.xml' % name)
            print self.size[-1]
        else:
            print 'Dump failed, please check the connection of DUT'
            raise Exception
        
        #将xml文件解析后结果回传，作为参数传递给元素遍历函数elementLocate()
        xmlTree = ET.parse(self.path + '%s-window_dump.xml' % name)
        xmlTreeIter = xmlTree.iter(tag='node')      
        return xmlTreeIter
    
    def pageSwipe(self):
        #下翻屏显,当前屏幕显示区域找不到Element时调用，翻屏幅度尽量保守，不宜超过2/3屏
        os.popen('adb shell input swipe 800 1000 800 400')
       
       
class Element(object):
    '''
          遍历xml树，查找元素所在区域的Bouds并计算出其近似中心点坐标
    '''
    def __init__(self):
        '''
        dump文件本地存储目录，bounds是数字所以正则匹配数字模式
        '''
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
        #通过名称定位元素，作为用户接口，可以在主函数中通过该方法调用elementLocate()方法
        #可通过 text\resource-id\classname定位，方法通过参数形式传入
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
    
    ##用户传参接口
    #定义要寻找的元素,如要寻找Reset
    tgName = 'Reset'
    
    while True:
        #执行uiautomator dump，返回解析结果xmlTreeIter
        xmlTreeIter = page.uidump(tgName)
        
        #异常场景【待优化】
        #当翻屏到Listview底部仍无法定位到指定元素时抛出异常
        #到底部判断依据：获取dump文件size压入size数组，每次循环比对末尾两个值是否相等
        #该判定依据并不可靠，极有可能出现两次dump文件虽然内容不同但size却相等，此时会误判
        ##比对文件dump文件内容是精准的办法但效率低
        if page.size[-1] == page.size[-2]:
            print 'Can not find the el, Please check the name'
            raise Exception
            
        #定位元素中心坐标
        target = element.findElementByName(tgName, xmlTreeIter)
       
        if target is None:
            page.pageSwipe()
            continue              
        else:
            print 'UIAutomator Dump success , saved as %s-window_dump.xml' % tgName
            print 'Element %s located success' % tgName
            break
       
       #发送点击动作给定位到的元素
        action.touch(target[0],target[1])
         
        
     打印输出与手机反应
     手机自动翻屏并停止在“Reset”元素显示的位置
     
      The bounds of the element Reset is:
      ['228', '1820', '416', '1922']
      The center coord of the element Reset is:
      [322, 1871]
      UIAutomator Dump success , saved as Reset-window_dump.xml
      Element Reset located success
