#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from pdfminer.high_level import extract_pages,extract_text
import re
import json
import regex
from Configration import config

def Find_Description(index,text = None, pdf_path = None):
    '''
    :param index: image index
    :param text:
    :param pdf_path:
    :return: [Description,...]
    '''
    if text is None and pdf_path is None:
        print("No text input")
        raise Exception
    if pdf_path is not None:
        text =extract_text(pdf_path)
    # 使用正则表达式筛选出符合条件的文字
    pattern = r'Figure {}.(.*?)\n\n'.format(index)
    matches = re.findall(pattern, text, re.DOTALL)
    temp = []
    #处理配的字符串
    if len(matches) > 0:
        for match in matches:
            temp.append(match)
    return temp


#获取一个文件夹中所有图片的page与index，返回列表
#page_0_image_1.png这种文件名格式
def Get_Images_index(file_path):
    '''
    :param file_path: file name with images cut from one pdf
    :return: [[page,index],...]
    '''
    image_index_list = []
    if os.path.exists(file_path):
        file_list = os.listdir(file_path)
    else:
        file_list = []
    if(len(file_list) > 0):
        # 正则表达式模式
        pattern = r"page_(\d+)_image_(\d+)\.png"
        for file in file_list:
            # 使用正则表达式进行匹配
            match = re.match(pattern, file)
            if match:
                page_index = int(match.group(1))
                image_index = int(match.group(2))
                image_index_list.append([page_index,image_index])
    return image_index_list

def Find_Correlation(index,text = None, pdf_path = None):
    '''
    :param index: image index
    :param text:
    :param pdf_path:
    :return: [relation_information,...] string list
    '''
    if text is None and pdf_path is None:
        print("No text input")
        raise Exception
    if pdf_path is not None:
        text =extract_text(pdf_path)
    # 使用正则表达式筛选出符合条件的文字
    pattern = r"(?:\n\n|^)(.*?\(Fig\. {}.*?)(?=\n\n)".format(index)
    matches = re.findall(pattern, text, re.DOTALL)
    #反向删除多余正则式
    reverse_pattern = r'(?<=\n\n)(.*?\(Fig\. {}.*?)(?=\n\n|$)'.format(index)
    temp = []
    if len(matches) > 0:
        for match in matches:
            if "\n\n" in match:
                # 反向删除多余
                result = regex.findall(reverse_pattern, match, regex.DOTALL | regex.REVERSE)
            else:
                result = [match]
            temp.append(result[0])
    return temp


def Find_Image_Information(pdf_path,images_path,store_path=None,handel = True):
    if not (os.path.exists(pdf_path) and os.path.exists(images_path)):
        print("file not exist")
        raise Exception
    else:
        text = extract_text(pdf_path)
        index = Get_Images_index(images_path)
        data = {}
        #找相关联描述
        for image_index in index:
            description = Find_Description(image_index[1],text)
            correlation = Find_Correlation(image_index[1],text)
            # 处理匹配的字符串
            if (len(description) > 0 or len(correlation) > 0):
                if handel:
                    if len(description):
                        for item_index, item in enumerate(description):
                            description[item_index] = description[item_index].strip()     #去除两边空白字符
                            description[item_index] = description[item_index].replace('\n', '')   #替换\n
                    if len(correlation):
                        for item_index, item in enumerate(correlation):
                            correlation[item_index] = correlation[item_index].strip()
                            correlation[item_index] = correlation[item_index].replace('\n', '')
                data[image_index[1]] = {
                    "description":description,
                    "correlation":correlation
                }

        #保存
        file = r'images_information.json'
        if store_path is not None:
            # 获取文件名,去除扩展名
            filename = os.path.splitext(os.path.basename(pdf_path))[0]
            # 移除路径中可能导致问题的特殊字符
            filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
            filename = filename.rstrip(". ")  # 移除末尾的点和空格

            if not os.path.exists(store_path + "/" + filename):
                os.makedirs(store_path + "/" + filename)
            output_file = store_path + "/" + filename + "/" +  file
        else:
            output_file = "./"

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        return True




#获取元素类别
def Get_items(pdf_path):
    '''
    :param pdf_path:
    :return: set of items in pdf
    '''
    items = set()
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        for element in page:
            items.add(type(element).__name__)
    return set(items)


if __name__ == "__main__":
    # items = Get_items(file)    #{'LTFigure', 'LTLine', 'LTTextBoxHorizontal', 'LTTextLineHorizontal'}
    '''
    英文
        (Fig. 7)
        Figure 2.
    '''


    dic_path = config["test_image_store"]
    file = config["test_pdf"]
    store_file = config["out_file"]


    Find_Image_Information(file,dic_path,store_file)






