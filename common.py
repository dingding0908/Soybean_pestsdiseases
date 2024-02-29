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
    saved_model_path = r"E:\Desktop\GIT\datasciencestudy\17 DeepLearning\renn50_1130.h5"  # 将路径替换为你实际保存模型的路径
    model=keras.models.load_model(saved_model_path,custom_objects=custom_objects)
    class_names =np.array( ['Bacterial Pustule', 'Cifuna Locuples Walker', 'Eocanthecona', 'Frogeye Leaf Spot', 'Healthy',
                  'Larva_Spodoptera', 'Mossaic Virus', 'Red spider', 'Red_Hairy_Catterpillar', 'Southern blight',
                  'Soybean moth', 'Sudden Death Syndrone', 'Target Leaf Spot', 'Tobacco_Caterpillar', 'Yellow Mosaic',
                  'bacterialBlight', 'brown_spot', 'crestamento', 'cutworm', 'ferrugen', 'powdery_mildew', 'septoria',
                  'soybean aphid', 'soybean root rot'])
    # class_names =np.array(['Mossaic Virus','Southern blight','Sudden Death Syndrone','Yellow Mosaic','bacterial_blight','brown_spot','crestamento','ferrugen','powdery_mildew','septoria'])
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    if len(img_array.shape)==2:
        img_array=img.convert('RGB')
    img_array1 = np.expand_dims(img_array, axis=0)
    normalization = layers.Rescaling(1 / 255.)
    images_normalized = normalization(img_array1)
    predictions = model.predict(images_normalized)
    # max_index = np.argmax(predictions)
    # max=class_names[max_index]
    index = np.argsort(predictions)
    class_name=list(class_names[list(index[0][-3:])])
    predictions_value=list(predictions[0][list(index[0][-3:])])
    return class_name,predictions_value

def idenftify_crab_disease(img_path):
    custom_objects={'KerasLayer': hub.KerasLayer}
    saved_model_path = r"E:\Desktop\2024年全年\202402\08CrabidentifyHarmful\renn50_0227_v2.h5" # 将路径替换为你实际保存模型的路径
    model=keras.models.load_model(saved_model_path,custom_objects=custom_objects)
    class_names =np.array( ['BacterialEnteritis', 'BlackRottenCheeks', 'Ciliosis', 'ImmolationParalysis',
                  'Rot', 'ShellUlcer', 'Trembleness', 'WaterPong'])
    # class_names =np.array(['Mossaic Virus','Southern blight','Sudden Death Syndrone','Yellow Mosaic','bacterial_blight','brown_spot','crestamento','ferrugen','powdery_mildew','septoria'])
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    if len(img_array.shape)==2:
        img_array=img.convert('RGB')
    img_array1 = np.expand_dims(img_array, axis=0)
    normalization = layers.Rescaling(1 / 255.)
    images_normalized = normalization(img_array1)
    predictions = model.predict(images_normalized)
    # max_index = np.argmax(predictions)
    # max=class_names[max_index]
    index = np.argsort(predictions)
    class_name=list(class_names[list(index[0][-3:])])
    predictions_value=list(predictions[0][list(index[0][-3:])])
    return class_name,predictions_value


# 线性映射
def linear_mapping(x, new_min, new_max):
    # 原始范围 [0, 0.6]
    old_min, old_max = 0, 0.6

    # 新范围 [0.6, 0.7]
    a = (new_max - new_min) / (old_max - old_min)
    b = new_min - a * old_min

    # 执行映射
    mapped_value = a * x + b
    return mapped_value
