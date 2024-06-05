# 环境安装
python版本>=3.10  
>conda create -n PaperRec python=3.10  
conda activate PaperRec

安装库：  
>pip install openai  
pip install pypiwin32  
pip install pymupdf         导入库名为fitz  
pip install pillow          导入库名为PIL  
pip install pdfminer.six  
pip install PyPDF2  
pip install pdfplumber  
pip install pdf2image  
pip install pytesseract  
pip install python-docx  
pip install regex  






# 主体文件结构：  
>Agents------|  大模型Agents  
>abandon------|  废弃文件  
>output------|  中间文件保存    
>- pdf_name_file------|
 >  - images       
  >  - images_informations.json
  >  - text.txt  
>- ...
>
>test ------|测试功能模块文件夹  
utils------|功能模块 
>- MatchImages.py  匹配图片与文本
>- pdfGetImage.py  切割pdf中图片
>- Prompts.py  Agents中使用的prompts
>- pdfImagesInfo.py  搜索pdf中图片信息
>- Structed_extraction.py 结构化处理pdf文本
>- CalculateRank3.py 筛选参考文献
>- ExtractRef.py  筛选参考文献
>
>data ------|pdf原始文件夹  
Configration.py  ------|全局参数设置  
main.py  ------|功能总和

# 运行
>## 首先填写api密钥 
>## 下载poppler库放入当前路径的"dependence"文件夹中,下载路径：
>## 一、单独pdf操作情况
>- 执行main.py选择操作的pdf文件  
>## 二、批量处理情况
>- 将pdf文件放入当前目录data文件夹中(已放有resnet.pdf作为参考)
>- 执行main_batch.py文件