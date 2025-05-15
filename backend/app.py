import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
import pdfplumber
from collections import OrderedDict
import pytesseract
import numpy as np
from bs4 import BeautifulSoup
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sqlite3

# 设置 tesseract 路径
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # macOS 默认路径

def init_db():
    """初始化数据库，创建必要的表"""
    conn = sqlite3.connect('text_list.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS text_list (id VARCHAR PRIMARY KEY, content TEXT)')
    conn.commit()
    conn.close()

# 在应用启动时初始化数据库
init_db()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
watermark = 'Larrry想做技术大佬'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def remove_watermark(text_list, en_list, watermark):
    """移除文本中的水印，调用豆包API"""
    # 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
    # 初始化Openai客户端，从环境变量中读取您的API Key
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        #base_url="https://ark.cn-beijing.volces.com/api/v3",
        base_url=os.environ.get("BASE_URL"),
        # 从环境变量中获取您的 API Key
        api_key=os.environ.get("ARK_API_KEY"),
    )

    # 使用json.dumps()将列表转换为JSON字符串
    text_list_str = json.dumps(text_list, ensure_ascii=False)
    en_list_str = json.dumps(en_list, ensure_ascii=False)
    # Non-streaming:
    print("----- standard request -----")
    # 构造 content 内容
    content = f"""请帮我去除文本中的错误解析进去的水印文案，水印内容为：{watermark}。
    待处理文本内容为：{text_list_str}，对应的英文译文为：{en_list_str}。
    并为我返回一个json数组，要求json数组中只有文案内容，不带json的key名称，就像这样['文案1','文案2','文案3']，数组中每个元素与原始文案的元素对应。
    另外对原始文案的格式做一下美化，例如去掉不必要的空格与换行。如果中文文案字符串需要合并，请将对应的英文译文字符串也合并，最终返回一个json数组，数组中每个元素是一个对象，对象中包含中文文案和英文译文。格式如下：
    [
        {{
            "zh": "合并后的中文文案1",
            "en": "合并后的英文译文1"
        }},
        {{
            "zh": "合并后的中文文案2",
            "en": "合并后的英文译文2"
        }},
        ...
    ]，不要包含任何注释、解释或markdown代码块标记（如```json）。"""

    # 打印 content 内容
    print("即将发送给模型的 content 内容如下：")
    print(content)
    key = hashlib.md5(content.encode('utf-8')).hexdigest()
    # 先从本地sqllite数据库中查询是否存在
    conn = sqlite3.connect('text_list.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM text_list WHERE id = ?', (key,))
    result = cursor.fetchone()
    if result:
        return json.loads(result[0])
    else:
        completion = client.chat.completions.create(
            # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
            model="gpt-4o-mini",
            messages=[
            {"role": "system", "content": "你是人工智能助手，擅长处理文字内容"},
            {"role": "user", "content": content}
        ],
    )
    # 将返回的JSON字符串转换为列表
    try:
        print(completion.choices[0].message.content)
        text_list = json.loads(completion.choices[0].message.content)
        # 将text_list放入本地的sqllite数据库，并持久化至本地文件
        save_to_sqlite(key,text_list)
        return text_list
    except json.JSONDecodeError:
        print("警告：AI返回的内容不是有效的JSON格式")
        return text_list  # 如果解析失败，返回原始列表

def extract_words_from_pdf(pdf_path):
    """
    用 pdfplumber 从PDF文件中提取所有单词或词组（以分号分隔），跳过文档第一个非空行和所有以'Chapter'开头的行，并保持原始顺序去重。
    只保留全英文内容，自动去除解析错误的中文内容。
    """
    words = []
    skipped_first = False
    english_pattern = re.compile(r'^[A-Za-z0-9\s.,;:\'"?!()\-]+$')  # 只允许英文、数字、常用英文标点
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')  # 匹配任意中文字符
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                if not skipped_first and line.strip():
                    skipped_first = True
                    continue
                if line.strip().lower().startswith('chapter'):
                    continue
                items = [item.strip() for item in line.split(';')]
                for item in items:
                    if not item:
                        continue
                    # 合并多余空白
                    item = re.sub(r'\s+', ' ', item)
                    # 去除所有中文字符
                    item = re.sub(r'[\u4e00-\u9fff]', '', item)
                    item = item.strip()
                    # 过滤全为标点或长度为1的无效项
                    if all(c in ',.;:!?"\'()[]{}' for c in item) or len(item) <= 1:
                        continue
                    words.append(item)
    unique_words = list(OrderedDict.fromkeys(words))
    return unique_words

def extract_table_from_pdf(pdf_path):
    start_time = time.time()
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and any(cell and cell.strip() for cell in row):
                        en = row[0].strip() if len(row) > 0 and row[0] else ''
                        zh = row[1].strip() if len(row) > 1 and row[1] else ''
                        results.append({'en': en, 'zh': zh})
        zh_list = [result['zh'] for result in results]
        en_list = [result['en'] for result in results]
        new_results = remove_watermark(zh_list, en_list, watermark)
    elapsed = time.time() - start_time
    print(f"extract_table_from_pdf方法耗时: {elapsed:.2f}秒")
    return new_results

def save_to_sqlite(key,text_list):
    # db文件可能不存在，需要创建
    conn = sqlite3.connect('text_list.db')
    cursor = conn.cursor()
    # 创建表 id重新定义一下，将content用hash算法转化为唯一id
    cursor.execute('CREATE TABLE IF NOT EXISTS text_list (id VARCHAR PRIMARY KEY, content TEXT)')
    # 插入数据
    cursor.execute('INSERT INTO text_list (id, content) VALUES (?, ?)', (key, json.dumps(text_list)))
    conn.commit()
    conn.close() 

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 根据请求参数判断文件类型
        file_type = request.form.get('type')
        try:
            if file_type == 'vocabulary':
                words = extract_words_from_pdf(filepath)
                return jsonify({'words': words})
            elif file_type == 'translation':
                # 只允许PDF
                if not filename.lower().endswith('.pdf'):
                    return jsonify({'error': '仅支持PDF文件'}), 400
                table_data = extract_table_from_pdf(filepath)
                return jsonify({'translations': table_data})
            else:
                return jsonify({'error': f'不支持的文件类型，请指定正确的type参数'}), 400
        finally:
            # 无论成功或失败都删除文件
            if os.path.exists(filepath):
                os.remove(filepath)

@app.route('/api/submit-translation', methods=['POST'])
def submit_translation():
    start_time = time.time()
    data = request.json.get('data', [])
    # 并发获取tips
    def get_tips(item):
        # 这里建议深拷贝item或只传必要字段，避免线程间数据污染
        return get_tips_from_ai(item.get('en', ''), item.get('zh', ''), item.get('my_en_contents', ''))

    # 并发执行
    with ThreadPoolExecutor(max_workers=8) as executor:  # 8可根据CPU和API限流调整
        future_to_item = {executor.submit(get_tips, item): item for item in data}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                item['tips'] = future.result()
            except Exception as exc:
                item['tips'] = f"获取建议失败: {exc}"

    elapsed = time.time() - start_time
    print(f"submit_translation接口耗时: {elapsed:.2f}秒")
    return jsonify({'data': data})

def get_tips_from_ai(en, zh, my_en_contents):
    """
    调用豆包API，获取优化建议
    """
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        #base_url="https://ark.cn-beijing.volces.com/api/v3",
        base_url=os.environ.get("BASE_URL"),
        # 从环境变量中获取您的 API Key
        api_key=os.environ.get("ARK_API_KEY"),
    )
    # Non-streaming:
    print("----- standard request -----")
    completion = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        # model="doubao-1-5-pro-256k-250115",
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是英语语言专家"},
            {"role": "user", "content": f"你需要根据标准答案指出我的译文存在哪些问题，至少从以下几个角度，单词拼写、语法、表达方式指出问题。中文:{zh} 我的译文：{my_en_contents}. 标准答案：{en}"}
        ],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


if __name__ == '__main__':
    app.run(debug=True, port=5000) 