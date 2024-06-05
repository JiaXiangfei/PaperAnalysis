
from Agents.Extracted_Analysis_Agent import Extract_Analysis_Agent

from utils.Prompts import task_dic
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTChar
from collections import defaultdict
import re
import ast
import json
from collections import OrderedDict
from .Prompts import Analysis_Model_Prompt_English


#按页提取文本、每页字数和每个字符的字体名和字符大小
def extract_text_and_fonts_by_page(pdf_path):
    text_by_page = {}
    word_count_by_page = {}
    fonts_by_page = {}

    for page_number, page_layout in enumerate(extract_pages(pdf_path)):
        text_elements = []
        font_details = []

        for element in page_layout:
            if isinstance(element, LTTextBox):
                text_block = ""
                for text_line in element:
                    text_block += text_line.get_text()

                    if hasattr(text_line, '__iter__'):  # 确保text_line是可迭代的
                        for character in text_line:
                            if isinstance(character, LTChar):
                                font_details.append((character.get_text(), character.fontname, character.size))
                    else:
                    # 处理非可迭代的text_line情况
                        if isinstance(text_line, LTChar):
                            font_details.append((text_line.get_text(), text_line.fontname, text_line.size))

                text_elements.append(text_block)

        page_text = "\n".join(text_elements)
        text_by_page[page_number + 1] = page_text
        word_count_by_page[page_number + 1] = len(page_text)
        fonts_by_page[page_number + 1] = font_details


    return text_by_page, word_count_by_page, fonts_by_page


def find_main_and_titles_fonts(fonts):
    font_counts = defaultdict(int)
    for page_fonts in fonts.values():
        for _, font_name, font_size in page_fonts:
            font_counts[(font_name, font_size)] += 1

    # 根据正文的字数最多，找出正文文本的字体样式
    main_text_style = max(font_counts, key=font_counts.get)
    main_text_size = main_text_style[1]

    # 收集所有可能的标题字体样式，对标题的字体大小做一点条件限制，不能和正文字体相差太小，也不能相差太大（依次排除字体特大的水印）
    tolen_min = 0.0001
    tolen_max = 1
    titles_fonts = [(font_name, font_size) for (font_name, font_size), _ in font_counts.items() if
                    main_text_size * (1 + tolen_max) > font_size > main_text_size * (1 + tolen_min)]

    # 返回正文字体格式，可能的标题格式
    return main_text_style, titles_fonts


def extract_titles_from_full_text(titles_fonts, full_pdf_text, combined_fonts):
    title_candidates = []  # 储存可能的标题字符串
    current_title = ''  # 储存可能的标题字符串

    # 遍历combined_fonts来匹配字体信息
    for char, font_name, font_size in combined_fonts:
        if (font_name, font_size) in titles_fonts:
            current_title += char  # 如果匹配，将匹配的字符加入到当前标题字符串中
        else:  # 否则，如果之前已经开始记录一个标题，将当前标题候选添加到列表中
            if current_title:
                title_candidates.append(current_title)
                current_title = ''
                # 检查是否有未处理的标题候选
    if current_title:
        title_candidates.append(current_title)

    # 在原始文本中匹配这些标题候选
    extracted_titles = []
    for candidate in title_candidates:
        # 构建一个正则表达式，允许标题中存在任意数量和位置的空格
        pattern = r'\s*'.join(re.escape(char) for char in candidate)
        matches = re.finditer(pattern, full_pdf_text)
        for match in matches:
            extracted_titles.append(match.group())

    extracted_titles = [title for title in extracted_titles if len(title) >= 5]

    return extracted_titles


def find_section_headings(full_pdf_text):
    pattern = r'(?m)^[0-9A-Z].*(?=\n)'
    matches = re.finditer(pattern, full_pdf_text)
    headings = [
        match.group(0).strip() for match in matches
        if match.group(0).count(' ') <= 10  #一级标题中空格的个数不超过10个
    ]

    return headings


def clean_list(extrcated_list):
    special_pattern = r'[\t\n\r\f\v\b]'
    cleaned_list = [re.sub(special_pattern, '', item) for item in extrcated_list]  # 清洗字符串中的特殊符号
    cleaned_list = [s for s in cleaned_list if any(c.isalpha() for c in s)]  # 删掉全是数字的字符串
    cleaned_list = [item for item in cleaned_list if 50 > len(item) >= 5]  # 删掉过长和过短的字符串
    second_level_pattern = re.compile(r'\.\S')  # 删掉第一个出现的小数点不是空格的字符串，即，删掉二级标题
    disallowed_end_chars = {'.', ',', ':'}  # 一级标题不以小数点等符号结尾
    cleaned_list = [s for s in cleaned_list if
                    not (second_level_pattern.search(s)) and not (s[-1] in disallowed_end_chars)]

    return cleaned_list


def clean_list_elements(extracted_list):
    # 定义一个正则表达式，用于匹配特殊符号，如 \n, \t, \r 等
    special_characters_pattern = r'[\t\n\r\f\v\b]'

    # 使用列表推导式清洗每个元素，并创建一个新的清洗后的列表
    cleaned_list = [re.sub(special_characters_pattern, '', item) for item in extracted_list]

    return cleaned_list


#截取标题与标题之间的内容作为前一个标题下的所属内容
def titles_match_fulltext(located_titles, full_text):
    # 构建正则表达式，在标题后添加一个换行符进行匹配，匹配标题时忽略大小写和空格数量
    title_patterns = ['\\s*'.join([re.escape(char) for char in title] + ['\n']) for title in located_titles]
    title_regex = '(' + '|'.join(title_patterns) + ')'

    # 使用正则表达式分割全文，保留标题作为分隔符，并忽略大小写
    parts = re.split(title_regex, full_text, flags=re.IGNORECASE)
    # 使用OrderedDict以保留插入顺序
    structurized_content = OrderedDict()

    current_title = None
    for part in parts:
        # 检查部分是否为标题
        match = re.match(title_regex, part, flags=re.IGNORECASE)
        if match:
            # 移除标题中的多余空格和换行符，恢复原标题
            normalized_title = re.sub(r'\s+', ' ', match.group().strip())
            current_title = normalized_title.strip()
            structurized_content[current_title] = ''
        elif current_title:
            # 追加非标题部分到当前标题下的内容
            structurized_content[current_title] += part

        # 检查是否存在Abstract键
        abstract_key = next((key for key in structurized_content.keys() if "abstract" in key.lower()), None)
        if not abstract_key:
            # 找到Introduction的键
            introduction_key = next((key for key in structurized_content.keys() if "introduction" in key.lower()), None)
            if introduction_key:
                # 获取Introduction前的所有内容
                introduction_start = full_text.lower().find(introduction_key.lower())
                abstract_text = full_text[:introduction_start].strip()
                structurized_content["Abstract"] = abstract_text

    # 移除标题前后添加的换行符
    final_structurized_content = {title.strip(): content for title, content in structurized_content.items()}
    return final_structurized_content


def remove_spaces_and_uppercase_keys(input_dict):
    # 使用字典推导式来创建新字典，其中键已经被处理
    return {key.upper().replace(" ", ""): value for key, value in input_dict.items()}


def extract_values_as_text(structurized_content):
    # 使用列表推导式来提取所有值
    values = [value for value in structurized_content.values()]

    # 使用join方法将所有值连接成一个字符串
    text = ' '.join(values)

    return text


def get_task_by_title(text, task_dic):
    # 使用正则表达式去除文本中的数字和空格
    cleaned_text = re.sub(r'[0-9\s\.]+', '', text)
    cleaned_text_upper = cleaned_text.upper()

    # 检查清理后的文本是否是字典的一个键
    for key in task_dic.keys():
        if key in cleaned_text_upper:
            # 如果是，返回对应的值
            return task_dic[key]

    else:
        agent = Extract_Analysis_Agent(model = "gpt-4-turbo")
        response = agent.General_task(text)
        print("模型生成针对性分析任务" + response)
        return response


def get_task_by_title_easy(text, task_dic):
    # 使用正则表达式去除文本中的数字和空格
    cleaned_text = re.sub(r'[0-9\s\.]+', '', text)
    cleaned_text_upper = cleaned_text.upper()

    # 检查清理后的文本是否是字典的一个键
    for key in task_dic.keys():
        if key in cleaned_text_upper:
            # 如果是，返回对应的值
            return task_dic[key]

    else:
        return task_dic["others"]


def extract_after_first_key(structurized_content):
    new_dict = {}
    skip_first = True
    for key, value in structurized_content.items():
        if skip_first:
            skip_first = False
            continue
        new_dict[key] = value
    return new_dict


def remove_references(results):
    if 'REFERENCES' in results:
        del results['REFERENCES']
    return results


def Struxtured_extraction(pdf_path, temp_path, details):
    texts, counts, fonts = extract_text_and_fonts_by_page(pdf_path)
    full_pdf_text = ''.join(f'{key}{value}' for key, value in texts.items())
    # 合并fonts，把value抽取出来作为一个列表
    combined_fonts = []
    for value in fonts.values():
        combined_fonts.extend(value)
    main_text_style, titles_fonts = find_main_and_titles_fonts(fonts)
    main_text_size = main_text_style[1]  # 正文字体大小
    titles_by_fonts = extract_titles_from_full_text(titles_fonts, full_pdf_text, combined_fonts)
    titles_by_re = find_section_headings(full_pdf_text)
    titles_from_full_text = list(set(titles_by_fonts).union(set(titles_by_re)))
    titles_from_full_text = clean_list(titles_from_full_text)
    print(titles_from_full_text)

    agent1 = Extract_Analysis_Agent(model="gpt-4-0125-preview")
    agent2 = Extract_Analysis_Agent(model="moonshot-v1-128k")

    response = agent1.Extract(titles_from_full_text)
    print("LLM找到的title：" + response)

    def remove_output_tag(response):
        if " [output]" in response:
            # 使用分割和连接的方法来移除"[output]"及其空格
            return " ".join(response.split(" [output] "))
        else:
            # 如果没有找到，返回原始response
            return response

    text_within_brackets = remove_output_tag(response)
    # 使用字符串的find()方法查找第二个中括号的位置
    # start_index = response.find('[', 1)  # 从第二个字符开始查找中括号
    # end_index = response.find(']', start_index)  # 从start_index之后查找闭合的中括号
    # 提取中括号内的文本
    # text_within_brackets = response[start_index + 1:end_index]

    extracted_list = ast.literal_eval(text_within_brackets)
    extracted_list = clean_list_elements(extracted_list)
    print("清洗过一次的title：" + ":".join(extracted_list))
    structurized_content = titles_match_fulltext(extracted_list, full_pdf_text)
    structurized_content = remove_spaces_and_uppercase_keys(structurized_content)
    abstract_text = structurized_content['ABSTRACT']
    abstract = agent1.Extract_abstract(abstract_text)
    structurized_content['ABSTRACT'] = abstract
    if 'ABSTRACT' in structurized_content:
        # 将 ABSTRACT 键值对从字典中移除
        abstract_value = structurized_content.pop('ABSTRACT')

        # 创建一个新字典，将 ABSTRACT 作为第一个键值对插入
        structurized_content = {'ABSTRACT': abstract_value, **structurized_content}

    print("提取到结果字典的title：" + ":".join(structurized_content.keys()))

    # 将结果传入json保存
    with open(temp_path, 'w', encoding='utf-8') as json_file:
        json.dump(structurized_content, json_file, ensure_ascii=False, indent=4)

    # 已经完成对PDF的提取

    total = extract_values_as_text(structurized_content)
    background = agent2.GeneralBackground(total)
    new_concept = agent1.New_concept(background, structurized_content["ABSTRACT"])
    results = {"Concept": new_concept, "ABSTRACT": abstract}

    prompts_list = []
    format_list = []
    structurized_content_no_abstract = extract_after_first_key(structurized_content)

    for key in structurized_content_no_abstract.keys():
        # 调用 get_value_by_text_or_others 方法获取值
        if details == 0:
            task = get_task_by_title_easy(key, task_dic)
        else:
            task = get_task_by_title(key, task_dic)
        # 将结果存储在 results 字典中
        prompts_list.append(Analysis_Model_Prompt_English)
        format_list.append([background, task, structurized_content[key]])
    print("prompt已准备好")

    results_list = agent2.Multi_Response(prompts_list,format_list)
    for key,result in zip(structurized_content_no_abstract.keys(),results_list):
        results[key] = result

    first_key, first_value = next(iter(results.items()))
    # 从原字典中删除第一个键值对
    del results[first_key]
    # 将第一个键值对添加到字典的最后
    results[first_key] = first_value
    # 删除对参考文献的分析
    results = remove_references(results)

    print("Paper已分析完毕")
    return results


if __name__ == '__main__':
    pass

