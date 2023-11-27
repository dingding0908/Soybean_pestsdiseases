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

def res_error(data=[], msg='失败', code=500):
    if msg == '失败':
        if code == 422:
            msg = "参数错误"
        if code == 400:
            msg = "通用错误"
    return jsonify({"code": code, "msg": msg, "message": msg, "data": data})

import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from PIL import Image
def idenftify_disease(img_path):
    custom_objects={'KerasLayer': hub.KerasLayer}
    saved_model_path = r"E:\Desktop\GIT\datasciencestudy\17 DeepLearning\renn50_1123.h5"  # 将路径替换为你实际保存模型的路径
    model=keras.models.load_model(saved_model_path,custom_objects=custom_objects)
    class_names = ['Mossaic Virus','Southern blight','Sudden Death Syndrone','Yellow Mosaic','bacterial_blight','brown_spot','crestamento','ferrugen','powdery_mildew','septoria']
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    img_array1 = np.expand_dims(img_array, axis=0)
    normalization = layers.Rescaling(1 / 255.)
    images_normalized = normalization(img_array1)
    predictions = model.predict(images_normalized)
    print('predictions',predictions[0])
    max_index = np.argmax(predictions)
    return class_names[max_index]