#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/3/17 9:37
# @Author  : ys
# @File    : pdfGetImage.py
# @Software: PyCharm
import base64
import decimal

import win32ui
import PyPDF2
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTFigure
from pdf2image import convert_from_path
from decimal import Decimal
import os
import re
import fitz

from Configration import config
os.environ["PATH"] += os.pathsep + config["poppler_path"]        #添加poppler临时路径

def Choose_File(default = "../.."):
    print('打开文件对话框，选取文件')
    dlg = win32ui.CreateFileDialog(1)  # 0代表另存为对话框，1代表打开文件对话框
    dlg.SetOFNInitialDir(os.path.abspath(os.path.join(os.getcwd(), default)))  # 默认当前上级目录
    dlg.DoModal()  # 显示对话框
    filename = dlg.GetPathName()  # 获取用户选择的文件全路径
    return filename

def Crop_image_Save(element, pageObj, pagenum, image_num,file = None,keep_temp = False,Save_path = "./"):
    # 获取从PDF中裁剪图像的坐标
    ##############################################左下角点坐标、右上角点坐标，以左下角为原点
    [image_left, image_bottom, image_right, image_top] = [element.x0, element.y0, element.x1, element.y1]
    #### 使用坐标(left, bottom, right, top)裁剪页面
    height = pageObj.mediabox.height
    width = pageObj.mediabox.width
    ##############################################调整视界范围，下方信息丢失
    #pageObj.mediabox.lower_left = (image_left, image_bottom)
    #pageObj.mediabox.upper_right = (image_right, image_top)
    # 将裁剪后的页面保存为新的PDF
    # cropped_pdf_writer = PyPDF2.PdfWriter()
    # cropped_pdf_writer.add_page(pageObj)

    #创建临时文件夹
    dict = "temp"
    if not os.path.exists(dict):
        os.makedirs(dict)
    if file is not None:
        # 获取文件名,去除扩展名
        filename = os.path.splitext(os.path.basename(file))[0]
        #移除路径中可能导致问题的特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
        filename = filename.rstrip(". ")  # 移除末尾的点和空格

        if not os.path.exists(os.path.join(dict, filename)):
            os.makedirs(dict + "/" + filename)
        cropped_pdf_file_path = os.path.abspath(f'./temp/{filename}/cropped_image_{pagenum}_{image_num}.pdf')
        if not os.path.exists(Save_path + "/" + filename + "/" + "images"):
            os.makedirs(Save_path + "/" + filename + "/" + "images")
        output_file = os.path.abspath(f"{Save_path}/{filename}/images/page_{pagenum}_image_{image_num}.png")
        #output_file = os.path.abspath(f"{Save_path}/{filename}/images/")
    else:
        cropped_pdf_file_path = os.path.abspath(f'./temp/cropped_image_{pagenum}_{image_num}.pdf')
        output_file = os.path.abspath(f"{Save_path}/page_{pagenum}_image_{image_num}.png")

    #裁剪
    # with open(cropped_pdf_file_path, 'wb') as cropped_pdf_file:
    #     cropped_pdf_writer.write(cropped_pdf_file)
    # 将裁剪后的PDF转换为图像并保存
    # images = convert_from_path(cropped_pdf_file_path, poppler_path=os.path.abspath(config["poppler_path"]))
    # image = images[0]
    # image.save(output_file, "PNG")

    #print(type(height),type(width),type(image_left),type(image_right),type(image_top),type(image_bottom))
    if isinstance(height,decimal.Decimal) or isinstance(height,int):
        height = float(height)
    if isinstance(width, decimal.Decimal) or isinstance(width,int):
        width = float(width)
    #print(type(height), type(width), type(image_left), type(image_right), type(image_top), type(image_bottom))


    ################################################左上角原点，右下角坐标系
    image_rects = fitz.Rect(image_left, height - image_top,image_right,height - image_bottom)

    # 打开PDF文件
    # 打开PDF文件
    pdf_document_1 = fitz.open(file)
    #     # 获取当前页
    page = pdf_document_1.load_page(pagenum)

    # 从页面中截取图片
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), clip=image_rects)
    #print(pix.h,pix.w)

    # 保存图片
    image_path = output_file
    pix.save(image_path)

    pdf_document_1.close()

    # # 打开PDF文件
    # pdf_document = fitz.open(file)
    #
    # # 遍历PDF中的每一页
    # for page_number in range(len(pdf_document)):
    #     # 获取当前页
    #     page = pdf_document[page_number]
    #
    #     # 检索页面上的图像列表
    #     images = page.get_images(full=True)
    #
    #     # 遍历页面上的所有图像
    #     for image_number, img in enumerate(images):
    #         # 提取图像的base64字符串
    #         base64_img = img[5]
    #
    #         # 将base64字符串解码为图像数据
    #         img_data = base64.b64decode(base64_img)
    #
    #         # 保存图像
    #         image_path = output_file
    #         with open(image_path, 'wb') as f:
    #             f.write(img_data)
    #
    # pdf_document.close()

    # 删除临时裁剪的PDF文件与文件夹
    if not keep_temp:
        if os.path.exists(cropped_pdf_file_path):
            os.remove(cropped_pdf_file_path)
        if file is not None and len(os.listdir(dict + "/" + filename)) == 0:
            os.rmdir(dict + "/" + filename)
        if os.path.exists(dict) and len(os.listdir(dict)) == 0:
            os.rmdir(dict)

def Get_Image(pdf_path,store_path):
    # 创建一个PDF文件对象
    pdfFileObj = open(pdf_path, 'rb')
    # 创建一个PDF阅读器对象
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)
    Image_Count = 1
    # 我们从PDF中提取页面
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        # 初始化从页面中提取文本所需的变量
        pageObj = pdfReaded.pages[pagenum]
        # 找到所有的元素,并页面中出现的所有元素进行排序，依据元素下部在pdf的位置排序
        page_elements = [(element.y1, element) for element in page._objs]
        page_elements.sort(key=lambda a: a[0], reverse=True)
        # 查找组成页面的元素
        for i, component in enumerate(page_elements):
            # 提取页面布局的元素
            element = component[1]
            # 检查元素中的图像
            if isinstance(element, LTFigure):
                # 判断是否需要裁剪
                if Judge_Cut(pageObj,element):
                    Crop_image_Save(element, pageObj, pagenum, Image_Count, file = pdf_path, Save_path=store_path)
                    Image_Count += 1
    # 关闭pdf文件对象
    pdfFileObj.close()


def File_Get_Image(file_path,store_path):
    file_list = os.listdir(file_path)
    if file_list > 0:
        for file in file_list:
            Get_Image(file_path + "/" + file, store_path)


def Judge_Cut(pageObj,element):
    flag = True
    # 获取页面的完整尺寸
    full_page_width = pageObj.mediabox.upper_right[0] - pageObj.mediabox.lower_left[0]
    full_page_height = pageObj.mediabox.upper_right[1] - pageObj.mediabox.lower_left[1]
    # 判断是否需要裁剪，获取从PDF中裁剪图像的坐标
    [image_left, image_top, image_right, image_bottom] = [element.x0, element.y0, element.x1, element.y1]
    # 检查是否需要裁剪
    #是否全张
    if (image_left == 0.0 and image_bottom == full_page_height and
        image_right == full_page_width and image_top == 0.0):
        flag = False
    #是否过小
    img_width = image_right - image_left
    img_height = image_bottom - image_top
    if (int(img_height) < int(full_page_height/20) or int(img_width) < int(full_page_width/6)):
        flag = False
    return flag


if __name__ == "__main__":
    file = Choose_File()
    #file = config["test_pdf"]
    store_path = config["out_file"]
    Get_Image(file,store_path)


