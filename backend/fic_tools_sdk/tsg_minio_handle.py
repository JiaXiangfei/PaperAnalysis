# -*- coding: utf-8 -*-
import os

from xmlrpc.client import ResponseError
from minio import Minio
from minio.error import S3Error, InvalidResponseError
from fic_tools_sdk.config import FIC_TSG_Logger, Minio_env
from fic_tools_sdk.fic_tools import FIC_Tools_File, FIC_Tools

"""
tsg_minio_handler.py

此类主要用于对Minio 增删查 操作。

目前已完成：
1. 文件批量上传
- 函数 upload_file 
2. 目录文件批量删除
- 函数 delete_minio_folder_by_prefix

@author: Jason Chan
@since: 2024-05-07
"""


class FIC_TSG_Minio_Handler:
    """
    此类用于对Minio 增删查 操作。
    """

    """
    :param 初始化部分
    """

    def __init__(self):
        """
        初始化SomeClass实例。
        该方法不接受参数，并且没有返回值。
        主要完成以下初始化工作：
        - 初始化MinIO环境配置
        - 创建MinIO客户端
        - 获取并设置MinIO桶（bucket）名称
        - 检查MinIO桶是否存在
        - 初始化日志记录器
        """
        # 初始化MinIO环境配置
        self.minio_env = Minio_env()
        # 创建MinIO客户端
        self.minioClient = self.create_minio_client()
        # 获取MinIO桶名称
        self.bucket_name = self.minio_env.get_env('MINIO_BUCKET_NAME')
        # 检查桶是否存在，此时不设置logger，因为is_minio_bucket_exist方法可能不存在
        self.logger = None
        self.is_minio_bucket_exist()  # 检查桶是否存在
        # 初始化日志记录器
        self.islog = True  # 标记是否启用日志记录
        self.logger = FIC_TSG_Logger()

    def create_minio_client(self):
        """
        创建一个MinIO客户端实例。

        配置信息 请看配置端

        返回值:
            - Minio: 如果成功初始化，返回一个MinIO客户端实例。
            - None: 如果在初始化过程中遇到异常，则返回None。
        """
        try:
            return Minio(
                endpoint=self.minio_env.get_env('MINIO_HOST'),
                access_key=self.minio_env.get_env('MINIO_ACCESS_KEY'),
                secret_key=self.minio_env.get_env('MINIO_SECRET_KEY'),
                secure=False
            )
        except Exception as err:
            error_message = f'create_minio_client|Exception error: {str(err)}'
            if self.islog:
                self.logger.logger.error(error_message)
            else:
                print(error_message)
            return None

    """
    :param 功能 函数部分
    """

    @FIC_Tools.time_it
    def upload_file(self, folder_name, folder_path):
        """
        上传文件到指定的文件夹。

        参数:
        - folder_name: 是同一个文件夹中需要上传的文件的MD5值
                        对应的是 存储桶中 生成的 “文件夹”
        - file_path: 字符串，待上传文件夹的绝对路径。

        返回值:
        - 如果文件夹已存在，返回字符串 "1_folder_exist"。
        - 如果文件上传成功，返回上传结果（依赖于 upload_files_to_minio 方法的返回值）。
        - 如果遇到错误，抛出 ValueError 或记录错误日志。
        """
        if not folder_name or not folder_path:
            raise ValueError("folder_name and file_path cannot be empty.")
        try:
            if self.is_folder_exist(self.bucket_name, folder_name):
                return "1_folder_exist"
            else:
                return self.upload_files_to_minio(folder_name, folder_path)
        except ResponseError as err:
            self.logger.logger.error(f'def upload_file|File: {self.bucket_name} upload_failed: {str(err)}')

    @FIC_Tools.time_it
    def delete_minio_folder_by_prefix(self, prefix):
        """
        根据指定前缀删除 MinIO 存储桶中的文件和文件夹。

        - prefix: 要删除的文件和文件夹的前缀。
        """
        for obj in self.minioClient.list_objects(self.bucket_name, prefix=prefix, recursive=True):
            # 判断对象是否为文件
            if not obj.object_name.endswith("/"):
                try:
                    # 删除文件
                    self.minioClient.remove_object(self.bucket_name, obj.object_name)
                except ResponseError as err:
                    # 打印删除过程中遇到的错误
                    print(f"删除时出错： {obj.object_name}: {err}")
        # 删除过程完成后通知
        print("目录下的所有文件都已删除.")

    def upload_single_file(self, file_info):
        """
        上传单个文件到MinIO服务器。

        参数:
        - file_info: 一个元组，包含文件路径和对象名称。

        返回值:
        - None: 文件上传成功。
        - 字符串: 文件上传失败时返回错误代码。

        异常:
        - 处理S3Error和ResponseError之外的异常会返回特定错误代码。
        """
        file_path, object_name = file_info
        try:
            self.minioClient.fput_object(self.bucket_name, object_name, file_path)
            self.logger.logger.info(f"Uploaded '{file_path}' to '{object_name}' in '{self.bucket_name}'")
            return None
        except (S3Error, ResponseError) as err:
            self.logger.logger.error(f'File: {object_name} upload failed: {str(err)}')
            return "3_Upload_Failed"
        except Exception as err:
            self.logger.logger.error(f'Unexpected error: {str(err)}')
            return "4_Unexpected_Error"

    def upload_files_to_minio(self, folder_name, upload_dir):
        """
        将指定本地目录中的所有文件上传到MinIO服务器。

        参数:
        folder_name (str): MinIO服务器上要创建的文件夹名称。
        upload_dir (str): 包含要上传文件的本地目录路径。

        返回:
        无返回值。

        抛出:
        NotADirectoryError: 如果`upload_dir`不是一个有效的目录。
        """

        # 检查上传目录是否有效
        if not os.path.isdir(upload_dir):
            raise NotADirectoryError(f"{upload_dir} 不是一个有效的目录。")

        # 使用工具方法从目录上传文件
        FIC_Tools_File.upload_files(self.upload_single_file, folder_name, upload_dir)

    def minio_folder_list(self, bucket_name):
        """
        获取MinIO存储桶中所有对象（文件或文件夹）的名称列表。

        参数:
        bucket_name (str): MinIO服务器上的存储桶名称。

        返回:
        list[str]: 存储桶中对象名称的列表。

        抛出:
        S3Error: 如果在获取存储桶对象时发生意外错误。
        """
        object_names = []

        try:
            objects = self.minioClient.list_objects(bucket_name)
            for obj in objects:
                object_names.append(obj.object_name)
            return object_names
        except S3Error as err:
            self.logger.logger.error(f'意外错误: {str(err)}')

    """
    :param 工具 函数部分
    """

    def is_file_exist(self, bucket_name, file_md5, folder_md5):
        """
        检查指定存储桶和文件夹中是否存在具有特定MD5的文件。

        参数:
        - bucket_name (str): S3存储桶的名称。
        - file_md5 (str): 要检查的文件的MD5校验和。
        - folder_md5 (str): 文件所在文件夹的MD5校验和。

        返回:
        - bool: 如果文件存在，则返回True；否则返回False。
        """
        try:
            # 尝试检查文件MD5是否在存储桶和文件夹的ETag列表中。
            if file_md5 in self.minio_file_etag_list(bucket_name, folder_md5):
                return True
            return False
        except S3Error as err:
            # 记录S3访问错误。
            self.logger.logger.error(f'S3Error error: {str(err)}')

    def is_folder_exist(self, bucket_name, folder_name):
        """
        检查S3存储桶中指定的文件夹是否存在。

        参数:
        - bucket_name (str): S3存储桶的名称。
        - folder_name (str): 要检查是否存在的文件夹名称。

        返回:
        - bool: 如果文件夹存在，则返回True；否则返回False。
        """
        try:
            folder_name = folder_name + '/'  # 为文件夹名称添加尾部斜杠，确保其格式正确
            if folder_name in self.minio_folder_list(bucket_name):  # 查询文件夹是否存在于指定存储桶中
                print(f'folder: {folder_name} is exist')
                return True
            print(f'folder: {folder_name} is not exist')
            return False
        except S3Error as err:  # 捕获并记录S3操作中的错误
            self.logger.logger.error(f'S3Error error: {str(err)}')

    def is_minio_bucket_exist(self):
        """
        检查MinIO桶是否存在，如果不存在则创建。

        此函数不接受参数，并且没有返回值。
        它主要用于确保指定的MinIO桶存在，如果不存在，则通过调用MinIO客户端的make_bucket方法来创建。

        异常处理：
        - 如果遇到InvalidResponseError异常，将记录错误日志。
        """
        try:
            # 检查桶是否存在，如果不存在则创建该桶
            if not self.minioClient.bucket_exists(self.bucket_name):
                self.minioClient.make_bucket(self.bucket_name)
        except InvalidResponseError as err:
            # 记录InvalidResponseError异常错误日志
            self.logger.logger.error(f'InvalidResponseError error: {str(err)}')

    def delete_minio_bucket(self):
        """
        删除MinIO中的存储桶。

        此方法尝试删除当前实例所配置的MinIO存储桶。如果删除过程中遇到任何问题，例如网络错误或存储桶不存在，
        则会记录一个错误日志。

        参数:
        - self: 方法的对象引用，提供对类属性和方法的访问。

        返回值:
        - 无
        """
        try:
            self.minioClient.remove_bucket(self.bucket_name)  # 尝试删除指定的存储桶
        except InvalidResponseError as err:  # 捕获无效响应错误
            self.logger.logger.error(f'InvalidResponseError error: {str(err)}')  # 记录错误日志

    def minio_file_etag_list(self, bucket_name, prefix):
        """
        获取MinIO存储桶中指定前缀的文件的ETag列表。

        参数:
        - bucket_name (str): MinIO存储桶的名称。
        - prefix (str): 文件的前缀，用于筛选文件。

        返回:
        - list: 包含所选文件ETag的列表。
        """
        # 初始化一个空列表用于存储ETag
        list_etag = []
        try:
            # 列出指定存储桶和前缀的所有对象
            objects = self.minioClient.list_objects(bucket_name, prefix)
            for obj in objects:
                # 将每个对象的ETag添加到列表中
                list_etag.append(obj.etag)
            return list_etag
        except S3Error as err:
            # 记录遇到的S3异常错误
            self.logger.logger.error(f'Unexpected error: {str(err)}')
