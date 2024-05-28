#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Software: PyCharm


from Agents.Base.BaseAgent import BaseAgent
from Configration import config
from utils.Prompts import Extract_Prompt_English,GeneralBackground_Prompt_English,Analysis_Model_Prompt_English,task_dic,GenrateTask_Prompt_English, Get_abstract_prompt



class Extract_Analysis_Agent(BaseAgent):
    def __int__(self,model="gpt-3.5-turbo-1106",temperature = 0,mode = None,verbal = False):
        super().__init__(model,temperature,mode,verbal)


    def Extract(self,text):
        self.Load_Prompt(Extract_Prompt_English, [text], role = "system")
        response = self.Response()
        return response

    def Extract_abstract(self,text):
        self.Load_Prompt(Get_abstract_prompt, [text], role = "system")
        response = self.Response()
        return response


    def GeneralBackground(self,text):
        self.Load_Prompt(GeneralBackground_Prompt_English, [text], role = "system")
        response = self.Response()
        return response


    def New_concept(self,background,text):
        self.Load_Prompt(Analysis_Model_Prompt_English, [background,task_dic["ABSTRACT_CONCEPT"],text], role = "system")
        response = self.Response()
        return response


    def General_task(self,text):
        self.Load_Prompt(GenrateTask_Prompt_English, [text], role = "system")
        response = self.Response()
        return response


    def General_Analysis(self, background, task, text):
        self.Load_Prompt(Analysis_Model_Prompt_English, [background,task,text], role = "system")
        response = self.Response()
        return response





if __name__ == "__main__":
    import os
    os.environ['OPENAI_API_KEY'] = config["openai_key"]
    os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]


    Match_Image = Extract_Analysis_Agent(model="gpt-3.5-turbo")




