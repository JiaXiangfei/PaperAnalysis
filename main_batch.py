#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ys
# @File    : main_batch.py
# @Software: PyCharm

from utils.pdfImagesInfo import Find_Image_Information
from utils.MatchImages import MatchImage
from utils.pdfGetImage import Get_Image
from utils.CalculateRank3 import Get_Reccomend
from utils.ExtractRef import Extract_Reference
from utils.Structured_extraction import Struxtured_extraction
import os
import re
import json
from Configration import config

def Insert_Images(pdf_path,middle_path,result_path = "./",model = "gpt-4-32k"):
    # 获取文件名,去除扩展名
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # 移除路径中可能导致问题的特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
    filename = filename.rstrip(". ")  # 移除末尾的点和空格
    store_path = os.path.join(result_path ,"result_{}.docx".format(filename))
    text_path = os.path.join(middle_path, filename,"text_parts.json")
    images_path = os.path.join(middle_path, filename, "images")
    images_information_path = os.path.join(middle_path, filename, "images_informatin.json")
    try:
        Get_Image(pdf_path,middle_path)
        print("Find Images OK!")
        Find_Image_Information(pdf_path, images_path, middle_path)
        print("Find Images information OK!")
        MatchImage(text_path,images_information_path,images_path,store_path,model=model)
        print("Match Images OK!")

    except Exception as e:
        print(e)
        return False
    else:
        return True
def Extract_rec(pdf_path,middle_path):
    # 获取文件名,去除扩展名
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # 移除路径中可能导致问题的特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
    filename = filename.rstrip(". ")  # 移除末尾的点和空格
    text_path = os.path.join(middle_path, filename, "text_parts.json")
    ref_path = os.path.join(middle_path, filename, "Reference.txt")
    referencesL = Extract_Reference(text_path)
    Get_Reccomend(text_path, ref_path,referencesL)

def Extract(pdf_path,out_file):
    #创建文件
    # 获取文件名,去除扩展名
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # 移除路径中可能导致问题的特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
    filename = filename.rstrip(". ")  # 移除末尾的点和空格
    if not os.path.exists(os.path.join(out_file, filename)):
        os.makedirs(os.path.join(out_file, filename))
    output_file_path_txt = os.path.join(out_file, filename, "text.txt")
    output_file_path_json = os.path.join(out_file, filename, "text_parts.json")
    output_origin_file_path_json = os.path.join(out_file, filename, "original_parts.json")

    results = Struxtured_extraction(pdf_path,output_origin_file_path_json)
    # 将文件输出到txt中
    # 打开文件进行写入操作
    with open(output_file_path_txt, 'w', encoding='utf-8') as file:
        # 遍历字典的项
        for key, value in results.items():
            # 写入键，然后换行
            file.write(key + '\n')
            # 写入值，然后换行
            file.write(value + '\n')

    # 将结果传入json保存
    with open(output_file_path_json, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)



def Batch_Process(folder_path,middle_path,result_path = "./",model =  "gpt-4-32k"):
    '''
    :param folder_path: pdf存储文件夹
    :param middle_path: 中间文件存储文件夹
    :param result_path: 存储结果地址
    :param model: 使用的模型
    :return:
    '''
    if os.path.exists(folder_path):
        # 列出文件夹中的所有文件
        all_files = os.listdir(folder_path)
        # 过滤出所有PDF
        pdf_files = [file for file in all_files if file.endswith('.pdf')]
        if len(pdf_files) > 0:
            print(f"Total {len(pdf_files)} pdf files!")
            for index,pdf_file in enumerate(pdf_files):
                print(f"File {index + 1} : {pdf_file}\nStart to analyse!")
                pdf_file_path = os.path.join(folder_path, pdf_file)
                #####################执行操作


                Extract(pdf_file_path, middle_path)
                Extract_rec(pdf_file_path, middle_path)
                Insert_Images(pdf_file_path, middle_path, result_path, model)


                print(f"File {index}'s analysis has finished!\n========================================")
            print(f"All files have analysed!")
        else:
            print("Empty File")
    else:
        print("File doesn't exist!")



if __name__ == "__main__":
    os.environ['OPENAI_API_KEY'] = config["openai_key"]
    os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]
    middle_path = config["out_file"]
    Batch_Process("./data",middle_path)
