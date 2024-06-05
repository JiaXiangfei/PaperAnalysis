#!/usr/bin/env python
# -*- coding: utf-8 -*-


Add_Images_Prompt_Chinese = '''
任务描述：
您有一段已存在的文本和相关的图片信息描述，现在需要根据文本内容与图片信息将图片插入到适当的位置。
严格按照以下要求：
1.从给定的全部文本进行分析,使用已有文本中的语境，结合图片描述将图片插入到合适的位置。
2.确保插入位置与该图片有很强的关联性和逻辑性,最后只需要给出修改后的全部文本。
3.仅使用<图片数字编号>作为插入图片的标记，插入图片严格按照"换行符+<编号>+换行符“的格式。
4.根据文本语境决定插入图片的数量，至少需要插入一张。
5.返回的结果不要有其他任何多余的介绍词语等。
6.不要更改文本行文结构

示例：
给定文本：
这儿有种了很多花，那边还有一片宁静的湖泊。

图片信息：
图片1描述：一朵盛开的鲜花。
图片2描述：一片宁静的湖泊。
修改后的文本：
这儿有种了很多花
<1>
，那边还有一片宁静的湖泊
<2>
。


所有图片的信息：
{}

！所有图片信息到此为止！

给定的文本：
{}

！给定的文本到此为止！
'''

Add_Images_Prompt_English = '''
Task Description:
You have an existing text and related image information description, now you need to insert the image 
into the appropriate position according to the text content with the image information.
Strictly follow the rules below:
1. Analyze all the given text, use the context from the existing text, and insert the image into the 
appropriate position based on the image description and correlation.
2. Ensure that the insertion position has strong correlation and logic with the image, and finally only 
provide the modified entire text.
3. Use only the<image number>as a marker for inserting images,insert the picture strictly in the 
format of ”Line breaks + <number> + line breaks“.
4. Determine the number of images to be inserted based on the text context,at least one needs to be inserted.
5. Must return without any other extra introductory words, etc.
6. Do not change the structure of the text

Give a example:
Given text:
There are a lot of flowers planted here and a peaceful lake over there.

Information about all the pictures:
Figure 1 information:
Description: a blooming flower.
Correlation: white color
Figure 2 information:
Description: a peaceful lake.
Correlation: very big
Modified text:
There are many flowers 
<1>
planted here and a peaceful lake 
<2>
over there .

All the picture information and body text will be given below.
Information about all the pictures:
{}

!This is where all the picture information ends!

All given texts are as follows.
Given text:
{}


'''

Optimal_Prompt_Chinese = '''
任务描述：
您有一段已存在的文本，其中使用<图片数字编号>作为标记此处有图片，现在需要根据文本内容与图片插入位置将文本修改地更加通顺。

严格按照以下要求：
1.使用给定文本中的语境，不需要做太大的文章逻辑上的更改。
2.如果不需要修改，请返回原文；如果需要修改，请返回修改后的文本。
3.不要修改图片标记

给定的文本：
{}
'''

Optimal_Prompt_English = '''
Task Description:
You have an existing text which uses <image numerical number> as a markup here with an image, 
and now you need to revise the text to make it more fluent according to the text content and 
the location where the image is inserted.

Strictly follow the requirements below:
1. use the context in the given text without making too many changes in the logic of the text.
2. If you don't need to make changes, go back to the original text; if you need to make changes, 
go back to the modified text.
3. do not modify the image tags

the given text:
{}
'''

Add_Images_Muitl_Prompt_Chinese = '''
任务描述：
您有一段已存在的文本和相关的图片信息描述，现在需要根据文本内容与图片信息将图片插入到适当的位置。
严格按照以下要求：
1.从给定的全部文本进行分析,使用已有文本中的语境，结合图片描述将图片插入到合适的位置，图片插入必须要有强相关性。
2.必须返回修改后的全部文本并且不要有其他任何多余的介绍词语等。
3.仅使用<图片数字编号>作为插入图片的标记，插入图片严格按照"换行符+<编号>+换行符“的格式。
4.根据文本语境决定插入图片数量，也可以不插入图片。如果没有强相关性，不要插入图片。
5.返回的结果不要有其他任何多余的介绍词语等。
6.不要更改文本行文结构

示例：
给定文本：
这儿有种了很多花，那边还有一片宁静的湖泊。

图片信息：
图片1描述：一朵盛开的鲜花。
图片2描述：一片宁静的湖泊。
修改后的文本：
这儿有种了很多花
<1>
，那边还有一片宁静的湖泊
<2>
。


所有图片的信息：
{}

！所有图片信息到此为止！

给定的文本：
{}

！给定的文本到此为止！
'''

Add_Images_Muitl_Prompt_English = '''
Task Description:
You have an existing text and related image information description, now you need to insert the image into 
the appropriate position according to the text content with the image information.
Strictly follow the rules below:
1. Analyze all the given text, use the context from the existing text, and insert the image into the 
appropriate position based on the image description and correlation,image insertion must have strong correlation.
2. Determine the number of images to be inserted based on the text context, or choose not to insert images.
If there is no strong correlation, do not insert images.
3. Use only the<image number>as a marker for inserting images,insert the picture strictly in the 
format of ”Line breaks + <number> + line breaks“.
4. All modified text must be returned without any additional introductory words.
5. Must return without any other extra introductory words, etc.
6. Do not change the structure of the text

Give a example:
Given text:
There are a lot of flowers planted here and a peaceful lake over there.

Information about all the pictures:
Figure 1 information:
Description: a blooming flower.
Correlation: white color
Figure 2 information:
Description: a peaceful lake.
Correlation: very big
Modified text:
There are many flowers 
<1>
planted here and a peaceful lake 
<2>
over there .

All the picture information and body text will be given below.
Information about all the pictures:
{}

!This is where all the picture information ends!

All given texts are as follows.
Given text:
{}

!All the given text ends here!
'''

Optimal_Multi_Prompt_Chinese = '''
任务描述：
您有一段已存在的文本，其中使用<图片数字编号>作为标记此处有图片，现在需要根据文本内容与图片插入位置将文本修改地更加通顺。

严格按照以下要求：
1.如果一个图片出现多次，必须删除到只出现一次，只保留最好的那一次。
2.从给定的全部文本进行分析，使用给定文本的语境，不需要做太大的文章逻辑上的更改。
3.如果不需要修改，请返回原文；如果需要修改，请返回修改后的文本。
4.不要修改图片标记，也不要添加多余的介绍说明。
5.不要截断文本。


给定的文本：
{}
'''

Optimal_Multi_Prompt_English = '''
Task Description:
You have an existing text which uses <image numerical number> as a markup here with an image, and now you need to 
revise the text to make it more fluent according to the text content and the location where the image is inserted.

Strictly follow the requirements below:
1. If an image appears multiple times, it must be deleted until it only appears once and only the best one is retained.
2. use the context in the given text without making too many changes in the logic of the text.Analyze the entire text 
given, using the context of the given text without making significant logical changes to the article.
3. If you don't need to make changes, go back to the original text; if you need to make changes, go back to the 
modified text.
4. Do not modify the image labels, nor add unnecessary introductions.
5. Do not truncate the text.

the given text:
{}
'''


Extract_Prompt_English = """
You are an agent that automatically recognizes and extracts titles from a paper.
[Task] Now, I will provide you with a list containing several strings. You need to identify all the first-level titles that may come from the same paper from the list, and store the results you identify in a new list. Check the new list. If there are no strings "Abstract" and "References" in the new list, please add "Abstract" at the beginning and "References" after the main text and before the appendix. If there are, ignore this step. Finally, just print out the list you get, without returning other redundant text.
[Input]{}.

Finally, I would like to give you some references for automatically identifying paper titles:
1. First-level headings are usually used to represent major chapters or large paragraphs, while second-level headings are used to represent more specific sections or sub-paragraphs. People often use numerical numbers or specific title formats to represent different levels of titles. For example, a first-level title may be numbered with Arabic numerals (such as 1, 2, 3), which may be followed by a decimal point or any number of spaces (or both). ), and then the title content; while the second-level title adds a decimal point and numbers after the numerical number based on the first-level title, such as 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3, etc. You only need to identify the first-level titles.
2. There may be very long titles that are split into multiple strings in the list I gave. You can identify and judge the title number and the logic behind the string, and merge them back into a string, that is, into a complete title.
3. Be sure not to have the title of the appendix. The content provided to you may include appendix titles, which usually start with letters A, B, C, etc., such as "A.OBJECTDECTIONBASELINES", "B.OBJECTDECTIONIMPROVENTS", "C.IMAGENETLOCALIZATION", etc. as title numbers. If this section is included in the list I gave you, please make sure to remove the title of this section.
4.The main structure of a paper can include the following parts: article title, author, statement, keywords, abstract, introduction, main content, conclusion, and references.
"""


Get_abstract_prompt = """ 
You are an agent that automatically recognizes and extracts abstract from a paper.
[Task] Now, I will provide you with a text that may contains some other information I don't want. Please identify and extract the abstract section from the text provided above. The abstract typically appears at the beginning of a document and may be labeled as "Abstract" or may not have a clear label. It summarizes the purpose, methods, main findings, and conclusions of the study.
[Input]{}.

[waring]:
1. Ignore content that is not part of the abstract, such as the title, author information, and keywords.
2. The abstract might not include an obvious label; you may need to discern it based on content characteristics (e.g., abstracts typically summarize completed research using past tense).
3. Ensure the extracted abstract is coherent and complete, free from text snippets that belong to other sections of the document.
"""


GeneralBackground_Prompt_English = """
You are an expert reader of academic literature, and you are very good at reading long English-language documents and providing central summaries of the full academic literature. Next, I will give you an English-language academic paper and ask you to generate a central summary of the paper for me after you understand it in detail. This central summary should highlight the most important innovations, methods, and conclusions of the paper.

[Input]{}

[waring].
1. Your central summary should be in line with the central idea of the original text, and it is not allowed to misinterpret the meaning of the original text.
2. The central summary does not need to be too long, but must accurately express the most important innovations, methods, and conclusions of the paper.

"""

Analysis_Model_Prompt_English = """
You are an "academic blogger" who specializes in writing blog posts on a variety of topics in the style of an academic paper. I'm going to give you three parts, one part [Background], one part [Task], and one part [Input].
[Background]: {}

[Task] {}

[Input]{}.

[Warning]:
1. It is necessary to summarize briefly and adjust according to the length, with a maximum length of 300 words, especially for the experimental part, which cannot exceed 200 words
2. The section introducing the experiment must be brief and concise, without introducing too many details
3. Use a third person conversation tone that is both interesting and captures the reader's interests.
4. Accurate and easy to understand. Use easy to understand language and replace abstract concepts with easy to understand explanations.
5. Do not translate the original text
"""

task_dic = {
'ABSTRACT_CONCEPT': """
Now, I'm going to give you the abstract portion of an academic paper, tell me what new concept is in it, and explain it in one sentence. Be sure to keep it short, just tell me what the concept is, don't generate too much content. Make a list of all the concepts you think are important.
The output format is as follows:       
Residual Learning Framework: This is a new approach to training deeper neural networks, where layers are reformulated to learn residual functions in reference to the layer inputs, making these networks easier to optimize and capable of gaining accuracy from increased depth.
""",
'ABSTRACT': """
Don't make any changes, just tell me the original text of the ABSTRACT section
""",
'INTRODUCTION': """
Now I'm going to give you the INTRODUCTION section of your academic paper, please summarize this section in conjunction with the [Background], summarize the key elements of this section, mainly why the paper is conducting this research and what the paper hopes to achieve with this research
""",
'RELATEDWORK': """"
Now, I will provide you with the "Related Work" section of the academic paper, and in answering this section, you will help me explain into which categories the existing research is divided, what attempts have been made in each category, what are the shortcomings of the existing research, and what approaches are proposed in this paper to address these issues.
""",
'METHOD':"""
Now, I am going to provide you with the "Method" portion of the academic paper, and in answering this portion, you are going to help me explain what framework model the paper is designed to model, what methods are used, what are some of the innovations, and how does the model address the shortcomings of existing research
""",
'MODEL':"""
Now, I am going to provide you with the "MODEL" portion of the academic paper, and in answering this portion, you are going to help me explain what framework model the paper is designed to model, what methods are used, what are some of the innovations, and how does the model address the shortcomings of existing research
""",
'EXPERIMENTS':"""
I will now provide you with the "EXPERIMENTS" section of this academic paper, and please summarize this section in conjunction with the background, briefly summarizing the key content of this section, not exceeding 200 words""",
'RESULT':"""
I will now provide you with the "Results" section of this academic paper, which is summarized in conjunction with [Background], Summarize the key content of this section, including the experimental results, the conclusions drawn, and whether these conclusions address the issues mentioned in the instruction.
""",
'CONCLUSION':"""
I will now provide you with the "Conclusion" section of this academic paper. Summarize the content of this section based on the [Background], Summarize the conclusion of the paper in points, followed by a paragraph summarizing the significance of the conclusion and future research directions.
""",
'others':"""
Now, I will provide you with some of the content of this academic paper. Summarize the content of this section based on the background, highlighting the innovation and highlights of the article
""",
}

Translate_Prompt = """
You are a professional scholar who is well versed in academic translation of Chinese and English papers, I will give you a passage of text and ask you to translate it for me according to the academic style of expression and the third person narrative tone.

[Input]: {}

[Waring].
1. Don't add or transform, just translate.
2. special identifiers such as <1>,<2>,<3>,<4>,<5>,<6> must be kept in their original position in the sentence, don't change them and don't translate them.
3. Keep the translation as concise as possible and do not make a long speech.

"""

GenrateTask_Prompt_English="""

You are an academic blogger who specializes in writing blog articles on various topics in the form of academic papers. Now I will give you the title section of a paper. Please follow the example I gave you and write a prompt for me. This prompt is used to enable the big language model to professionally summarize specific parts of the text in the paper.
Example:
[input]: MODEL
[output]: Now, I am going to provide you with the "MODEL" port of the academic paper, and in answering this port, you are going to help me explain what framework model the paper is designed to model, what methods are used, what are some of the innovations, and how do the model address the shortcomings of existing research
[input]: Method
[output]: Now, I am going to provide you with the "Method" port of the academic paper, and in answering this port, you are going to help me explain what framework model the paper is designed to model, what methods are used, what are some of the innovations, and how do the model address the shortcomings of existing research

[input]: {}
"""



if __name__ == "__main__":
    pass
