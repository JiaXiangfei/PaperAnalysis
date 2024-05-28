import os

from flask_mysqldb import MySQL
from flask import Flask, request, json, \
    render_template_string, jsonify, url_for, send_from_directory, Response, make_response, send_file
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import markdown2
from backend.fic_tools_sdk.Object_handler import ObjectStor_Handler
from backend.fic_tools_sdk.config import Paperres_Config
from backend.utiles import secure_filename
from main import Single_Process
import json
from Configration import config
from backend.fic_tools_sdk.fic_tools import File_Tools as fTools

app = Flask(__name__)
CORS(app)
app.config['save_pdf_folder'] = r'../data'
app.config['out_path'] = r'../output'

# 设置解析程序所需变量
os.environ['OPENAI_API_KEY'] = config["openai_key"]
os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]
middle_path = config["out_file"]
app.config['folder_filename'] = ""
app.config['result_name'] = ""


def generate_file(file_path):
    # 读取文件内容并切分成小块，每次发送一个小块
    chunk_size = 1024  # 设置每个小块的大小

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def custom_make_response(*args, **kwargs):
    response = make_response(*args, **kwargs)
    response.headers["Content-Type"] = "application/octet-stream"
    return response


@app.route("/api/paper/upload", methods=['GET', 'POST'])
def uploadFile():
    if 'file' not in request.files:
        return jsonify(success=False, message='没有文件部分'), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message='没有选择文件'), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['save_pdf_folder'], filename)
        file.save(file_path)

        middle_path = config["out_file"]

        # 假设这里是分析文件的逻辑
        middle_filename = Single_Process(file_path, middle_path, mode=0, insert_image=True, reference=True, trans=True)
        app.config['folder_filename'] = middle_filename
        app.config['result_name'] = "result_{}.docx".format(middle_filename)
        print("后端分析已完成")

        download_link = url_for('download_with_progress', _external=True)
        # 返回分析结果的下载链接
        return jsonify(success=True, download_link=download_link), 200


@app.route('/progress')
def download_with_progress():
    print("下载文件")
    #folder_path = "../output" + f"/{middle_filename}"
    #folder_path = f"../output/{middle_filename}"
    #print(f"尝试访问的文件夹路径: {folder_path}")
    file_path = f"../output/{app.config['folder_filename']}/{app.config['result_name']}"
    #file_path = folder_path.join(result_name)
    print(f"尝试访问的文件路径: {file_path}")

    if not os.path.exists(file_path):
        print("文件不存在!")
        raise FileNotFoundError(f"文件未找到: {file_path}")

    response = custom_make_response(generate_file(file_path))
    response.headers['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(
        app.config['result_name'].encode('utf-8').hex())
    response.headers['Content-Length'] = os.path.getsize(file_path)
    return response

@app.route('/api/paper/download_link', methods=['GET'])
def get_download_link():
    # 这里重复之前生成下载链接的逻辑
    download_link = url_for('download_with_progress', _external=True)  # 注意使用_external=True生成绝对URL

    # 返回下载链接给前端
    return jsonify(success=True, download_link=download_link), 200


if __name__ == '__main__':
    app.run(debug=False)
