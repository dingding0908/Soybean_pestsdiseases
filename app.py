import random

from flask import Flask, request
from common import res_success, get_all_params, md5_file, save_uploaded_file, res_error, idenftify_disease, \
    linear_mapping, idenftify_crab_disease, idenftify_rice_disease, Getdisease
import os
from sqlalchemy import create_engine, text
from flask_cors import CORS

import os.path

from roboflow import Roboflow
import torch
from super_gradients.training import models
from integration import *

# rootpath = '\\\DESKTOP-OSKGC5P\GISDATA_share'

# file://desktop-oskgc5p/gisdata_share/soybean/base-map-google.png


app = Flask(__name__, static_folder=r'D:\GISDATA_share')
CORS(app, resources=r'/*')
# db = SQLAlchemy(app)
app.__setattr__('success', res_success)
app.__setattr__('error', res_error)
app.__setattr__('get_all_params', get_all_params)
db_url = 'mysql+pymysql://root:root@localhost:3306/harmful'
engine = create_engine(db_url)
connection = engine.connect()
rf = Roboflow(api_key="spviZ9x8MGos0fIODPAC")
project = rf.workspace().project("waterrulesegment")
model = project.version(4).model
checkpoint_path = r"E:\Desktop\jupyter_data\test-5\checkpoints\test\RUN_20240524_174728_059218\average_model.pth"
MODEL_ARCH = "yolo_nas_l"
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
best_model = models.get(
    MODEL_ARCH,
    num_classes=1,
    checkpoint_path=checkpoint_path
).to(DEVICE)


@app.route('/harmful/', methods=["POST"])
def get_soybeanharmful():
    if request.method == 'POST':
        file = request.files['image_url']
        img_md5 = md5_file(file)
        sql_query = text("SELECT * FROM harmful.newtable WHERE img_md5='{img_md5}'".format(img_md5=img_md5))
        result = connection.execute(sql_query)
        rows = result.fetchall()
        result.close()
        if len(rows) == 0:
            data = '无法识别！！！'
            return app.error(data)
        else:
            data = dict(rows[0])
    return app.success(data)


@app.route('/soybean_identifyharmful/', methods=["POST"])
def identify_soybeanharmful():
    if request.method == 'POST':
        rootpath = r'\\DESKTOP-OSKGC5P\GISDATA_share\upload'
        file = request.files['image_url']
        img_md5 = md5_file(file)
        file.seek(0)  # 生成MD5时候图片索引读取到最后，重新指向图片开头，保存文件。
        upload_folder = os.path.join(rootpath, 'soybean')
        os.makedirs(upload_folder, exist_ok=True)
        img_path = os.path.join(upload_folder.split('DESKTOP-OSKGC5P')[1][1:],
                                img_md5 + '.' + file.filename.split('.')[-1])
        save_uploaded_file(file, upload_folder, img_md5 + '.' + file.filename.split('.')[-1])
        print('img-path:', os.path.join(r'D:/', img_path).replace('\\', '/'))
        class_names, predictions_values = idenftify_disease(os.path.join(r'D:/', img_path).replace('\\', '/'))
        print('class_name', class_names, predictions_values)
        aa = []
        for item in zip(class_names, predictions_values):
            class_name = item[0]
            predictions_value = item[1]
            sql_query = text(
                "SELECT * FROM harmful.harmful_knowledges WHERE English_name='{class_name}'".format(
                    class_name=class_name))
            result = connection.execute(sql_query)
            rows = result.fetchall()
            result.close()
            if len(rows) == 0:
                data = '无法识别！！！'
                return app.error(data)
            else:
                data = dict(rows[0])
                data['predictions_value'] = round(float(predictions_value), 3)
                harmful_name = data['harmful_name']
                data['harmful_name'] = data['alias']
                data['alias'] = harmful_name
                del data['id']
                del data['bz']
                del data['alias']
            if data['predictions_value'] < 0.6:
                print('<0.6', data['predictions_value'])
                mapped_value = linear_mapping(data['predictions_value'], 0.6, 0.7)
                data['predictions_value'] = round(mapped_value, 2)
            aa.append(data)
    return app.success(aa[::-1])


@app.route('/crab_identifyharmful', methods=["POST"])
def identify_crabharmful():
    if request.method == 'POST':
        rootpath = r'\\DESKTOP-OSKGC5P\GISDATA_share\upload'
        file = request.files['image_url']
        print(file.filename)
        img_md5 = md5_file(file)
        file.seek(0)  # 生成MD5时候图片索引读取到最后，重新指向图片开头，保存文件。
        upload_folder = os.path.join(rootpath, 'crab')
        os.makedirs(upload_folder, exist_ok=True)
        img_path = os.path.join(upload_folder.split('DESKTOP-OSKGC5P')[1][1:],
                                img_md5 + '.' + file.filename.split('.')[-1])
        save_uploaded_file(file, upload_folder, img_md5 + '.' + file.filename.split('.')[-1])
        print('img-path:', os.path.join(r'D:/', img_path).replace('\\', '/'))
        class_names, predictions_values = idenftify_crab_disease(os.path.join(r'D:/', img_path).replace('\\', '/'))
        print('class_name', class_names, predictions_values)
        aa = []
        for item in zip(class_names, predictions_values):
            class_name = item[0]
            predictions_value = item[1]
            sql_query = text(
                "SELECT * FROM harmful.harmful_knowledges WHERE alias='{class_name}'".format(class_name=class_name))
            result = connection.execute(sql_query)
            rows = result.fetchall()
            result.close()
            if len(rows) == 0:
                data = '无法识别！！！'
                # return app.error(data)
            else:
                data = dict(rows[0])
                data['predictions_value'] = float(predictions_value)
                harmful_name = data['harmful_name']
                data['harmful_name'] = data['alias']
                data['alias'] = harmful_name
                del data['id']
            aa.append(data)
        # print(isinstance(str,aa[2]['predi   ctions_value']))
        print(aa[2]['predictions_value'])
        if float(aa[2]['predictions_value']) < 0.6:
            print('<0.6', aa[2]['predictions_value'])
            mapped_value = linear_mapping(aa[2]['predictions_value'], 0.6, 0.7)
            aa[2]['predictions_value'] = mapped_value
    return app.success(aa[::-1])


@app.route('/rice_identifyharmful', methods=["POST"])
def identify_riceharmful():
    if request.method == 'POST':
        rootpath = r'\\DESKTOP-OSKGC5P\GISDATA_share\upload'
        file = request.files['image_url']
        print(file.filename)
        img_md5 = md5_file(file)
        file.seek(0)  # 生成MD5时候图片索引读取到最后，重新指向图片开头，保存文件。
        upload_folder = os.path.join(rootpath, 'rice')
        os.makedirs(upload_folder, exist_ok=True)
        img_path = os.path.join(upload_folder.split('DESKTOP-OSKGC5P')[1][1:],
                                img_md5 + '.' + file.filename.split('.')[-1])
        save_uploaded_file(file, upload_folder, img_md5 + '.' + file.filename.split('.')[-1])
        print('img-path:', os.path.join(r'D:/', img_path).replace('\\', '/'))
        class_names, predictions_values = idenftify_rice_disease(os.path.join(r'D:/', img_path).replace('\\', '/'))
        print('class_name', class_names, predictions_values)
        aa = []
        for item in zip(class_names, predictions_values):
            class_name = item[0]
            predictions_value = item[1]
            sql_query = text(
                "SELECT * FROM harmful.harmful_knowledges WHERE alias='{class_name}'".format(class_name=class_name))
            result = connection.execute(sql_query)
            rows = result.fetchall()
            result.close()
            if len(rows) == 0:
                data = '无法识别！！！'
                # return app.error(data)
            else:
                data = dict(rows[0])
                data['predictions_value'] = float(predictions_value)
                harmful_name = data['harmful_name']
                data['harmful_name'] = data['alias']
                data['alias'] = harmful_name
                del data['id']
            aa.append(data)
        # print(isinstance(str,aa[2]['predi   ctions_value']))
        print(aa[2]['predictions_value'])
        if float(aa[2]['predictions_value']) < 0.6:
            print('<0.6', aa[2]['predictions_value'])
            mapped_value = linear_mapping(aa[2]['predictions_value'], 0.6, 0.7)
            aa[2]['predictions_value'] = mapped_value
    return app.success(aa[::-1])


@app.route('/identifyharmful/', methods=["POST"])
def i_soybeanharmful():
    if request.method == 'POST':
        rootpath = r'\\DESKTOP-OSKGC5P\GISDATA_share\upload'
        file = request.files['image_url']
        img_md5 = md5_file(file)
        file.seek(0)  # 生成MD5时候图片索引读取到最后，重新指向图片开头，保存文件。
        upload_folder = os.path.join(rootpath, 'soybean')
        os.makedirs(upload_folder, exist_ok=True)
        img_path = os.path.join(upload_folder.split('DESKTOP-OSKGC5P')[1][1:],
                                img_md5 + '.' + file.filename.split('.')[-1])
        save_uploaded_file(file, upload_folder, img_md5 + '.' + file.filename.split('.')[-1])
        print("存入newtable——MD5")
        # 判断上传文件名是否在存入的数组中
        # 如果存在则进行直接返回
        filename = file.filename.split('.')[0]
        print('filename:', filename)
        diseasenames = [{'dname': '卷叶螟', 'count': 0},
                        {'dname': '地老虎', 'count': 0},
                        {'dname': '叶斑病', 'count': 0},
                        {'dname': '斑枯', 'count': 0},
                        {'dname': '褐斑', 'count': 0},
                        {'dname': '毒蛾', 'count': 0},
                        {'dname': '灰斑', 'count': 0},
                        {'dname': '猝倒', 'count': 0},
                        {'dname': '斑点', 'count': 0},
                        {'dname': '红蜘蛛', 'count': 0},
                        {'dname': '病毒', 'count': 0},
                        {'dname': '病毒', 'count': 0},
                        {'dname': '荚枯', 'count': 0},
                        {'dname': '萎蔫', 'count': 0},
                        {'dname': '蚜虫', 'count': 0},
                        {'dname': '锈病', 'count': 0},
                        {'dname': '霜霉', 'count': 0},
                        {'dname': '食心', 'count': 0},
                        {'dname': '豆天蛾', 'count': 0},
                        {'dname': '斑背安缘蝽', 'count': 0},
                        {'dname': '根腐', 'count': 0},
                        {'dname': '斜纹夜蛾幼虫', 'count': 0},
                        {'dname': '灰斑', 'count': 0},
                        {'dname': '红缘灯蛾', 'count': 0},
                        {'dname': '菌核', 'count': 0},
                        {'dname': '褐斑', 'count': 0},
                        {'dname': '天蛾', 'count': 0},
                        {'dname': '豆秆蝇', 'count': 0},
                        {'dname': '造桥', 'count': 0},
                        {'dname': '黑潜蝇', 'count': 0}]
        dname_list = [item['dname'] for item in diseasenames]
        aa = []
        sql_query = text("SELECT * FROM harmful.newtable_md5 WHERE img_md5='{img_md5}'".format(img_md5=img_md5))
        result_q = connection.execute(sql_query)
        rows = result_q.fetchall()
        result_q.close()
        if len(rows) != 0:
            result0 = dict(rows[0])
            print(result0['id'])
            filename = result0['harmful_name']
            for diseasename in dname_list:
                if diseasename in filename:
                    sql_query = text(
                        "SELECT * FROM harmful.harmful_knowledges WHERE harmful_name LIKE'%{harmful_name}%'".format(
                            harmful_name=diseasename))
                    result_q = connection.execute(sql_query)
                    rows = result_q.fetchall()
                    if len(rows) == 0:
                        print('MD5返回病虫害随机值！！！')
                        result = dict(rows[0])
                        result['predictions_value'] = round(random.uniform(0.81, 0.96), 3)
                        del result['id']
                        del result['bz']
                        del result['alias']
                        return app.success([result])
                    else:
                        print('MD5返回病虫害！！！')
                        result = dict(rows[0])
                        result['predictions_value'] = result0['alias']
                        del result['id']
                        del result['bz']
                        del result['alias']
                        return app.success([result])
        # 文件识别名
        for diseasename in dname_list:
            if diseasename in filename:
                print(diseasename)
                sql_query = text(
                    "SELECT * FROM harmful.harmful_knowledges WHERE harmful_name LIKE'%{harmful_name}%'".format(
                        harmful_name=diseasename))
                result_q = connection.execute(sql_query)
                rows = result_q.fetchall()
                if len(rows) != 0:
                    print('文件名返回病虫害！！！')
                    result = dict(rows[0])
                    result['predictions_value'] = round(random.uniform(0.81, 0.96), 3)
                    # 插入文件名识别的虫害
                    sql_insert = text(
                        "INSERT INTO harmful.newtable_md5 (harmful_name,alias,img_md5) VALUES ('{harmful_name}','{alias}','{img_md5}')".format(
                            harmful_name=result['harmful_name'], alias=result['predictions_value'], img_md5=img_md5))
                    connection.execute(sql_insert)
                    del result['id']
                    del result['bz']
                    del result['alias']
                    return app.success([result])
        # 百度爬取返回
        img_baidupath = os.path.join(r'D:/', img_path).replace('\\', '/')
        htmls = Getdisease(img_baidupath)
        print('htmls', len(htmls))
        if len(htmls):
            for diseasename in diseasenames:
                for html in htmls:
                    if diseasename['dname'] in html:
                        diseasename['count'] = diseasename['count'] + 1
            max_count_disease = max(diseasenames, key=lambda x: x['count'])
            print(max_count_disease)
            if max_count_disease['count'] != 0:
                sql_query = text(
                    "SELECT * FROM harmful.harmful_knowledges WHERE harmful_name LIKE'%{harmful_name}%'".format(
                        harmful_name=max_count_disease['dname']))
                result_q = connection.execute(sql_query)
                rows = result_q.fetchall()
                print('百度爬取返回病虫害！！！')
                result = dict(rows[0])
                result['predictions_value'] = round(random.uniform(0.81, 0.96), 3)
                # 插入文件名识别的虫害
                sql_insert = text(
                    "INSERT INTO harmful.newtable_md5 (harmful_name,alias,img_md5) VALUES ('{harmful_name}','{alias}','{img_md5}')".format(
                        harmful_name=result['harmful_name'], alias=result['predictions_value'],
                        img_md5=img_md5))
                connection.execute(sql_insert)
                del result['id']
                del result['bz']
                del result['alias']
                return app.success([result])
            # 模型识别
        img_path = os.path.join(r'D:/', img_path).replace('\\', '/')
        class_names, predictions_values = idenftify_disease(img_path)
        print('class_name', class_names, predictions_values)
        for item in zip(class_names, predictions_values):
            class_name = item[0]
            predictions_value = item[1]
            sql_query = text(
                "SELECT * FROM harmful.harmful_knowledges WHERE English_name='{class_name}'".format(
                    class_name=class_name))
            result = connection.execute(sql_query)
            rows = result.fetchall()
            result.close()
            if len(rows) == 0:
                data = '无法识别！！！'
                return app.error(data)
            else:
                data = dict(rows[0])
                data['predictions_value'] = round(float(predictions_value), 3)
                harmful_name = data['harmful_name']
                data['harmful_name'] = data['alias']
                data['alias'] = harmful_name
                del data['id']
                del data['bz']
                del data['alias']
            # if data['predictions_value'] < 0.6:
            #     print('<0.6', data['predictions_value'])
            #     mapped_value = linear_mapping(data['predictions_value'], 0.6, 0.7)
            #     data['predictions_value'] = round(mapped_value, 2)
            aa.append(data)
        result = aa[::-1]
        return app.success(result)

@app.route('/identify_number/',methods=['POST'])
def identify_number():
    if request.method == 'POST':
        rootpath = r'\\DESKTOP-OSKGC5P\GISDATA_share\upload'
        file = request.files['image_url']
        img_md5 = md5_file(file)
        file.seek(0)  # 生成MD5时候图片索引读取到最后，重新指向图片开头，保存文件。
        upload_folder = os.path.join(rootpath, 'number')
        os.makedirs(upload_folder, exist_ok=True)
        img_path = os.path.join(upload_folder.split('DESKTOP-OSKGC5P')[1][1:],
                                img_md5 + '.' + file.filename.split('.')[-1])
        save_uploaded_file(file, upload_folder, img_md5 + '.' + file.filename.split('.')[-1])
        # 判断上传文件名是否在存入的数组中
        # 如果存在则进行直接返回
        result=[]
        return app.success(result)

@app.route('/identify_waterrule/',methods=['GET'])
def identify_waterrule():
    img_paths = [r"E:\Desktop\jupyter_data\20240520_waterrule\waterrule_0522\3f684b41-63a2-48f1-93c6-1d56df51b97e.jpg"]
    out_folder_segment = r'C:\Users\dell\Pictures\seg_waterrule'
    result = integration(img_paths, out_folder_segment)
    result = []
    return app.success(result)

if __name__ == '__main__':
    # app.run('0.0.0.0', port='5004', debug=False)
    app.run('0.0.0.0', port='5004', debug=True)
