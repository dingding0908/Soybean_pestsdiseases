import hashlib

from flask import request, jsonify
import os
def md5_file(file):
    md5 = hashlib.md5()
    while chunk := file.read(8192):  # 读取文件内容的块，以提高效率
        md5.update(chunk)
    return md5.hexdigest()
def save_uploaded_file(file, upload_folder,name):
    file.save(os.path.join(upload_folder, name))

def get_all_params():
    json_data = {}
    try:
        json_data = request.get_json() if request.get_json() else {}
    except Exception as e:
        pass
    if request.values:
        for key in request.values.keys():
            if '[]' in key:
                json_data[key[:-2]] = request.values.getlist(key)
    data = {**request.form.to_dict(), **request.args.to_dict(), **json_data}
    print(request.url, data)
    return data


def res_success(data=[], msg='成功', code=200):
    return jsonify({"code": code, "msg": msg, "message": msg, "data": data})
