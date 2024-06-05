# -*- coding: utf-8 -*-
import configparser
import os


def load_config():
    conf = configparser.ConfigParser()
    conf.read('fic_tools_sdk/config.ini')
    return conf


class Paperres_Config:
    def __init__(self):
        # 临时文件夹 用于存储临时上传文件
        self.config = load_config()

        self.pdf_folder_path = os.path.join(os.getcwd(), self.config['Paperres_Config']['pdf_folder_path'])
        self.paperrec_folder_path = os.path.join(os.getcwd(), self.config['Paperres_Config']['paperrec_folder_path'])
        self.tmp_folder_path = os.path.join(os.getcwd(), self.config['Paperres_Config']['tmp_folder_path'])
        self.image_prefix = self.config['Paperres_Config']['image_prefix']

        os.makedirs(self.pdf_folder_path, exist_ok=True)
        os.makedirs(self.paperrec_folder_path, exist_ok=True)

        self.pdf_file_path = None

    def get_pdf_folder_path(self):
        return self.pdf_folder_path

    def get_paperrec_folder_path(self):
        return self.paperrec_folder_path


'''
对象存储（OSS） 配置信息 模块
'''


class OSS_Config:
    def __init__(self):
        self.config = load_config()

        self.access_key = self.config['Minio_Config']['minio_access_key']
        self.secret_key = self.config['Minio_Config']['minio_secret_key']
        self.host = self.config['Minio_Config']['host'] + ':' + str(self.config['Minio_Config']['port'])
        self.https = self.config['Minio_Config']['https'].lower() == 'true'
        self.bucket_name = self.config['Minio_Config']['minio_bucket_name']


class Log_Config:
    def __init__(self):
        """
        初始化配置信息
        :param config:
        """

        self.config = load_config()
        print(self.config)
        self.host = self.config['Log']['host']
        self.port = int(self.config['Log']['port'])
        self.level = self.config['Log']['level'].upper()
        self.islog = self.config['Log']['islog'].lower() == 'true'


class Redis_Config:
    def __init__(self):
        """
        初始化配置信息
        :param config:
        """
        self.config = load_config()

        self.host = self.config['Redis_Config']['host']
        self.port = int(self.config['Redis_Config']['port'])
        self.password = self.config['Redis_Config']['password']
        self.db = int(self.config['Redis_Config']['db'])