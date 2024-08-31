import hashlib

from flask import request, jsonify
import os

from selenium.common.exceptions import TimeoutException


def md5_file(file):
    md5 = hashlib.md5()
    while chunk := file.read(8192):  # 读取文件内容的块，以提高效率
        md5.update(chunk)
    return md5.hexdigest()


def save_uploaded_file(file, upload_folder, name):
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

custom_objects = {'KerasLayer': hub.KerasLayer}
saved_model_path = r"E:\Desktop\GIT\datasciencestudy\17 DeepLearning\renn50_1130.h5"  # 将路径替换为你实际保存模型的路径
model = keras.models.load_model(saved_model_path, custom_objects=custom_objects)


def idenftify_disease(img_path):
    class_names = np.array(
        ['Bacterial Pustule', 'Cifuna Locuples Walker', 'Eocanthecona', 'Frogeye Leaf Spot', 'Healthy',
         'Larva_Spodoptera', 'Mossaic Virus', 'Red spider', 'Red_Hairy_Catterpillar', 'Southern blight',
         'Soybean moth', 'Sudden Death Syndrone', 'Target Leaf Spot', 'Tobacco_Caterpillar', 'Yellow Mosaic',
         'bacterialBlight', 'brown_spot', 'crestamento', 'cutworm', 'ferrugen', 'powdery_mildew', 'septoria',
         'soybean aphid', 'soybean root rot'])
    # class_names =np.array(['Mossaic Virus','Southern blight','Sudden Death Syndrone','Yellow Mosaic','bacterial_blight','brown_spot','crestamento','ferrugen','powdery_mildew','septoria'])
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    if len(img_array.shape) == 2:
        img_array = img.convert('RGB')
    img_array1 = np.expand_dims(img_array, axis=0)
    normalization = layers.Rescaling(1 / 255.)
    images_normalized = normalization(img_array1)
    predictions = model.predict(images_normalized)
    # max_index = np.argmax(predictions)
    # max=class_names[max_index]
    index = np.argsort(predictions)
    class_name = list(class_names[list(index[0][-3:])])
    predictions_value = list(predictions[0][list(index[0][-3:])])
    return class_name, predictions_value


def idenftify_crab_disease(img_path):
    custom_objects = {'KerasLayer': hub.KerasLayer}
    saved_model_path = r"E:\Desktop\2024年全年\202402\08CrabidentifyHarmful\renn50_0227_v2.h5"  # 将路径替换为你实际保存模型的路径
    model = keras.models.load_model(saved_model_path, custom_objects=custom_objects)
    class_names = np.array(['BacterialEnteritis', 'BlackRottenCheeks', 'Ciliosis', 'ImmolationParalysis',
                            'Rot', 'ShellUlcer', 'Trembleness', 'WaterPong'])
    # class_names =np.array(['Mossaic Virus','Southern blight','Sudden Death Syndrone','Yellow Mosaic','bacterial_blight','brown_spot','crestamento','ferrugen','powdery_mildew','septoria'])
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    if len(img_array.shape) == 2:
        img_array = img.convert('RGB')
    img_array1 = np.expand_dims(img_array, axis=0)
    normalization = layers.Rescaling(1 / 255.)
    images_normalized = normalization(img_array1)
    predictions = model.predict(images_normalized)
    # max_index = np.argmax(predictions)
    # max=class_names[max_index]
    index = np.argsort(predictions)
    class_name = list(class_names[list(index[0][-3:])])
    predictions_value = list(predictions[0][list(index[0][-3:])])
    return class_name, predictions_value


def idenftify_rice_disease(img_path):
    custom_objects = {'KerasLayer': hub.KerasLayer}
    saved_model_path = r"E:\Desktop\2024年全年\202402\09RiceIdentityHarmful\renn50_0229_v1.h5"  # 将路径替换为你实际保存模型的路径
    model = keras.models.load_model(saved_model_path, custom_objects=custom_objects)
    class_names = np.array(['bacterial_leaf_blight', 'brown_spot', 'healthy', 'leaf_blast',
                            'leaf_scald', 'narrow_brown_spot', 'neck_blast', 'rice_hispa', 'sheath_blight', 'tungro'])
    # class_names =np.array(['Mossaic Virus','Southern blight','Sudden Death Syndrone','Yellow Mosaic','bacterial_blight','brown_spot','crestamento','ferrugen','powdery_mildew','septoria'])
    img = Image.open(img_path).resize((224, 224))
    img_array = np.array(img)
    if len(img_array.shape) == 2:
        img_array = img.convert('RGB')
    img_array1 = np.expand_dims(img_array, axis=0)
    normalization = layers.Rescaling(1 / 255.)
    images_normalized = normalization(img_array1)
    predictions = model.predict(images_normalized)
    # max_index = np.argmax(predictions)
    # max=class_names[max_index]
    index = np.argsort(predictions)
    class_name = list(class_names[list(index[0][-3:])])
    predictions_value = list(predictions[0][list(index[0][-3:])])
    return class_name, predictions_value


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


# 爬虫上传百度图片，返回html字符串
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


def Getdisease(img_path):
    htmls = []
    options = Options()
    # options.add_argument("--headless")  # 使用无头模式
    driver = webdriver.Chrome(options=options,executable_path=r"D:\Users\Programs\chromedriver-win64\chromedriver.exe")
    # 访问图片上传页面
    driver.get("https://graph.baidu.com/pcpage/index?tpl_from=pc")
    # 找到上传控件
    upload = driver.find_element(By.CLASS_NAME, 'general-upload-file')
    # 上传图片
    upload.send_keys(img_path)
    html = driver.page_source
    htmls.append(html)
    # time.sleep(3)
    # print(driver.page_source)
    # 等待元素出现
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'graph-same-list-title')))
    # 获取所有的相同类名的元素
    except TimeoutException:
        print("graph-same-list-title 元素未在指定时间内出现在页面中。")
        return htmls
    elements = driver.find_elements(By.CLASS_NAME, 'graph-same-list-title')
    # driver.page_source
    # 遍历这些元素
    for i, element in enumerate(elements):
        element.click()  # 对每个元素点击
        time.sleep(3)
        # 切换到新窗口
        handles = driver.window_handles
        driver.switch_to.window(handles[-1])
        # 获取页面 html
        html = driver.page_source
        htmls.append(html)
        driver.switch_to.window(handles[0])  # 切换回原窗口，等待下一次点击
    driver.quit()
    return htmls
