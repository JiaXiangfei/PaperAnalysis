options = [{'id': 1, 'name': '详细分析'}, {'id': 2, 'name': '匹配图片'}, {'id': 3, 'name': '翻译中文'}, {'id': 4, 'name': '分析文献'}]

md5_paperrec_folder_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\resnet'

import json

def option_json(options: list, md5_paperrec_folder_path):
    '''
    :param options: [{'id': 1, 'name': '详细分析'}, {'id': 2, 'name': '匹配图片'}, {'id': 3, 'name': '翻译中文'}, {'id': 4, 'name': '分析文献'}]
    :return:  前端用户选择的分析类型对应的json文件
    '''
    option_list = []
    retured_json_name = ''
    reference_name = "Reference.json"

    if len(options):
        for item in options:
            option_list.append(item['id'])
        # 检查元素是否存在
        insert_image = 2
        trans = 3
        reference = 4
        if trans in option_list:
            retured_json_name = 'images_insert_cn.json'
        else:
            retured_json_name = 'images_insert.json'

        full_path = '/'.join([md5_paperrec_folder_path, retured_json_name])
        with open(full_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        if reference in option_list:
            reference_path = '/'.join([md5_paperrec_folder_path, reference_name])
            with open(reference_path, 'r', encoding='utf-8') as json_file:
                reference_data = json.load(json_file)
            # dict1 = json.loads(data)
            # dict2 = json.loads(reference_data)
            data.update(reference_data)
            merged_dict = data
            # 如果需要将结果转换回JSON字符串
            data = json.dumps(merged_dict, ensure_ascii=False)
        return data
    else:
        print(f"元素不在列表中")

