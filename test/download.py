import os
from flask import Flask, request, Response, make_response
from flask import Flask, render_template, url_for

app = Flask(__name__)
file_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\KDD_zhanglin_Getting_LLM_to_think_and_act_like_a_human_being__Logical_path_reasoning_and_Replanning\KDD_zhanglin_Getting_LLM_to_think_and_act_like_a_human_being__Logical_path_reasoning_and_Replanning.docx'  # 设置服务器端的文件路径和文件名

def generate_file():
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


@app.route('/progress')
def download_with_progress():
    file_name = os.path.basename(file_path)  # 获取文件名
    response = custom_make_response(generate_file())
    response.headers['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(file_name.encode('utf-8').hex())
    response.headers['Content-Length'] = os.path.getsize(file_path)
    return response


@app.route('/')
def index():
    download_link = url_for('download_with_progress')  # 调用 url_for 函数生成下载链接
    return render_template(r'test/download.html', download_link=download_link)

if __name__ == '__main__':
    app.run(debug=True, port=50000)
