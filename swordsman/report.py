# -*- coding: utf-8 -*-
'''
测试报告模块
'''
from log import logger
import time
from xml.dom.minidom import parse
from shutil import copyfile
import os


class HtmlReport(object):
    '''
    测试结果类
    '''

    def __init__(self, path):
        self.__resource_folder = '../resource'  # 测试报告模板目录
        self.__reportPath = path  # 测试报告目录
        self.__createTime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.__templateFilePath = os.path.join(self.__resource_folder, "reportTemplate.html")  # 报告模板文件路径
        self.__reportFileName = "report_%s.html" % (self.__createTime)
        self.__filepath = os.path.join(self.__reportPath, self.__reportFileName)  # 报告文件路径

    def __saveXml(self, doc, filepath):
        '''
                保存xml文件
        '''
        try:
            with open(filepath, 'w', encoding='UTF-8') as fh:
                doc.writexml(fh, indent='', addindent='\t', newl='\n', encoding='UTF-8')
        except Exception as e:
            logger.error('保存报告文件失败,原因%s' % repr(e))

    def build(self, testtask):
        '''
                生成测试报告
        '''
        # 根据模板文件生成报告文件
        filepath = self.__filepath
        if os.path.exists(filepath) == False:
            copyfile(self.__templateFilePath, filepath)

        try:
            # 打开结果文件
            doc = parse(filepath)
        except Exception as e:
            logger.error('打开报告模板文件失败,原因%s' % repr(e))
            return

            # 定位到body/div/table节点
        rootNode = doc.documentElement
        bodyNode = rootNode.getElementsByTagName('body')
        divNode = bodyNode[0].getElementsByTagName('div')
        tableNode = divNode[0].getElementsByTagName('table')

        n = 0
        for testsuite in testtask.testsuite_list:
            n += 1
            # 添加testsuite结果到报告中
            trNode = doc.createElement('tr')
            # 添加用例名称
            tdNode = doc.createElement('td')
            tdNode.setAttribute('class', 'table_suite')
            tdNode.setAttribute('colspan', '5')
            tdText = doc.createTextNode('{}--{}--{}'.format(n, testsuite.filename, testsuite.suitename))
            tdNode.appendChild(tdText)
            trNode.appendChild(tdNode)
            # 整行添加到dom中
            tableNode[0].appendChild(trNode)

            # 添加testcase结果到报告中
            for testcase in testsuite.testcase_list:
                trNode = doc.createElement('tr')
                # 添加用例名称
                tdNode = doc.createElement('td')
                tdNode.setAttribute("class", "table_case")
                tdText = doc.createTextNode(testcase.casename)
                tdNode.appendChild(tdText)
                trNode.appendChild(tdNode)
                # 添加开始时间
                tdNode = doc.createElement('td')
                tdNode.setAttribute("class", "table_case")
                tdText = doc.createTextNode(testcase.start_time)
                tdNode.appendChild(tdText)
                trNode.appendChild(tdNode)
                # 添加结束时间
                tdNode = doc.createElement('td')
                tdNode.setAttribute("class", "table_case")
                tdText = doc.createTextNode(testcase.end_time)
                tdNode.appendChild(tdText)
                trNode.appendChild(tdNode)
                # 添加状态
                tdNode = doc.createElement('td')
                if testsuite.result == True:
                    tmpStr = "Pass"
                    tdNode.setAttribute("class", "table_pass")
                elif testsuite.result == False:
                    tmpStr = "Fail"
                    tdNode.setAttribute("class", "table_fail")
                else:
                    tmpStr = "Undo"
                    tdNode.setAttribute("class", "table_case")
                tdText = doc.createTextNode(tmpStr)
                tdNode.appendChild(tdText)
                trNode.appendChild(tdNode)

                # 添加失败原因
                tdNode = doc.createElement('td')
                tdNode.setAttribute("class", "table_case")
                if testcase.reason is None:
                    tdText = doc.createTextNode(' ')
                else:
                    tdText = doc.createTextNode(testcase.reason)
                tdNode.appendChild(tdText)
                trNode.appendChild(tdNode)

                # 整行添加到dom中
                tableNode[0].appendChild(trNode)

        # 保存xml文件
        self.__saveXml(doc, filepath)

