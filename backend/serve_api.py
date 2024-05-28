import os

from flask_mysqldb import MySQL
from flask import Flask, request, json, \
    render_template_string
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

#设置解析程序所需变量
os.environ['OPENAI_API_KEY'] = config["openai_key"]
os.environ['OPENAI_BASE_URL'] = config["openai_base_url"]
middle_path = config["out_file"]


def option_json(options: list, md5_paperrec_folder_path):
    '''
    :param options: [{'id': 1, 'name': '详细分析'}, {'id': 2, 'name': '匹配图片'}, {'id': 3, 'name': '翻译中文'}, {'id': 4, 'name': '分析文献'}]
    :return:  前端用户选择的分析类型对应的json文件
    '''
    option_list = []
    retured_json_name = ''
    reference_name = "Reference.json"

    if len(options):
        for item in options:
            option_list.append(item['id'])
        # 检查元素是否存在
        insert_image = 2
        trans = 3
        reference = 4
        if trans in option_list:
            retured_json_name = 'images_insert.json'
        else:
            retured_json_name = 'images_insert.json'

        full_path = '/'.join([md5_paperrec_folder_path, retured_json_name])
        with open(full_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        if reference in option_list:
            reference_path = '/'.join([md5_paperrec_folder_path, reference_name])
            with open(reference_path, 'r', encoding='utf-8') as json_file:
                reference_data = json.load(json_file)
            # dict1 = json.loads(data)
            # dict2 = json.loads(reference_data)
            data.update(reference_data)
            merged_dict = data
            # 如果需要将结果转换回JSON字符串
            data = json.dumps(merged_dict, ensure_ascii=False)
        return data
    else:
        print(f"元素不在列表中")


def pdf_handler(pdf_file_path, md5_paperrec_folder_path, get_option):
    '''
    :param pdf_file_path:  pdf文件的保存地址
    :param middle_path:   分析结果的保存地址
    :param get_option:    前端用户选择的分析类型
    :return:
    '''
    try:
        Single_Process(pdf_file_path, md5_paperrec_folder_path)
    except:
        status = 'fail'
        print("Process falied!")

    result_json = option_json(get_option, md5_paperrec_folder_path)
    return result_json


@app.route("/api/paper/upload", methods=['GET', 'POST'])
def uploadFile():
    # 保存文件的路径
    #save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)).split('TPMService')[0], 'TPMService/static')
    # 获取文件
    file = request.files.get('file')
    data = request.form.get('switchState')
    data = json.loads(data)

    response_data = {
        'message': '文件已上传',
        'options': data,
    }
    options = data['checkboxList']
    # if file and file.filename and file.content_type.startswith('application/pdf'):
        # 获取文件名
        # html_var_list = [request.form.get(f'param{i}') for i in range(1, 5)]
    # 清洗文件名以确保安全
    safe_filename = secure_filename(file.filename)
    pdf_file_path = os.path.join(config["pdf_folder_path"], safe_filename)
    print(pdf_file_path)

    try:
        # 保存文件
        file.save(pdf_file_path)

        print("Start Calculate MD5")
        # 计算上传文件 MD5 值
        folder_md5 = fTools.calculate_file_md5(pdf_file_path)

        # 创建对应pdf 数据处理文件夹
        md5_paperrec_folder_path = os.path.join(config['out_file'], folder_md5)
        os.makedirs(md5_paperrec_folder_path, exist_ok=True)

        '''
        将 PDF 转换为 JSON Data 和 本地图片

        将JSON DATA 转换为 Markdown Data

        将Markdown Data 保存为 0-markdown-{folder_md5}.md 文件
        '''

        markdown_data = fTools.convert_json_to_markdown(pdf_handler(pdf_file_path,
                                                                    md5_paperrec_folder_path,
                                                                    options,
                                                                    ))

        pdf_json_to_markdown_name = f'0-markdown-{folder_md5}.md'
        pdf_json_to_markdown_file_path = os.path.join(md5_paperrec_folder_path, pdf_json_to_markdown_name)

        fTools.write_to_file(pdf_json_to_markdown_file_path, markdown_data)

        '''
        上传到 MinIO
        '''
        print(f"上传到 MinIO: ")
        minio_handler = ObjectStor_Handler()
        minio_handler.upload_file(folder_md5, md5_paperrec_folder_path)

        '''
        删除临时上传PDF文件
        '''
        os.remove(pdf_file_path)
        '''
        下载 Markdown 文件
        '''
        minio_object_prefiix = f"{folder_md5}/{pdf_json_to_markdown_name}"

        # 图片前缀
        images_prefix = f"{folder_md5}/9-image-"
        # 获取图片URL
        images_url_list = minio_handler.create_minio_multi_object_url(images_prefix)

        # 下载 Markdown 文件
        minio_handler.download_file_from_minio_by_prefix(minio_object_prefiix,
                                                         pdf_json_to_markdown_file_path)
        # 替换图片URL
        new_content = fTools.replace_urls_with_images(fTools.read_file(pdf_json_to_markdown_file_path),
                                                      Paperres_Config().image_prefix, images_url_list)
        # 将 Markdown 转换为 HTML
        html_content = markdown2.markdown(new_content)
        return render_template_string(html_content)
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Error occurred", 500
    # else:
    #     return "No PDF file uploaded", 400
    ##保存文件
    # if file:
    #     # 确保文件名是安全的，并保存文件
    #     filename = file.filename
    #     filename = os.path.splitext(os.path.basename(filename))[0]
    #     file_path = os.path.join("../data", filename)
    #     file.save(file_path)

        # 获取附加的表单数据并开始解析
        # data = request.form.get('switchState')
        # data = json.loads(data)
        # options = data['checkboxList']
        # get_option = Get_Para(options)

        # data = None
        # status = 'success'
        # try:
        #     Single_Process(file_path,middle_path,get_option[0],get_option[1],get_option[2],get_option[3])
        # except:
        #     status = 'fail'
        #     print("Process falied!")
        # else:
        #     result_path = os.path.join(middle_path, filename,"text_parts.json")
        #     with open(result_path, 'r') as file_response:
        #         data = json.load(file_response)


        #上传的json
    #     response_data = {
    #         'status': status,
    #         'message': '文件已上传',
    #         'options': options,
    #         'data':data
    #     }
    #     return jsonify(response_data)
    # else:
    #     return jsonify({'status': 'error', 'message': '未找到上传文件'}), 400


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

if __name__ == '__main__':
    app.run(debug=False)