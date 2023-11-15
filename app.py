from flask import Flask, request
from common import res_success, get_all_params, md5_file, save_uploaded_file, res_error
import os
from sqlalchemy import create_engine, text
from flask_cors import CORS

rootpath = '\\\DESKTOP-OSKGC5P\GISDATA_share'

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


if __name__ == '__main__':
    app.run('0.0.0.0', port='5004', debug=False)
