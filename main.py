from utils.pdfImagesInfo import Find_Image_Information
from utils.MatchImages import MatchImage
from utils.pdfGetImage import Get_Image
from utils.ExtractRef import Get_Reccomend
from utils.Structured_extraction import Struxtured_extraction
import os
import re
import json
from Configration import config
from utils.pdfGetImage import Choose_File

def Extract_rec(pdf_path,middle_path):
    # 获取文件名,去除扩展名
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # 移除路径中可能导致问题的特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
    filename = filename.rstrip(". ")  # 移除末尾的点和空格
    text_path = os.path.join(middle_path, filename, "original_parts.json")
    ref_path = os.path.join(middle_path, filename, "Reference.json")
    #执行操作
    Get_Reccomend(text_path, ref_path)

def Extract(pdf_path, out_file, details):
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

    results = Struxtured_extraction(pdf_path, output_origin_file_path_json, details=details)
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
    # 增加一个return，把文件名return出来
    return filename


def Insert_Images(pdf_path, middle_path,model="gpt-4-32k",insert_image = True,reference = True,trans = False,):
    # 获取文件名,去除扩展名
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # 移除路径中可能导致问题的特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除Windows路径中不允许的字符
    filename = filename.rstrip(". ")  # 移除末尾的点和空格
    text_path = os.path.join(middle_path, filename,"text_parts.json")
    images_path = os.path.join(middle_path, filename, "images")
    images_information_path = os.path.join(middle_path, filename, "images_information.json")
    store_path = os.path.join(middle_path, filename, "result_{}.docx".format(filename))

    try:
        Get_Image(pdf_path,middle_path)
        print("Find Images OK!")
        Find_Image_Information(pdf_path, images_path, middle_path)
        print("Find Images information OK!")
        MatchImage(text_path,images_information_path, images_path, store_path, model=model,insert_image = insert_image,reference = reference,trans = trans)
        print("Match Images OK!")

    except Exception as e:
        print(e)
        return False
    else:
        return True

def Single_Process(pdf_path,middle_path,mode = 0,insert_image = True,reference = True,trans = True,model =  "gpt-4-32k"):
    '''
    :param pdf_path: pdf存储路径
    :param middle_path: 中间文件存储文件夹
    :param mode: 模式选择，0为简单版本，1为详细版本
    :param insert_image: 是否插入图片
    :param reference: 是否加入摘要
    :param translate: 是否翻译
    :param result_path: 存储结果地址
    :param model: 使用的模型
    :return:
    '''
    if os.path.exists(pdf_path):
        print(f"Start to analyse!")
        # 请在此处进行模式选择，0为简单版本，1为详细版本
        middle_filename = Extract(pdf_path, middle_path, mode)
        Extract_rec(pdf_path,middle_path)
        # Insert_Images(pdf_path, middle_path, result_path, model,insert_image,reference, trans)
        Insert_Images(pdf_path, middle_path, model, insert_image, reference, trans)
        print(f"Analysis has finished!\n========================================")
        return middle_filename
    else:
        print("File doesn't exist!")

if __name__ == "__main__":
    os.environ['OPENAI_API_KEY'] = config["openai_key"]
    os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]

    #pdf_path = config["test_pdf"]
    pdf_path = Choose_File("./")
    middle_path = config["out_file"]
    #a = Extract_rec(pdf_path, middle_path)
    #Insert_Images(pdf_path,middle_path,model="gpt-4-turbo")
    Single_Process(pdf_path,middle_path,mode=0,insert_image=True,reference=True,trans=False,model="gpt-4-turbo")
    '''
        :param pdf_path: pdf存储路径
        :param middle_path: 中间文件存储文件夹
        :param mode: 模式选择，0为简单版本，1为详细版本
        :param insert_image: 是否插入图片
        :param reference: 是否加入摘要
        :param translate: 是否翻译
        :param result_path: 存储结果地址
        :param model: 使用的模型
        :return: 
    '''