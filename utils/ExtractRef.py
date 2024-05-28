import re
import os
import json

def extract_references_content(structurized_content):
    # 将字典键转换为列表并全部转换为小写，以便寻找索引
    keys_list = list(structurized_content.keys())
    lower_keys_list = [key.lower() for key in keys_list]

    # 尝试找到 'references' 的索引（忽略大小写），若找不到，则返回错误信息
    try:
        ref_index = lower_keys_list.index('references')
    except ValueError:
        print("字典中未找到 'References' 键（忽略大小写）。")
        return
    # 提取 'References'（忽略大小写）及其前后键的内容
    merged_content = ""
    start_index = max(0, ref_index - 1)  # 从References前1个键
    end_index = min(ref_index + 2, len(keys_list))  # 到References后2个键
    for i in range(start_index, end_index):
        merged_content += f"{keys_list[i]}:\n{structurized_content[keys_list[i]]}\n\n"
    return merged_content

def Get_references_content(text):
    text_list = text.split('\n')

    clean_pattern = r'[\t\n\r\f\v\b]'
    list_cleaned = [re.sub(clean_pattern, '', item) for item in text_list]  # 清洗字符串中的特殊符号
    list_cleaned = [s for s in list_cleaned if any(c.isalpha() for c in s)]  # 删掉全是数字的字符串

    # 处理列表，合并非以'[]'开头的元素
    merged_lst = []
    current_item = ''
    for item in list_cleaned:
        if item.startswith('['):
            # 如果当前元素以'['开头，则将其添加到结果列表（如果当前项不为空）
            if current_item:
                merged_lst.append(current_item)
            # 设置当前元素为当前项
            current_item = item
        else:
            # 如果当前元素不以'['开头，则将其添加到当前项
            current_item += ' ' + item
    # 如果列表中有最后一个未添加的元素，将其添加到结果列表
    if current_item:
        merged_lst.append(current_item)

    pattern_ref = r'\[\d+\] [A-Za-z]'
    references_re = [item for item in merged_lst if re.match(pattern_ref, item) and len(item) < 300]

    # 准备一个空列表来存放结果
    referencesL = []
    # 正则表达式匹配[number] title
    pattern_ref2 = r'\[(\d+)\]\s*(.*)'
    # 遍历列表中的每个字符串
    for entry in references_re:
        match = re.search(pattern_ref2, entry)
        if match:
            # 如果找到匹配项，则提取编号和标题
            number = match.group(1)
            title = match.group(2)
            # 创建字典并添加到结果列表
            referencesL.append({'number': number, 'title': title})

    return referencesL

def ReGetreferences(referencesL,structured_text):

    # 判断是否有缺失的项
    a = []
    for ref in referencesL:
        a.append(int(ref['number']))
    a.sort()
    # 准备一个空列表来存放所有缺失的数字
    missing_numbers = []
    # 首先检查列表中的第一个数字是否为1
    start = 1
    if a[0] > 1:
        missing_numbers.extend(range(start, a[0]))
    # 遍历列表中的数字（除了最后一个，因为最后一个没有下一个数字来比较）
    for i in range(len(a) - 1):
        # 检查当前数字和下一个数字之间是否缺失
        if a[i] + 1 != a[i + 1]:
            # 收集所有缺失的数字
            missing_numbers.extend(range(a[i] + 1, a[i + 1]))

    #
    # if not missing_numbers:#如果没有确实
    #     return None
    S = extract_references_content(structured_text)
    numbers = missing_numbers
    # 第一步：构建正则表达式来匹配这些数字和随后的较长文本，直到可能的另一个引用或文本末尾
    # pattern = r'\[(' + '|'.join(map(str, numbers)) + r')\] (.*?)\['
    pattern = r'\[(' + '|'.join(map(str, numbers)) + r')\] ([^\[]*)'
    # 使用正则表达式找到所有大致匹配
    preliminary_matches = re.findall(pattern, S)
    # 创建最终结果列表
    final_matches = []
    # 第二步：对每个初步匹配的文本进行再处理，以找到年份和点号之前的文本
    for num, content in preliminary_matches:
        # 查找年份和点号之前的文本
        match = re.search(r'(.*?\d{4}\.)', content)
        if match:
            final_content = match.group(1)  # 包括年份和点号
            final_matches.append((num, final_content))
        else:
            # 如果没有找到年份，保留原始内容
            final_matches.append((num, content.strip()))
    # 打印最终的匹配内容
    Match = []
    for match in final_matches:
        if match:
            Match.append({'number': str(match[0]), 'title': match[1]})
        # print(f"
    return Match

def extract_reference(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")
    else:
        with open(filepath, "r", encoding='utf-8') as f:
            structured_text = json.load(f)

    text = extract_references_content(structured_text)
    referencesL = Get_references_content(text)
    #L_re = ReGetreferences(referencesL,structured_text)
    return referencesL

#计算正文出现的次数
def countReferencesPerPara(structurized_content):
    """
    :param reference_dict:
    :return: {title:{'参考文献'：出现次数}} {...,'Abstract': {'41': 1}...}
    """
    #删去references键的内容
    textdict={}
    textdict ={k: v for k, v in structurized_content.items() if 'REFERENCES' not in k.upper() and 'REFERENCE' not in k.upper()}


    ref_dict_full_text = {}
    for index, rawtext in textdict.items():
        text = rawtext.replace('\n', ' ')
        # Extracting numbers from the given text
        numbers = re.findall(r'\[[0-9, ]+\]', text)
        ref_dict_full_text[index] = numbers

    reference_counts = {}
    for title, refs in ref_dict_full_text.items():
        flat_list = [item for sublist in refs for item in sublist.replace('[', '').replace(']', '').split(', ')]
        ref_count = {}
        for ref in flat_list:
            if ref in ref_count:
                ref_count[ref] += 1
            else:
                ref_count[ref] = 1
        reference_counts[title] = ref_count
    return reference_counts

def feqscore(reference_k):
    return 2 * (1 - pow((0.5), reference_k))


def CalculateR(reference_counts):
    """
    计算每个参考文献的得分
    参数：reference_counts - 一个字典，键为标题，值为另一个字典，其中键为参考文献，值为出现次数
    返回值：ref_score_bytitle - 一个字典，键为标题，值为另一个字典，其中键为参考文献，值为得分
    """
    ref_score_bytitle = {}
    ref_count = {}  # 存储每个参考文献出现的标题数量
    ref_total_score = {}  # 存储每个参考文献的总得分

    # 遍历每个标题及其参考文献
    for title, refs in reference_counts.items():
        ref_score = {}
        for ref, frequency in refs.items():
            # 计算参考文献的得分并累加
            score = feqscore(frequency)
            ref_score[ref] = score

            # 更新参考文献出现的标题数量和总得分
            if ref in ref_count:
                ref_count[ref] += 1
                ref_total_score[ref] += score
            else:
                ref_count[ref] = 1
                ref_total_score[ref] = score

        ref_score_bytitle[title] = ref_score

    # 更新得分，加上参考文献出现的标题数量的一半
    for ref in ref_total_score:
        ref_total_score[ref] += 0.5 * ref_count[ref]

    # 为"Abstract"和"Introduction"标题中的参考文献额外加分
    for title, refs in ref_score_bytitle.items():
        if title.lower() in ["abstract", "introduction"]:
            for ref, score in refs.items():
                if ref in ref_total_score:
                    ref_total_score[ref] += 1  # 额外加1分

    # 返回按参考文献汇总的得分
    return {ref: total_score for ref, total_score in ref_total_score.items()}

def indexref(rec,referencesL):
    if referencesL is None:
        return
    for ref in referencesL:
        if ref['number'] == rec:
            return ref['title']
    return None

def Get_Reccomend(filepath, ref_path, rank=3):
    try:
        rec = GetR_inner(filepath, ref_path, rank)
        return rec
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

def GetR_inner(filepath, ref_path, rank=3):
    with open(filepath, "r", encoding='utf-8') as f:
        structurized_content = json.load(f)

    reference_counts = countReferencesPerPara(structurized_content)
    refscore = CalculateR(reference_counts)
    reclist = sorted(refscore.items(), key=lambda x: x[1], reverse=True)
    if reclist is not None and len(reclist) >= rank:
        reclist = reclist[:rank]
    referencesL = extract_reference(filepath)
    recref = []
    for rec, _ in reclist:
        str1 = indexref(rec, referencesL)
        recref.append(str1)


    ref = ""
    if recref:
        for i in range(len(recref)):
            ref += f" {i + 1} :{recref[i]}\n"
        temp = {"Paper Recommend":ref}
        # with open(ref_path, 'w', encoding='utf-8') as outputf:
        #     outputf.write(s)
        with open(ref_path, 'w', encoding='utf-8') as outputf:
            # 使用json.dump()将数据写入文件，可以选择设置缩进为美化输出
            json.dump(temp, outputf, indent=4)
    else:
        print("reclist null")


if __name__ == '__main__':
    rec = Get_Reccomend(r"..\output\resnet\original_parts.json",r"..\output\resnet\Reference.txt")
    filepath = r"..\output\resnet\original_parts.json"
    # with open(filepath, "r", encoding='utf-8') as f:
    #     structurized_content = json.load(f)
    # reference_counts = countReferencesPerPara(structurized_content)
    # for k,v in reference_counts.items():
    #     print(f'key:{k},value{v}\n')