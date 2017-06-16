# Adroid listView 组件内容自动遍历查找元素
需求
Android自动化测试需要通过Resource-id\XPath等属性进行定位，之后才可以传递点击、输入等动作事件，listView是比较特殊的组件，内部显示的内容通常会超过一屏需要通过拖动屏幕才能展示完，如果需要对其内部元素进行操作而该元素又恰恰没显示在靠近顶部的位置，实现起来就有些困难，因uiautomator每次只能抓取当前屏幕的内容，本例用于解决该问题。


思路
adb shell uiautomator dump 获取当前activity当前屏显区域的控制树xml文件；
python 解析xml遍历查找，如找到元素则计算其所在区域中心坐标值并返回，如未找到则向上拖动屏幕重新dump并解析后遍历查找；


实例
某Android手机设置成英语界面，Settings中第一屏中有 WLAN 元素，下翻三屏有Reset元素，分别尝试自动查找并点击。


代码及注释
【代码模拟在Android手机 设置页面中查找某个元素，如 Reset】，代码及注释见xmlParse.py


        
 打印输出与手机反应
  手机自动翻屏并停止在“Reset”元素显示的位置
     
      The bounds of the element Reset is:
      ['228', '1820', '416', '1922']
      The center coord of the element Reset is:
      [322, 1871]
      UIAutomator Dump success , saved as Reset-window_dump.xml
      Element Reset located success
