#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : MatchImages.py
# @Software: PyCharm


from Configration import config
from Agents.MatchImageAgent import MatchImageAgent
from docx import Document
import re
from pathlib import Path
from docx.shared import Mm
from PIL import Image
from utils.Translate import translate
import json
from docx.shared import Mm, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def Text2Doc(text,image,save_path):
    # 创建一个新的 Word 文档对象
    doc = Document()
    # 按行分割文本内容
    lines = text.split('\n')
    # 逐行处理文本内容
    for line in lines:
        pattern = r"<(\d)>"
        index = re.search(pattern, line)
        if index:
            # 如果行中包含 <index> 标记，则插入图片
            index = index.group(1)
            image_path = Find_image_by_number(image,index)
            if image_path is not None:
                #缩放大小
                # A4纸张宽度减去两边边距（以毫米为单位）
                # 这里我们假设左右边距总和为50.8mm，以留出一定的边距
                usable_width_mm = 210 - 63.6
                # 使用Pillow来获取图片尺寸
                with Image.open(str(image_path)) as img:
                    original_width, original_height = img.size
                    dpi = img.info.get('dpi', (300, 300))
                # 计算图片应该缩放到的宽度和高度，保持原始宽高比
                # 假设图片需要完全缩放到可用宽度
                scale_factor = usable_width_mm / (original_width / dpi[0] * 25.4)
                new_height_mm = original_height / dpi[1] * 25.4 * scale_factor
                #添加
                doc.add_picture(str(image_path),width=Mm(usable_width_mm), height=Mm(new_height_mm))
        else:
            # 否则将文本行添加到文档中
            para = doc.add_paragraph()
            Set_chinese_font(para, font_name='宋体', font_size=12)
            para.add_run(line)
    doc.save(save_path)

def Find_image_by_number(image_folder, target_number):
    """
    在指定文件夹中查找文件名以特定数字结尾的图片。
    :param image_folder: 存储图片的文件夹路径
    :param target_number: 要查找的目标数字
    :return: 匹配的图片文件路径
    """
    # 编译正则表达式，匹配类似于"page_0_image_1.png"格式的文件名中的最后一个数字
    pattern = re.compile(r"page_\d+_image_(\d+)\.png$")
    # 使用Path遍历文件夹中的所有png文件
    for image_path in Path(image_folder).glob("*.png"):
        match = pattern.search(str(image_path.name))
        if match and match.group(1) == str(target_number):
            # 找到匹配的文件，返回路径
            return image_path
    return None

def Method_Delete_Repeat(text,reverse = False):
    # 从文本中反向查找并删除重复的<number>
    if (reverse):
        matches = re.findall(r'<(\d+)>', text)
        seen = set()
        result = text
        for match in reversed(matches):
            if match in seen:
                # 构建正则表达式来删除重复项，只删除具体的这个<number>
                pattern = r'(\<' + match + r'\>)'
                # 保证只替换最后一次出现的模式
                result = re.sub(pattern, '', result, count=1)
            else:
                seen.add(match)
    else:
        #正向删除
        matches = re.finditer(r'(<(\d+)>)', text)
        seen = set()
        # 文本作为列表处理，以便进行删除操作
        result = list(text)
        for match in matches:
            full_match = match.group(1)
            number = match.group(2)
            if number in seen:
                # 如果数字已经出现过，将其从结果中删除,将要删除的区间设置为None
                result[match.start():match.end()] = [None] * (match.end() - match.start())
            else:
                seen.add(number)
        # 从结果中去除所有None，然后将列表转换回字符串
        result = ''.join([char for char in result if char is not None])
    return result


def format_json_string(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 遍历字典，构建字符串
    formatted_str = ''
    for key, value in data.items():
        # 如果值是字符串，直接添加；否则，转换为字符串
        value_str = str(value)
        formatted_str += f'{key}\n:{value_str}\n'

    return formatted_str

def MatchImage(text, image_info, image_path, store_path, model="gpt-4-32k", insert_image=True, reference=True, trans=True):
    Match_Image = MatchImageAgent(model=model)
    # 使用Path对象,获取上一级目录
    path = Path(text)
    parent_directory = path.parent

    #开始插入,整体插入，启用多线程
    if insert_image:
        result = Select_topics(text,json_mode=True)
        #response = Match_Image.Match(result,image_info)
        response = Match_Image.Match_Multi(result, image_info)
        # 添加丢失部分
        response = Add_Cut(text, response)
        response = '\n' + response
        # 删除多余图片符号
        response = Method_Delete_Repeat(response, reverse=True)
        print(parent_directory)
        with open(str(parent_directory) + "/images_insert.txt", 'w',encoding="utf-8") as temp_file:
            temp_file.write(response)
        print("Match Step 1 Insert OK!")
        #-----------------------------------------
        #response = Match_Image.Optimal(response)
        #response = Match_Image.Optimal_Multi(response)
        print("Match Step 2 Optimal OK!")


    else:
        response = Select_topics(text, all=True)
        with open(str(parent_directory) + "/images_insert.txt", 'w',encoding="utf-8") as temp_file:
            temp_file.write(response)

    # 翻译
    if trans:
        images_insert_txt_path = str(parent_directory) + "/images_insert.txt"
        images_insert_json_path = str(parent_directory) + "/images_insert.json"
        image_tag = r"<(\d+)>"
        result_cn = translate(text, images_insert_txt_path, images_insert_json_path, image_tag)
        with open(str(parent_directory) + "/images_insert_cn.json", 'w', encoding="utf-8") as json_file:
            json.dump(result_cn, json_file, ensure_ascii=False, indent=4)
        response = format_json_string(str(parent_directory)+ "/images_insert_cn.json")

    # 拼接reference
    if reference:
        if os.path.exists(str(parent_directory) + "/Reference.json"):
            # with open(os.path.join(parent_directory, "Reference.json"), 'r', encoding="utf-8") as reference_file:
            #     reference = reference_file.read()
            # full_text = response + "\n" + reference
            with open(str(parent_directory) + "/Reference.json", 'r', encoding='utf-8') as file:
                references = json.load(file)
            if trans:
                response_cn = format_json_string(str(parent_directory) + "/images_insert_cn.json")
                full_text = response_cn + "\n推荐论文\n" + references["Paper Recommend"]
            else:
                full_text = response + "\nPaper Recommend\n" + references["Paper Recommend"]
        else:
            full_text = response
    else:
        full_text = response

    with open(str(parent_directory) + "/images_insert_optimal.txt", 'w',encoding="utf-8") as file:
        file.write(full_text)
    Text2Doc(full_text,image_path,store_path)
    print("Save at {}".format(store_path))

def Select_topics(text,all = False,json_mode = False):
    with open(text, 'r', encoding='utf-8') as file:
        all_text = json.load(file)
    temp = []
    for item, value in all_text.items():
        if json_mode:
            temp.append({item:value})
        else:
            temp.append(item + "\n" + value)
    if all:
        if json_mode:
            result = {}
            for i in temp:
                result.update(i)
        else:
            result = '\n'.join(temp)
    else:
        # 筛选出需要的主题
        exclude_indices = [0, len(temp) - 2, len(temp) - 1]
        include_list = [temp[i] for i in range(len(temp)) if i not in exclude_indices]
        if json_mode:
            result = {}
            for i in include_list:
                result.update(i)
        else:
            result = '\n'.join(include_list)
    return result

def Add_Cut(text,part):
    with open(text, 'r', encoding='utf-8') as file:
        all_text = json.load(file)
    temp = []
    for item, value in all_text.items():
        temp.append(item + "\n" + value)
    result = temp[0] + "\n" + part + "\n" + temp[len(temp) - 2] + "\n" + temp[len(temp) - 1]
    return result

def Set_chinese_font(paragraph, font_name='微软雅黑', font_size=12):
    run = paragraph.add_run()
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)

if __name__ == "__main__":
    import os
    os.environ['OPENAI_API_KEY'] = config["openai_key"]
    os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]
    image_path = config["test_image_store"]

    image_info = r"C:\Users\pp\Desktop\PaperRecommend\PaperRecommend\output\大语言模型改进文本嵌入-Improving Text Embeddings with Large Language Models\images_informatin.json"
    text = r"C:\Users\pp\Desktop\PaperRecommend\PaperRecommend\output\大语言模型改进文本嵌入-Improving Text Embeddings with Large Language Models\text.txt"

    #Match_Image = MatchImageAgent()
    # response = Match_Image.Match()
    # Match_Image.Optimal(response)


    #Text2Doc("test.txt",image_path)
    store_path = "result_eee.docx"
    #MatchImage(text,image_info,image_path,store_path,model="moonshot-v1-128k")


    test = '''
    {' ABSTRACT ': '基于Transformer的模型的巨大成功得益于强大的多头自注意机制，该机制学习令牌依赖性并从输入中编码上下文信息。先前的工作试图将模型决策归因于具有不同显著性度量的单个输入特征，但未能解释这些输入特征如何相互作用以实现预测。在本文中，我们提出了一种自注意归因方法来解释Transformer内部的信息交互。\n<1>\n我们以BERT为例进行了广泛的研究。首先，我们应用自注意归因来识别重要的注意头，而其他注意头可以通过边际性能退化来修剪。\n<3>\n此外，我们提取每一层中最显著的依赖项来构建属性树，从而揭示Transformer内部的分层交互。最后，我们证明了归因结果可以作为对抗性模式来实现对BERT的非目标攻击。\n', 'INTRODUCTION': '本文介绍了一种自注意归因方法（ATTATTR）来解释Transformer模型的内部工作，特别是BERT。作者旨在解决解释自我注意机制的挑战，并揭示输入词与网络组成结构之间的信息交互。\n', '3METHODS:SELF-ATTENTIONATTRIBUTION': '本文提出了一种自注意归因方法（ATTATTR），用于解释Transformer模型中的信息交互，特别是以BERT为例。该框架模型旨在解决在Transformer模型中理解单词如何相互作用的挑战，因为注意力得分矩阵相当密集，并且大的注意力得分不一定表明单词对对对模型决策的重要性。\n', '2BACKGROUND': '本文提出了一种新的自注意归因方法ATTATTR，以BERT为例，旨在解释Transformer模型中的信息交互。该方法确定了可以在对性能影响最小的情况下修剪的关键注意力头，并构建了一个归因树来揭示分层交互。这种方法不仅增强了自注意机制的可解释性，而且在其他变压器网络中也有潜在的应用，只需稍作修改。\n', '4EXPERIMENTS': '本文以BERT为例，对自注意归因方法（ATTATTR）在Transformer模型中解释信息交互进行了实验研究。作者在他们的实验中使用了BERT基础，在四个下游分类数据集上对其进行了微调：MNLI、RTE、SST-2和MRPC。通过定量分析、注意力头部修剪、可视化信息流和对抗性攻击实验，分析了ATTATTR的有效性。\n', '5RELATEDWORK': '现有的关于神经模型可解释性的研究可以分为几类。其中一类侧重于使用各种显著性度量将预测归因于输入特征，如DeepLift、分层相关性传播和综合梯度。另一类研究是专门针对NLP领域的，已经开发了一些方法来跟踪单词在LSTM模型中的重要性，并捕捉单词组合的贡献。第三类研究产生了层次解释，以揭示特征是如何组合在一起的。然而，这些方法通常检测输入令牌的连续块内的交互。\n', '6CONCLUSION': '在本文中，作者介绍了一种新的自注意归因方法ATTATTR，该方法旨在解释Transformer模型中的信息交互，特别是以BERT为例。通过定量分析，作者证明了ATTATTR在识别最重要的注意力头部方面的有效性，从而提出了一种新的头部修剪算法。该方法还构建了交互树，以可视化Transformer的信息流，从而提供对感受野的更深入理解。\n', 'ACKNOWLEDGEMENTS': '本文以BERT为例，提出了一种新的自注意归因方法（ATTATTR）来解释Transformer模型中的信息交互。该方法确定了可以在对性能影响最小的情况下修剪的关键注意力头，并构建了一个归因树来揭示分层交互。作者通过定量分析、注意力头部修剪、可视化信息流和对抗性攻击实验证明了他们的方法的有效性。\n', 'REFERENCES': '本文以BERT为例，提出了一种新的自注意归因方法（ATTATTR），提高了Transformer模型中自注意机制的可解释性。该方法确定了可以在对性能影响最小的情况下修剪的关键注意力头，并构建了一个归因树来揭示分层交互。作者通过定量分析、注意力头部修剪、可视化信息流和对抗性攻击实验证明了他们的方法的有效性。\n', 'Concept': '自注意-归因方法（ATTATTR）：这是一种新颖的技术，旨在通过识别可以在最小性能损失的情况下修剪的关键注意力头，并构建归因树来揭示分层交互，来解释变换器模型（如BERT）中的信息交互。\n'}
    '''
    Text2Doc(test,image_path)
