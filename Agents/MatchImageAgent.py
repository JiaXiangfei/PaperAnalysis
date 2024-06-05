#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Software: PyCharm


from Agents.Base.BaseAgent import BaseAgent
from Configration import config
from utils.Prompts import Add_Images_Prompt_English,Optimal_Prompt_English,Add_Images_Muitl_Prompt_English,Optimal_Multi_Prompt_English
import json
from concurrent.futures import ThreadPoolExecutor, wait
from functools import partial


class MatchImageAgent(BaseAgent):
    def __int__(self,model="gpt-3.5-turbo-1106",temperature = 0,mode = None,verbal = False):
        super().__init__(model,temperature,mode,verbal)
        self.template = Add_Images_Prompt_English

    def GetImageInfo(self,info):
        if isinstance(info,str):
            with open(info, 'r') as file:
                data = json.load(file)
        if isinstance(info, dict):
            data = info
        temp = ''
        for item in data:
            describe_list = data[item]["description"]
            relation_list = data[item]["correlation"]
            temp += "Figure {} information:\n".format(item)
            if len(describe_list) > 0:
                for describe_item in describe_list:
                    temp += "Description:{}\n".format(describe_item)
            if len(relation_list) > 0:
                for relation_item in relation_list:
                    temp += "Correlation:{}\n".format(relation_item)
        temp += "\n"
        return temp
    def Match(self,text,info):
        #开始匹配
        image_info  = self.GetImageInfo(info)
        self.Load_Prompt(Add_Images_Prompt_English, [image_info,text],role = "system")
        response = self.Response()
        return response

    def Optimal(self,text):
        self.Load_Prompt(Optimal_Prompt_English, [text],role = "system")
        response = self.Response()
        return response

    def Match_Multi(self,text,info,max_workers = 10):
        #读取文本
        if isinstance(text,str):
            with open(text, 'r',encoding="utf-8") as file:
                data = json.load(file)
        if isinstance(text, dict):
            data = text
        part_text = []
        for key in data:
            part_text.append(data[key])
        #获取图片信息
        image_info  = self.GetImageInfo(info)

        # 使用线程池执行并行请求
        responses = ""
        # 使用 ThreadPoolExecutor 管理多线程
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            # 向线程池提交任务
            for part in part_text:
                # 使用 functools.partial 部分应用函数参数
                thread_func = partial(self.__Match_Single, part,image_info)
                single_future = executor.submit(thread_func)
                futures.append(single_future)
            # 使用 wait 函数等待所有任务完成
            done, _ = wait(futures)
            for future, key in zip(futures,data):
                response = future.result()
                responses += "\n" + key + "\n" + response
        return responses

    def __Match_Single(self, text, info):
        self.Load_Prompt(Add_Images_Muitl_Prompt_English, [info,text],role = "system")
        response = self.Response()
        return response

    def Optimal_Multi(self,text):
        self.Load_Prompt(Optimal_Multi_Prompt_English, [text], role = "system")
        response = self.Response()
        return response

if __name__ == "__main__":
    import os
    os.environ['OPENAI_API_KEY'] = config["openai_key"]
    os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]

    text = r"C:\Users\pp\Desktop\PaperRecommend\PaperRecommend\output\大语言模型改进文本嵌入-Improving Text Embeddings with Large Language Models\text_parts.json"
    image_info = r"C:\Users\pp\Desktop\PaperRecommend\PaperRecommend\output\大语言模型改进文本嵌入-Improving Text Embeddings with Large Language Models\images_informatin.json"

    #Match_Image = MatchImageAgent(model="claude-3-opus-20240229")
    Match_Image = MatchImageAgent(model="gpt-4-turbo")
    #response = Match_Image.Match(text,image_info)
    #optimal = Match_Image.Optimal(response)
    #response = Match_Image.Match_Multi(text, image_info)


    test_optimal = r"C:\Users\pp\Desktop\PaperRecommend\PaperRecommend\output\大语言模型改进文本嵌入-Improving Text Embeddings with Large Language Models\images_insert.txt"
    with open(test_optimal,'r', encoding="utf-8") as temp_file:
        test_optimal_txt = temp_file.read()
    response = Match_Image.Optimal_Multi(test_optimal_txt)



