from flask import Flask, request, render_template, jsonify, redirect, url_for
import pandas as pd
from werkzeug.utils import secure_filename
import os
from apk_analysis import extract_apk_info
import joblib
from urllib.parse import urlencode
from pathlib import Path


app = Flask(__name__, template_folder='templates')
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
best_model = joblib.load('best_model.joblib')
vectorizer = joblib.load('vectorizer.joblib')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 直接从服务器的固定路径读取CSV文件
    file_path = "D:\\徐凯娟2\Demo\Demo\src\main\\resources\\upload\downloaded_urls.csv"

    # 读取上传的CSV文件并获取URL列表
    test_urls_df = pd.read_csv(file_path, usecols=['url'])
    test_urls = test_urls_df['url'].tolist()

    test_urls_df = pd.read_csv(file_path, usecols=['url'])
    test_urls = test_urls_df['url'].tolist()

    # 进行预测并处理结果
    test_urls_vec = vectorizer.transform(test_urls)
    test_pred = best_model.predict(test_urls_vec)
    predicted_black = [url for url, pred in zip(test_urls, test_pred) if pred == "black"]  # 假设1表示黑名单

    # 返回结果页面或JSON响应
    if predicted_black:
        return render_template('result.html', results=predicted_black, color='Black')
    else:
        return render_template('result.html', results=[], color='White')
    # 或者返回JSON响应：return jsonify({'results': predicted_black, 'color': 'Black'})


    return render_template('index1.html')


@app.route('/show-result', methods=['GET'])
def show_result():
    data = request.args.get('data')  # 获取URL中的查询参数'data'
    # 在这里处理数据，比如解析和呈现给用户
    return  data

@app.route('/upload-apk', methods=['POST'])
def upload_apk():
    if 'apkFile' not in request.files:
        return "错误：没有文件部分", 400
    file = request.files['apkFile']
    if file.filename == '':
        return "错误：没有选择文件", 400
    if file:
        # 保存文件到临时目录
        temp_dir = os.path.join(app.root_path, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)

        # 提取 APK 信息
        info = extract_apk_info(file_path)

        # 清除临时文件
        os.remove(file_path)

        # 使用url_for生成结果页面的URL，并附加查询参数
        return render_template('results.html', info=info)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index1')
def page1():
    return render_template('index1.html')

@app.route('/index2')
def page2():
    return render_template('index2.html')

@app.route('/index3')
def page3():
    return render_template('index3.html')

if __name__ == '__main__':
    app.run(debug=True)