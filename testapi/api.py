import os

import re
import openai
from flask_mysqldb import MySQL
from flask import Flask, request, render_template, flash, redirect, url_for, session, jsonify, json
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from main import Single_Process
import json
from Configration import config


app = Flask(__name__)
app.config['MYSQL_HOST'] = '10.8.29.28'
app.config['MYSQL_USER'] = 'paperrec'
app.config['MYSQL_PASSWORD'] = 'Fic@332PR'
app.config['MYSQL_DB'] = 'paperrecdb'
mysql = MySQL(app)
CORS(app)

#设置解析程序所需变量
os.environ['OPENAI_API_KEY'] = config["openai_key"]
os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]
middle_path = config["out_file"]


@app.route("/api/paper/upload", methods=['GET', 'POST'])
def uploadFile():
    # 保存文件的路径
    #save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)).split('TPMService')[0], 'TPMService/static')
    # 获取文件
    file = request.files['file']
    ##保存文件
    if file:
        # 确保文件名是安全的，并保存文件
        filename = file.filename
        filename = os.path.splitext(os.path.basename(filename))[0]
        file_path = os.path.join("./data", filename)
        file.save(file_path)

        # 获取附加的表单数据并开始解析
        options = request.form.get('switchState')
        get_option = Get_Para(options)

        data = None
        status = 'success'
        try:
            Single_Process(file_path,middle_path,get_option[0],get_option[1],get_option[2],get_option[3])
        except:
            status = 'fail'
            print("Process falied!")
        else:
            result_path = os.path.join(middle_path, filename,"text_parts.json")
            with open(result_path, 'r') as file_response:
                data = json.load(file_response)


        #上传的json
        response_data = {
            'status': status,
            'message': '文件已上传',
            'options': options,
            'data':data
        }
        return jsonify(response_data)
    else:
        return jsonify({'status': 'error', 'message': '未找到上传文件'}), 400


# @app.route("/api/paper/select", methods=['GET', 'POST'])
# def selectFile():
#     # 连接数据库
#     cur = mysql.connection.cursor()
#     # 查询数据库
#     cur.execute("SELECT * FROM filetest")
#     # 获取查询结果
#     result = cur.fetchone()
#     # 关闭数据库连接
#     cur.close()
#     # 返回查询结果
#     return {"code": 200, "message": "查询请求成功", "data": result}



def Get_Para(options:list):
    result = [0, False, False, False]
    print(type(options))
    print(type(options[0]["id"]))
    if len(options):
        for item in options:
            if item["id"].equals('1'):
                result[0] = 1
            if item["id"].equals('2'):
                result[1] = True
            if item["id"].equals('3'):
                result[2] = True
            if item["id"].equals('4'):
                result[3] = True
    return result

if __name__ == '__main__':
    app.run(debug=True)