import re
import requests
import random
import json
from hashlib import md5

# Set your own appid/appkey.
appid = '20230920001823881'
appkey = 'X71IjR_X928g9YBNhn99'

# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
from_lang = 'en'
to_lang = 'zh'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


def get_title_list(text_parts_path):
    # 读取JSON文件并将其转换为字典
    with open(text_parts_path, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)

    # 获取字典中的所有键
    keys = data_dict.keys()
    title_list = list(keys)

    # 打印所有键
    return title_list


def txt_to_json(titles, txt_file_path, json_file_path):
    """
    根据提供的标题列表从TXT文件中提取内容，并保存到JSON文件。

    参数:
    titles (list): 包含标题文本的列表。
    txt_file_path (str): TXT文件的路径。
    json_file_path (str): 输出JSON文件的路径。

    返回:
    None
    """
    # 读取TXT文件内容
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # 初始化一个空字典来存储数据
    data = {}

    # 使用正则表达式匹配标题及其内容
    for i, title in enumerate(titles):
        # 如果是最后一个标题，匹配标题到文本结束的内容
        if i == len(titles) - 1:
            pattern = r'(^|\b)' + re.escape(title) + r'(.*)$'
        # 否则，匹配当前标题和下一个标题之间的内容

        else:
            pattern = r'((?<=\n)' + re.escape(title) + r'(.*?)(?=\n\s*' + re.escape(titles[i + 1]) + r'\s*\n))'

        match = re.search(pattern, text, re.DOTALL)

        # 如果找到匹配项，则将内容添加到字典中
        if match:
            content = match.group(2).strip()  # 注意：捕获组根据正则表达式可能有所不同

            data[title] = content
        else:
            # 如果没有找到匹配项，则添加一个空字符串作为内容
            data[title] = ""

    # 将字典转换为 JSON 文件
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)



def json_file_to_dict(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"错误：文件 {json_file_path} 未找到。")
        return None
    except json.JSONDecodeError:
        print(f"错误：文件 {json_file_path} 不是有效的JSON格式。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def clean_dict_values(data_dict, pattern):
    """
    清洗字典中的每个值，移除匹配特定模式的子串。

    参数:
    data_dict (dict): 要清洗的字典。
    pattern (str): 正则表达式模式，用于匹配要移除的字符。

    返回:
    dict: 清洗后的字典。
    """
    for key, value in data_dict.items():
        if isinstance(value, str):
            # 使用正则表达式替换匹配pattern的子串为空字符串
            cleaned_value = re.sub(pattern, '', value)
            # 更新字典中的值，同时移除换行符
            data_dict[key] = cleaned_value.replace('\n', '')
    return data_dict


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def translate_api(query):
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    print(result)
    return result["trans_result"][0]["dst"]


# def extract_and_translate(text, pattern):
#     # 使用正则表达式匹配标识符及其文本
#     matches = re.finditer(pattern, text)
#
#     # 初始化索引，用于遍历文本
#     index = 0
#     translated_text = ""
#
#     # 遍历所有匹配的标识符
#     for match in matches:
#         # 翻译标识符前的文本
#         before_marker = text[index:match.start()]
#         translated_before = translate_api(before_marker)
#         translated_text += translated_before
#
#         # 添加换行符和标识符本身
#         translated_text += "\n" + match.group()
#
#         # 在标识符后添加“\n”
#         translated_text += "\n"
#
#         # 更新索引为当前标识符的结束位置
#         index = match.end()
#
#     # 翻译最后一个标识符后的所有文本
#     if index < len(text):
#         after_last_marker = text[index:]
#         translated_after = translate_api(after_last_marker)
#         translated_text += translated_after
#
#     translated_text += "\n"
#
#     return translated_text


def extract_and_translate(text, pattern):
    # 使用正则表达式匹配标识符及其文本
    matches = list(re.finditer(pattern, text))

    # 初始化索引，用于遍历文本
    index = 0
    translated_text = ""

    # 处理开始处可能存在的连续标识符
    if matches and matches[0].start() == 0:
        # 连接所有连续的起始标识符
        initial_markers = ''.join(match.group() for match in matches if match.start() == 0)
        translated_text += initial_markers + "\n"
        index = matches[0].end()

    # 从第一个非起始连续标识符开始处理后续的匹配项
    for match in matches:
        if match.start() == index:  # 检查是否连续
            translated_text += match.group() + "\n"
            index = match.end()
            continue

        # 确保在标识符前有文本才进行翻译
        before_marker = text[index:match.start()]
        if before_marker:  # 只有当before_marker不为空时才调用翻译API
            translated_before = translate_api(before_marker)
            translated_text += translated_before
        else:  # 如果没有前导文本，直接添加换行符和标识符
            translated_text += "\n"

        # 添加换行符和标识符本身
        translated_text += match.group() + "\n"

        # 更新索引为当前标识符的结束位置
        index = match.end()

    # 翻译最后一个标识符后的所有文本，考虑最后可能没有文本的情况
    after_last_marker = text[index:]
    translated_after = "" if not after_last_marker else translate_api(after_last_marker)
    translated_text += translated_after

    translated_text += "\n"

    return translated_text


def translate(text_parts_path, txt_path, image_insert_json, image_tag):

    title_list = get_title_list(text_parts_path)
    txt_to_json(title_list, txt_path, image_insert_json)
    data_dict = json_file_to_dict(image_insert_json)
    data_dict = clean_dict_values(data_dict,  r'[\n/\*\-\+]')
    print(data_dict)
    result_cn = {}
    for key, value in data_dict.items():
        # 调用translate_api方法进行翻译
        translated_value = extract_and_translate(value, image_tag)
        # 将翻译后的值赋给新字典
        result_cn[key] = translated_value
    return result_cn





# 假设 'data.json' 是你的JSON文件的名称
# text_parts_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\resnet\text_parts.json'
# txt_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\resnet\images_insert.txt'
# json_file_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\test\images_insert.json'

# print(translate(text_parts_path, txt_path, json_file_path,  image_tag=r"<(\d+)>"))