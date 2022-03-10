# -*- coding: utf-8 -*-
'''
测试核心引擎模块
'''
from httptool import json_post
import os
import json
from log import logger
from report import HtmlReport
from tools import now_formate


def create_instance(module_name, class_name, *args, **kwargs):
    """
    根据模块、类名的字符串实例化类
    """
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj


class TestTask(object):
    """
        测试任务类
    """

    def __init__(self):
        self.name = None  # 测试任务名称
        self.testsuite_list = []  # 测试套件集合

    def run(self):
        """
        执行一个测试任务
        testtask,执行的测试任务
        """
        for testsuite in self.testsuite_list:
            # 执行测试套件
            testsuite.run()


class TestSuite(object):
    """
        测试套件类
    """

    def __init__(self):
        self.suitename = None  # 测试套件名称
        self.filename = ''  # 测试套件的文件名称
        self.testcase_list = []  # 测试用例集合
        self.result = True  # 测试套件测试结果

    def run(self):
        """
        执行一个测试套件，并且进行验证
        """
        suite_data = {}  # 在测试套件内传递数据
        for testcase in self.testcase_list:
            if self.result is True or testcase.ignore is False:
                testcase.suite_data = suite_data
                # 运行测试用例
                if testcase.setup() is True:
                    testcase.run()
                else:
                    testcase.result = False
                    testcase.reason = '前置方法执行失败'
                testcase.teardown()
                suite_data = testcase.suite_data

                # 设置测试套件测试结果
                if testcase.result is False and self.result is True:
                    # 如果测试用例执行失败，则测试套件失败
                    self.result = False


class TestCase(object):
    """
        测试用例类
    """

    def __init__(self):
        self.casename = None  # 测试用例名称
        self.hostname = None  # 请求服务器地址
        self.urlpath = None  # 请求地址
        self.request = {}  # 请求数据
        self.response = {}  # 预期响应数据
        self.actual = {}  # 实际响应数据
        self.result = None  # 测试结果
        self.reason = None  # 失败原因
        self.start_time = ''  # 用例执行开始时间
        self.end_time = ''  # 用例执行结束时间
        self.suite_data = {}  # 测试套件之间传递的数据
        self.ignore = True   # 前面测试用例执行失败时，是否忽略执行

    def setup(self):
        """
            前置执行方法
        """
        return True

    def teardown(self):
        """
            后置执行方法
        """
        pass

    def do_assert(self):
        """
            验证结果的方法
        """
        return [True, None]

    def run(self):
        """
            执行测试脚本
        """
        # 发送请求
        self.start_time = now_formate()  # 请求开始时间
        self.action()  # 执行脚本
        self.end_time = now_formate()  # 请求结束时间

        # 对比实际数据和期望数据
        result, renson = self.do_assert()

        if result is False:
            self.reason = renson
            self.result = result
        else:
            # 测试通过
            self.result = True

    def action(self):
        """
           实际执行的动作，需要被子类继承使用
        :return:
        """
        url = '{}/{}'.format(self.hostname, self.urlpath)
        self.actual = json_post(url, self.request)  # 发起请求


class Config(object):
    """
        配置信息类
    """

    def __init__(self):
        self.data = {}  # 公共数据

    def load(self, filepath):
        """
            载入环境变量
        """
        with open(filepath, 'r', encoding='utf-8') as load_f:
            try:
                # 将文本文件的内容加载成json格式
                self.data = json.load(load_f)
            except Exception as e:
                logger.error('解析配置文件%s失败,原因%s' % (filepath, repr(e)))

    def convert_public_data(self, convert_data):
        """
            如果字符串中有需要替换的为配置信息的数据，则替换为公共数据
        """
        if isinstance(convert_data, dict):
            # 处理字典
            convert_dict = {}
            for k, v in convert_data.items():
                convert_dict[k] = self.convert_public_data(v)
            ret_data = convert_dict
        elif isinstance(convert_data, list):
            # 处理列表
            convert_list = []
            for tmp_data in convert_data:
                convert_list.append(self.convert_public_data(tmp_data))
            ret_data = convert_list
        elif isinstance(convert_data, str):
            # 需要处理的数据是字符串的情况
            ret_data = convert_data  # 默认不转换数据
            if convert_data.find('{#') >= 0 and convert_data.find('}') >= 0:
                if 'public_data' in self.data:
                    convert_data_array = convert_data.split('{#')
                    ret_str_list = []
                    n = 0
                    for tmp_data in convert_data_array:
                        if n > 0:
                            end_index = tmp_data.find('}')
                            if end_index > 0:
                                key = tmp_data[0:end_index]
                                public_data = self.data['public_data']
                                if key in public_data:
                                    real_str = public_data[key]
                                    ret_str = tmp_data.replace('%s}' % key, real_str)
                            else:
                                ret_str = tmp_data
                            ret_str_list.append(ret_str)
                        else:
                            ret_str_list.append(tmp_data)
                        n = n + 1
                    ret_data = ''.join(ret_str_list)
        else:
            # 其它情况
            ret_data = convert_data

        return ret_data


class Driver(object):
    """
        测试驱动类
    """

    def __init__(self, folder_path, env_filename):
        """
         初始化
        :param folder_path: 用例配置等文件的根目录位置
        :param env_filename: 环境文件名称
        """
        self.__case_path__ = os.path.join(folder_path, 'testcase')  # 测试用例目录
        self.__config_path__ = os.path.join(folder_path, 'config')  # 配置文件目录
        self.__report_path__ = os.path.join(folder_path, 'report')  # 报告文件目录
        # 载入测试环境配置
        self.config.load(os.path.join(self.__config_path__, env_filename))

        self.testtask = TestTask()  # 测试任务
        self.config = Config()  # 配置信息类

    def load_from_folder(self, path):
        """
                载入指定目录中的所有测试用例，包括子目录
        """
        for file in os.listdir(path):
            filepath = os.path.join(path, file)
            if os.path.isfile(filepath):
                self.load_testsuite(filepath)
            else:
                self.load_from_folder(filepath)

    def load_from_file(self, filepath):
        """
           载入指定名称的测试用例
        """
        if os.path.isfile(filepath):
            self.load_testsuite(filepath)
        else:
            logger.info('不存在文件{}'.format(filepath))

    def load_testsuite(self, filepath):
        """
           从指定文件中载入测试套件
        """
        with open(filepath, 'r', encoding='utf-8') as load_f:
            try:
                # 将文本文件的内容加载成json格式
                load_dict = json.load(load_f)
            except Exception as e:
                logger.error('解析用例文件%s失败,原因%s' % (filepath, repr(e)))
                return None
            # 加载测试套件
            testSuite = TestSuite()
            # 测试文件是一个测试套件
            testSuite.suitename = load_dict['suitename']  # 测试套件名称
            testSuite.filename = os.path.basename(filepath)  # 测试套件的文件名称
            testcases = load_dict['testcases']
            for case_data in testcases:
                # 加载测试用例
                script_module = case_data['module']
                script_class = case_data['class']
                testcase = create_instance(script_module, script_class)  # 动态创建测试用例实例

                testcase.casename = case_data['casename']
                testcase.hostname = self.config.convert_public_data(case_data['hostname'])
                testcase.urlpath = self.config.convert_public_data(case_data['urlpath'])
                if 'ignore' in case_data:
                    if case_data['ignore'] == 'False':
                        testcase.ignore = False
                testcase.request = self.config.convert_public_data(case_data['request'])
                testcase.response = self.config.convert_public_data(case_data['response'])

                # 追加测试用例到测试套件中
                testSuite.testcase_list.append(testcase)

            # 追加测试套件到测试任务中
            self.testtask.testsuite_list.append(testSuite)

    def run(self, env_filename, case_folder=None, case_filename=None):
        """
            执行测试
            env_filename,环境配置文件名称
            case_filename,执行的用例文件名称
        """
        # 载入测试用例
        if case_filename is not None and case_folder is not None:
            self.load_from_file(os.path.join(self.__case_path__, case_folder, case_filename))
        elif case_filename is not None and case_folder is None:
            self.load_from_file(os.path.join(self.__case_path__, case_filename))
        elif case_filename is None and case_folder is not None:
            self.load_from_folder(os.path.join(self.__case_path__, case_folder))
        else:
            self.load_from_folder(self.__case_path__)

            # 执行测试
        self.testtask.run()

        # 在日志中输出测试报告
        self.report_to_log(self.testtask)

        # 生成HTML格式测试报告
        t = HtmlReport(self.__report_path__)
        t.build(self.testtask)

    def report_to_log(self, testtask):
        """
                输出测试报告
        """
        logger.info('******输出测试结果********')
        for testsuite in testtask.testsuite_list:
            if testsuite.result is True:
                logger.info('套件执行通过,[{}]'.format(testsuite.suitename))
            else:
                logger.info('套件执行失败,[{}]'.format(testsuite.suitename))
            for testcase in testsuite.testcase_list:
                if testcase.result is True:
                    logger.info('-->用例执行通过,[{}]'.format(testcase.casename))
                else:
                    logger.info('-->用例执行失败,[{}],原因:{}'.format(testcase.casename, testcase.reason))

        logger.info('****输出测试结果结束*******')



