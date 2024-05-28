# -*- coding: utf-8 -*-
import concurrent
import concurrent.futures
import hashlib
import json
import os
import re
import time

from backend.fic_tools_sdk.fic_security import to_log
from chardet.universaldetector import UniversalDetector


class File_Tools:

    def __init__(self):
        pass

    """
    计算文件md5 
    目前推荐使用
    """

    @staticmethod
    def calculate_file_md5(file_path: str) -> str | None:
        """
        计算给定文件的MD5校验和。

        参数:
        :param file_path : 字符串，指定要计算MD5校验和的文件的路径。

        返回值:
        :return file_md5 : 字符串，文件的MD5校验和。如果在处理文件时遇到错误，返回None。
        """
        # 定义读取文件时的缓冲区大小
        chunk_size = 4096

        try:
            # 获取文件状态信息，用于异常处理和验证文件存在性
            file_stat = os.stat(file_path)

            # 初始化MD5加密算法对象
            md5_hash = hashlib.md5()

            # 打开文件，以二进制读取模式进行处理
            with open(file_path, 'rb') as file_handle:
                # 循环读取文件，直到没有更多的数据
                while True:
                    chunk = file_handle.read(chunk_size)  # 读取指定大小的数据块
                    if not chunk:  # 如果数据块为空，说明已读取完文件
                        break
                    md5_hash.update(chunk)  # 使用数据块更新MD5加密对象的状态

            # 计算并获取最终的MD5校验和
            file_md5 = md5_hash.hexdigest()

        except FileNotFoundError:
            # 如果文件不存在，打印错误信息并返回None
            print(f"文件路径错误：{file_path} 不存在")
            return None
        except PermissionError:
            # 如果没有文件的访问权限，打印错误信息并返回None
            print(f"没有权限访问文件：{file_path}")
            return None
        except Exception as e:
            # 捕获其他异常，打印未知错误信息并返回None
            print(f"处理文件 {file_path} 时发生未知错误：{e}")
            return None

        # 如果没有遇到任何错误，返回计算得到的MD5校验和
        return file_md5

    @staticmethod
    @to_log
    def upload_files(func_name, folder_name, upload_path, max_workers=2):
        """
        上传文件到Minio
        参数：
        :param func_name: 上传函数
        :param folder_name: 文件夹名称
        :param upload_path: 上传路径
        :param max_workers: 最大线程数

        返回
        :return:
        """
        # 遍历上传目录，收集所有需要上传的文件及其目标对象名称
        file_to_upload = []
        for root, dirs, files in os.walk(upload_path):
            for file in files:
                file_path = os.path.join(root, file)
                object_name = f"{folder_name}/{file}"
                file_to_upload.append((file_path, object_name))

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 使用 as_completed 以便异步处理异常
                futures = [executor.submit(func_name, file) for file in file_to_upload]
                for future in concurrent.futures.as_completed(futures):
                    if future.exception() is not None:
                        print(f'上传文件时发生异常: {future.exception()}')
                    else:
                        result = future.result()
                        print(f'文件上传结果: {result}')

                # 统一处理上传结果
                if any(result != "1_Upload_Success" for result in futures):
                    return "3_Upload_Failed"
                else:
                    return "2_Upload_Success:"
        except Exception as e:
            print(f'上传过程中发生未知错误: {e}')
            return "3_Upload_Failed"

    @staticmethod
    def write_to_file(file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    @to_log
    def read_file(pdf_json_to_markdown_file_path):
        """
        读取指定路径的文件内容。

        :param pdf_json_to_markdown_file_path: 文件路径
        :return: 文件内容
        """
        # 参数验证
        #fic_security.Sec.validate_file_path(pdf_json_to_markdown_file_path)
        encoding = File_Tools.detect_encoding(pdf_json_to_markdown_file_path)

        try:
            # 使用with语句打开文件，确保文件正确关闭
            with open(pdf_json_to_markdown_file_path, 'r', encoding=encoding) as file:
                # 对于大文件，这里采用逐行读取的方式
                content = file.read()
        except IOError as e:
            # 处理文件读取异常
            raise IOError(f"读取文件时发生错误: {e}")
        return content

    @staticmethod
    def json_load_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = json.load(file)

        return content

    @staticmethod
    def convert_json_to_markdown(json_data: object):
        """
        将JSON文件转换为Markdown格式。
        :param json_data: JSON Data。
        :return: Markdown格式的字符串。
        """

        markdown_data = ''
        for key, value in json_data.items():
            # 使用'#'符号来表示标题级别，这里假设所有标题都是最高级别（#）

            markdown_data += f"# {key}\n"
            # 如果值是字符串，则直接添加，如果是列表则每个元素换行
            # i = 1
            if isinstance(value, str):
                markdown_data += f"{value}\n\n"
                print("MD-str")
            elif isinstance(value, list):
                markdown_data += "\n".join([f"- {item}" for item in value]) + "\n\n"
                print("MD-list")
            else:
                # 对于其他类型的值，简单地转换为字符串
                markdown_data += f"{str(value)}\n\n"
                print("MD-3")

                # 写入Markdown文件
        return markdown_data
        #
        # markdown_list = []
        # for key, value in json_data.items():
        #     markdown_list.append(f"# {key}\n\n")
        #
        #
        # markdown_data = ''.join(markdown_list)
        # return markdown_data

    @staticmethod
    def replace_urls_with_images(file_content, rc, image_urls: list):
        # 正则表达式匹配url-minio-jpg字段
        content = file_content
        images_num = len(image_urls)
        # 创建一个新的字符串来保存替换后的内容
        new_content = ''
        match_indices = []
        # 查找所有匹配项的开始和结束索引
        for match in re.finditer(rc, content):
            match_indices.append((match.start(), match.end()))

        if len(image_urls) > 0:
            # 使用正则表达式替换
            last_end = 0
            for i, (start, end) in enumerate(match_indices):
                if i < images_num:
                    url = image_urls[i]
                else:
                    url = ''
                new_content += content[
                               last_end:start] + f'<div align=center><img src={url}></div><br>'
                last_end = end

                if i == len(match_indices) - 1:
                    new_content += content[end:]

        else:
            last_end = 0
            for i, (start, end) in enumerate(match_indices):
                new_content += content[last_end:start] + f'<div> </div>'
                last_end = end

                if i == len(match_indices) - 1:
                    new_content += content[end:]

        return new_content

    @staticmethod
    def detect_encoding(file_path):
        """
        自动检测文件编码。

        :param file_path: 文件路径
        :return: 文件编码
        """
        detector = UniversalDetector()
        with open(file_path, 'rb') as file:
            for line in file.readlines():
                detector.feed(line)
                if detector.done: break
        detector.close()

        return detector.result['encoding'] or 'utf-8'


class Tools:
    def __init__(self):
        pass

    @staticmethod
    def time_it(func):
        """
        装饰器函数，用于计算函数执行时间
        """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            exec_time = end_time - start_time
            print(f"函数 {func.__name__} 执行时间为: {exec_time:.6f} 秒")
            return result

        return wrapper
