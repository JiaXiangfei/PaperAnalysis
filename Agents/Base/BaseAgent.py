#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: YS
CreatedDate: 2023/12/12
Path:
Description: 
'''



from openai import embeddings
import json
from openai import OpenAI
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from functools import partial
from Configration import config

class BaseAgent():
    def __init__(self,model="gpt-3.5-turbo-1106",temperature = 0,mode = None,verbal = False):
        self.model = OpenAI()
        self.model_type = model
        self.temperature = temperature
        self.format = {"type": "json_object"} if mode == "json" else None
        self.__total_token = 0
        self.__present_token = 0
        self.__history = []
        self.__prompt = []
        self.__static = []
        self.__verbal = verbal
        self.__init()
        self.__lock = threading.Lock()
        self.__lock_token = threading.Lock()


    def Response(self,*chat,role = "user"):
        message = []
        if(len(self.__static) > 0):
            message += self.__static
        if(len(self.__prompt) > 0):
            message += self.__prompt
        if(len(self.__history) > 0):
            message += self.__history
        if(len(chat) > 0):
            message += [self.ChangeForm(chat[0],role)]

        response = self.model.chat.completions.create(
            model=self.model_type,
            temperature=self.temperature,
            response_format=self.format,
            messages=message
            )
        with self.__lock_token:
            self.__total_token += response.usage.total_tokens
        self.__present_token = response.usage.total_tokens
        if self.__verbal:
            print(response.choices[0].message.content)
        return response.choices[0].message.content
        #return response.choices[0]

    def run(self,*var,role = "user"):
        if(len(var) > 0):
            chat = var[0]
        else:
            chat = input("Please input:")
        self.__history.append(self.ChangeForm(chat,role))
        response = self.Response(chat)
        self.__history.append(self.ChangeForm(response,"assistant"))
        return response


    def Load_Prompt(self,prompt,*var,role = "user"):
        temp = prompt
        prompt_type = type(prompt)
        if (prompt_type == dict):
            if (len(var) > 0):
                if (type(var[0]) == list):
                    if (len(var[0]) == 1):
                        temp["content"] = prompt["content"].format(var[0][0])
                    else:
                        temp["content"] = prompt["content"].format(*var[0])
                if (type(var[0]) == dict):
                    temp["content"] = prompt["content"].format(**var[0])
                if (type(var[0]) == str):
                    temp["content"] = prompt["content"].format(var[0])
            with self.__lock:
                self.__prompt = [temp]
        if (prompt_type == str):
            if (len(var) > 0):
                if (type(var[0]) == list):
                    if (len(var[0]) == 1):
                        temp = prompt.format(var[0][0])
                    else:
                        temp = prompt.format(*var[0])
                if (type(var[0]) == dict):
                    temp = prompt.format(**var[0])
                if (type(var[0]) == str):
                    temp = prompt.format(var[0])
            with self.__lock:
                self.__prompt = [self.ChangeForm(temp,role)]
        #print(temp)

    def Multi_Response(self,prompts_list:list,formats_list:list,max_workers = 10,role = "system"):
        '''
        :param func_list: 可多线程执行的会话列表
        :param parameters_list: 各个prompts的format参数
        :param max_workers: 最大线程数
        :return: 各个结果组合的列表形式
        '''
        responses = []
        #检查参数
        if len(prompts_list) == 0 | len(formats_list) == 0 | len(prompts_list) != len(formats_list):
            print("Threading prompts or formats error")
        else:
            # 使用线程池执行并行请求,使用 ThreadPoolExecutor 管理多线程
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                # 向线程池提交任务
                for prompt,parameters in zip(prompts_list,formats_list):
                    # 使用 functools.partial 部分应用函数参数
                    thread_func = partial(self.__Single_Response, prompt,parameters,role = role)
                    single_future = executor.submit(thread_func)
                    futures.append(single_future)
                # 使用 wait 函数等待所有任务完成
                done, _ = wait(futures)
                for future in futures:
                    response = future.result()
                    responses.append(response)
        return responses

    def Full_Prompt(self,prompt,*var):
        temp = prompt
        prompt_type = type(prompt)
        if (prompt_type == dict):
            if (len(var) > 0):
                temp["content"] = prompt["content"].format(*var[0])
            return temp
        if (prompt_type == str):
            if (len(var) > 0):
                temp = temp.format(*var[0])
            return temp

    def __init(self):
        if self.format != None:
            self.__static.append({"role": "system", "content": "You are a helpful assistant designed to strictly output JSON."})



    def ChangeForm(self,info,role = "user"):
        return {"role":role,"content":info}

    def __Single_Response(self,prompt,parameters,role = "user"):
        self.Load_Prompt(prompt,parameters,role)
        response = self.Response()
        return response

    def Emembedding(self,input,model = "text-embedding-ada-002"):
        response = self.model.embeddings.create(
            input=input,
            model=model
        )
        self.__total_token += response.usage.total_tokens
        return response.data[0].embedding
        #return response

    def __CheckError(self,input):
        pass

    def AddMessage(self,info,role = "user"):
        self.__history.append({"role":role,"content":info})


    def Save_Hisrtoy(self):
        pass

    def Clear(self):
        self.__history.clear()


    def ResetPara(self,model="gpt-3.5-turbo-1106",temperature = 0,mode = None):
        pass

    def AddHistory(self,history):
        self.__history += history

    def ExportHistory(self):
        return self.__history

    def ExportMessage(self,message,role = "user"):
        return self.ChangeForm(message,role)

    def Total_Token(self):
        return self.__total_token

    def Present_Token(self):
        return self.__present_token


    def AllPrompt(self):
        print(self.__static)
        print(self.__prompt)
        print(self.__history)

    def Info(self):
        print("Total tokens:",self.__total_token)
        print("Present tokens:" , self.__present_token)






if __name__ == '__main__':
    import os
    os.environ['OPENAI_API_KEY'] = config["openai_key"]
    os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]

    temp = {"role": "user", "content": "HI"}
    #temp =  {"role": "user","content": "请帮我写个代码，要求给出斐波那契数列的第八个质数 "}
    test = BaseAgent(model="moonshot-v1-128k",verbal=True)
    #test.Load_Prompt("hi{}",["ss","sssssssss"])
    a = test.Response("Hi!")
    #test.AddMessage(a,"assistant")
    test.Info()
    #test.AllPrompt()
