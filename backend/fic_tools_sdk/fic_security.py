# -*- coding: utf-8 -*-
import functools
import os
import logging
from logging import Logger

from pygelf import GelfTcpHandler, GelfUdpHandler

import backend.fic_tools_sdk.config
from backend.fic_tools_sdk import config


class Log_Item:
    def __init__(self):
        self.config = config.Log_Config()

        self.islog = self.config.islog
        self.level = self.config.level

        self.logger = None

        if self.islog:
            self.configure_logger()

    def get_status_logger(self) -> bool:
        self.logger.addHandler(GelfTcpHandler(self.config.host, self.config.port))
        return self.islog

    def logger_ctl(self, option):
        if option == 'enable':
            self.enable_logger()
        elif option == 'disable':
            self.disable_logger()
        else:
            raise ValueError("无效的选项")

    def enable_logger(self):
        self.islog = True
        self.configure_logger()

    def disable_logger(self):
        self.islog = False

    def configure_logger(self):

        numeric_level = getattr(logging, self.level, logging.INFO)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {self.level}')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(numeric_level)

        # 配置GELF UDP handler
        gelf_udp_handler = GelfUdpHandler(self.config.host, self.config.port)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger.addHandler(gelf_udp_handler)

        # 保留标准输出流处理器以兼容控制台打印
        gelf_udp_handler.setFormatter(formatter)
        self.logger.addHandler(gelf_udp_handler)

    def get_logger(self):
        return self.logger


class Sec:
    def __init__(self):
        pass

    @staticmethod
    def validate_file_path(file_path):
        """
        验证文件路径的安全性和有效性。

        :param file_path: 待验证的文件路径
        :raises ValueError: 如果文件路径无效或不安全
        :raises FileNotFoundError: 如果文件不存在
        """
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("文件路径必须是一个非空字符串")

        if '..' in file_path or file_path.startswith('/'):
            raise ValueError("文件路径看起来不安全")

        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"指定的文件 '{file_path}' 不存在")

    @staticmethod
    def exception_handler(func):
        """
        装饰器，用于捕获并处理函数中的异常。

        :param func: 被装饰的函数
        :return: 包装后的函数
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as ve:
                print(f"发生 ValueError 异常: {ve}")
            except FileNotFoundError as fne:
                print(f"发生 FileNotFoundError 异常: {fne}")
            except PermissionError as pe:
                print(f"发生 PermissionError 异常: {pe}")
            except UnicodeDecodeError as ude:
                print(f"发生 UnicodeDecodeError 异常: {ude}")
            except Exception as e:
                print(f"发生未知异常: {e}")
                raise e

        return wrapper


logger = Log_Item().get_logger()


def to_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            logger.error(f"发生 ValueError 异常: {ve}")
            print(f"发生 ValueError 异常: {ve}")
        except FileNotFoundError as fne:
            logger.error(f"发生 FileNotFoundError 异常: {fne}")
            print(f"发生 FileNotFoundError 异常: {fne}")
        except PermissionError as pe:
            logger.error(f"发生 PermissionError 异常: {pe}")
            print(f"发生 PermissionError 异常: {pe}")
        except UnicodeDecodeError as ude:
            logger.error(f"发生 UnicodeDecodeError 异常: {ude}")
            print(f"发生 UnicodeDecodeError 异常: {ude}")
        except TypeError as te:
            logger.error(f"发生 TypeError 异常: {te}")
            print(f"发生 TypeError 异常: {te}")
        except IOError as ioe:
            logger.error(f"发生 IOError 异常: {ioe}")
            print(f"发生 IOError 异常: {ioe}")
        except Exception as e:
            print(f"发生未知异常: {e}")
            raise e

    return wrapper
