#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import csv
import logging
import os
from xmind2testcase.utils import get_xmind_testcase_list, get_absolute_path

"""
Convert XMind fie to Zentao testcase csv file 

Zentao official document about import CSV testcase file: https://www.zentao.net/book/zentaopmshelp/243.mhtml 
"""

# 主函数
def xmind_to_zentao_csv_file(xmind_file):
    """Convert XMind file to a zentao csv file"""
    logging.info("走到这---------------------------------------------------")
    xmind_file = get_absolute_path(xmind_file)
    logging.info('Start converting XMind file(%s) to zentao file...', xmind_file)
    # 拿testcases,是个列表
    testcases = get_xmind_testcase_list(xmind_file)
    # 添加csv标题
    fileheader = ["所属模块", "用例标题", "前置条件", "步骤ID","步骤", "预期", "关键词", "优先级", "用例类型", "适用阶段"]
    zentao_testcase_rows = [fileheader]

    # 适配jira格式-汪䶮
    modified_testcases = []
    for testcase in testcases:
        if len(testcase['steps']) > 1:  # 如果steps列表长度大于1，则进行拆分
            i = 0
            for step in testcase['steps']:
                i = i + 1
                # 遍历列表，对列表值拆分
                new_testcase = testcase.copy()  # 复制原始测试用例的信息
                
                # 更新新测试用例的步骤信息
                new_testcase['steps'] = [step]
                new_testcase.update({"stepId": i})
                # 生成一行新的测试用例数据
                row = gen_a_testcase_row(new_testcase)
                zentao_testcase_rows.append(row)
                
                # 将修改后的测试用例添加到列表中以供后续写入CSV文件
                modified_testcases.append(new_testcase)
        else:
            testcase.update({"stepId": 1})
            row = gen_a_testcase_row(testcase)

            zentao_testcase_rows.append(row)
            modified_testcases.append(testcase)


    
    # for testcase in modified_testcases:
    #     row = gen_a_testcase_row(testcase)
    #     zentao_testcase_rows.append(row)
    #     # print("11111111111111111")
    #     # print(row)
    zentao_file = xmind_file[:-6] + '.csv'
    if os.path.exists(zentao_file):
        os.remove(zentao_file)
        # logging.info('The zentao csv file already exists, return it directly: %s', zentao_file)
        # return zentao_file

    with open(zentao_file, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(zentao_testcase_rows)
        logging.info('Convert XMind file(%s) to a zentao csv file(%s) successfully!', xmind_file, zentao_file)

    return zentao_file

# 把xmind的数据填充
def gen_a_testcase_row(testcase_dict):
    # 模块
    case_module = gen_case_module(testcase_dict['suite'])
    # 用例名称
    case_title = testcase_dict['name']
    # 前置条件
    case_precontion = testcase_dict['preconditions']
    # 步骤
    case_step, case_expected_result = gen_case_step_and_expected_result(testcase_dict['steps'])
    # 步骤ID
    case_stepId = testcase_dict['stepId']
    # 关键词
    case_keyword = ''
    # 优先级
    case_priority = gen_case_priority(testcase_dict['importance'])
    # 执行方式
    case_type = gen_case_type(testcase_dict['execution_type'])
    case_apply_phase = '迭代测试'
    row = [case_module, case_title, case_precontion, case_stepId, case_step, case_expected_result, case_keyword, case_priority, case_type, case_apply_phase]
    return row

# 模块
def gen_case_module(module_name):
    if module_name:
        module_name = module_name.replace('（', '(')
        module_name = module_name.replace('）', ')')
    else:
        module_name = '/'
    return module_name

# 操作步骤和预期结果？
def gen_case_step_and_expected_result(steps):
    case_step = ''
    case_expected_result = ''

    for step_dict in steps:
        case_step += str(step_dict['step_number']) + '. ' + step_dict['actions'].replace('\n', '').strip() + '\n'
        case_expected_result += str(step_dict['step_number']) + '. ' + \
            step_dict['expectedresults'].replace('\n', '').strip() + '\n' \
            if step_dict.get('expectedresults', '') else ''
    return case_step, case_expected_result

# 优先级
def gen_case_priority(priority):
    mapping = {1: '高', 2: '中', 3: '低'}
    if priority in mapping.keys():
        return mapping[priority]
    else:
        return '中'

# 执行方式
def gen_case_type(case_type):
    mapping = {1: '手动', 2: '自动'}
    if case_type in mapping.keys():
        return mapping[case_type]
    else:
        return '手动'


if __name__ == '__main__':
    xmind_file = '../docs/ThunderCollection.xmind'
    zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
    print('Conver the xmind file to a zentao csv file succssfully: %s', zentao_csv_file)