from flask import Flask, request
from common import res_success, get_all_params, md5_file, save_uploaded_file
import os
from sqlalchemy import create_engine, text
from flask_cors import CORS

rootpath = '\\\DESKTOP-OSKGC5P\GISDATA_share'

# file://desktop-oskgc5p/gisdata_share/soybean/base-map-google.png


app = Flask(__name__, static_folder=r'D:\GISDATA_share')
CORS(app, resources=r'/*')
# db = SQLAlchemy(app)
app.__setattr__('success', res_success)
app.__setattr__('get_all_params', get_all_params)
db_url = 'mysql+pymysql://root:root@localhost:3306/harmful'
engine = create_engine(db_url)
connection = engine.connect()


@app.route('/harmful/', methods=["POST"])
def get_soybeanharmful():
    if request.method == 'POST':
        param = app.get_all_params()
        file = request.files['image_url']
        img_md5 = md5_file(file)
        # file.seek(0)  # 生成MD5时候图片索引读取到最后，重新指向图片开头，保存文件。
        # upload_folder = os.path.join(rootpath, 'soybean')
        # os.makedirs(upload_folder, exist_ok=True)
        # img_path = os.path.join('\\'+upload_folder.split('DESKTOP-OSKGC5P')[1], img_md5 + '.' + file.filename.split('.')[-1])
        # save_uploaded_file(file, upload_folder, img_md5 + '.' + file.filename.split('.')[-1])
        # param['harmful_file'] = img_path[2:].replace('\\', '/')
        # if 'harmful_name' not in param.keys():
        #     param['harmful_name'] = '未命名'
        # if 'precaution' not in param.keys():
        #     param['precaution'] = '默认预防措施'
        # if 'alias' not in param.keys():
        #     param['alias'] = '默认中文名'
        # if 'introduction' not in param.keys():
        #     param['introduction'] = '简介'
        # if 'symptoms' not in param.keys():
        #     param['symptoms'] = '症状'
        # if 'reason' not in param.keys():
        #     param['reason'] = '原因'
        sql_query = text("SELECT * FROM harmful.newtable WHERE img_md5='{img_md5}'".format(img_md5=img_md5))
        result = connection.execute(sql_query)
        rows = result.fetchall()
        result.close()
        if not rows:
            sql_insert = text(
                "INSERT INTO harmful.newtable (harmful_name, alias,introduction,symptoms,reason,img_path,img_md5,precaution) VALUES ('{harmful_name}','{alias}','{introduction}','{symptoms}','{reason}','{img_path}','{img_md5}','{precaution}')".format(
                    harmful_name=param['harmful_name'], img_path=param['harmful_file'], img_md5=img_md5,
                    precaution=param['precaution'], alias=param['alias'], introduction=param['introduction'],
                    symptoms=param['symptoms'], reason=param['reason']))
            connection.execute(sql_insert)
            data = param
        else:
            data = dict(rows[0])
    return app.success(data)


if __name__ == '__main__':
    app.run('0.0.0.0', port='5004', debug=True)
