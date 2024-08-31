import os
import numpy as np
import base64
import shutil
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
from tqdm import tqdm
import numpy as np
import cv2
import pytesseract as pt
from collections import Counter
from PIL import Image
import pytesseract as pt
import re
import math


def mask_image(path, image_name, base64_str, out_folder):
    os.chdir(os.path.dirname(path))
    np_data = np.fromstring(base64.b64decode(base64_str), np.uint8)
    mask = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    image = cv2.imread(path)
    image_size = image.shape[1::-1]
    mask_size = mask.shape[1::-1]
    mask = cv2.resize(mask, image_size)
    masked = cv2.bitwise_and(image, image, mask=mask)
    alpha = 100 / 100
    masked = cv2.addWeighted(masked, alpha, image, 1 - alpha, 0)
    # 裁剪最小区域
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    coords = np.argwhere(gray > 0)
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0)
    cropped = masked[x_min:x_max + 1, y_min:y_max + 1]
    if not os.path.exists(os.path.join(out_folder, image_name.split('.')[0])):
        os.makedirs(os.path.join(out_folder, image_name.split('.')[0]))
    cv2.imwrite(os.path.join(os.path.join(out_folder, image_name.split('.')[0]), image_name), cropped)
    shutil.copy(os.path.join(os.path.join(out_folder, image_name.split('.')[0]), image_name),
                os.path.join(os.path.join(out_folder, image_name.split('.')[0]), 'copy_' + image_name))
    return os.path.join(os.path.join(out_folder, image_name.split('.')[0]), image_name)


import warnings

warnings.filterwarnings('ignore')
from glob import glob
from tqdm import tqdm
import cv2
import os


def get_waterrule(model, img_paths, out_folder=r'C:\Users\dell\Pictures\seg_waterrule'):
    result = []
    for path in img_paths:
        save_name = os.path.basename(path)
        tmp = model.predict(path)
        base64_str = tmp[0]['segmentation_mask']
        out_img = mask_image(path=path, image_name=save_name, base64_str=base64_str,
                             out_folder=r'C:\Users\dell\Pictures\seg_waterrule')
        result.append(out_img)
    return result


from collections import Counter


def find_mode(array):
    counter = Counter(array)
    max_count = max(list(counter.values()))
    mode_val = [num for num, freq in counter.items() if freq == max_count]
    if len(mode_val) == len(array):
        print("No mode found")
    else:
        return mode_val


def scaleIamge(img_path):
    result = {'value': 0, 'msg': ''}
    img = cv2.cvtColor(img_path, cv2.COLOR_RGB2BGR)
    txt_number = []
    for scale in tqdm(range(100)):
        scale = float((scale + 10) / 10)
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        ret, img_resized = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # 进行OCR识别
        txt = pt.image_to_string(img_resized, config="--psm 7 -c tessedit_char_whitelist=0123456789")
        try:
            txt_number.append(int(txt.replace(')\n', '')))
        except:
            continue
        if isinstance(find_mode(txt_number), int):
            result['value'] = find_mode(txt_number)
            result['msg'] = '识别成功！！！'
        else:
            result['value'] = -1
            result['msg'] = '识别失败！！！'
    return result


def identify_number_location(result_prediction):
    result = []
    height, width = result_prediction.image.shape[:2]
    for bbox in result_prediction.prediction.bboxes_xyxy:
        data_dict = {'center_point': [], 'img': np.zeros([2, 3])}
        x1, y1, x2, y2 = map(int, bbox)
        # 如果x1小于0，将其设定为0
        x1 = max(0, x1)
        # x1 =  min(width, x1)
        # 如果y1小于0，将其设定为0
        y1 = max(0, y1)
        # 如果x2大于宽度，将其设定为图像的宽度
        x2 = min(width, x2)
        # 如果y2大于高度，将其设定为图像的高度
        y2 = min(height, y2)
        print('裁剪长宽高：', x1, y1, x2, y2, height, width)
        cropped_image = result_prediction.image[y1:y2, x1:x2]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        data_dict['center_point'] = [center_x, center_y]
        data_dict['img'] = cropped_image
        result.append(data_dict)
    return result, result_prediction.image


pt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def identify_img_number(number_imgs):
    aa = []
    for index, number_img in enumerate(number_imgs):
        number_ocr = {'number': 0, 'center_point': []}
        cropped_image_pil = Image.fromarray(number_img['img'])
        # 使用pytesseract的image_to_string()方法从图像中提取文本
        text = pt.image_to_string(cropped_image_pil, config="--psm 7 -c tessedit_char_whitelist=0123456789")
        # 使用正则表达式查找所有的数字
        number = re.findall(r'\d+', text)
        if len(number) != 0 & len(aa) > 1:
            if len(aa) > 1 & int(number[0]) > aa[-1]['number']:
                # 缩减或者扩大范围重新识别新处理的图片进行识别数字
                tmp = scaleIamge(number_img['img'])
                print("tmp[value]", tmp['value'], aa[-1])
                if tmp['value'] > aa[-1]['number']:
                    continue
                else:
                    number[0] = tmp['value']
            number_ocr['number'] = int(number[0])
            number_ocr['number'] = int(number[0])
            number_ocr['center_point'] = number_img['center_point']
        aa.append(number_ocr)
    return aa


def filter_number(number_ocr_list):
    # 过滤识别的数字对不符合的数字过滤删除
    result = []
    number_list = [item['number'] for item in number_ocr_list]
    numbers = list(range(5, 900, 5))
    for index, item in enumerate(number_list):
        if item in numbers:
            result.append(number_ocr_list[index])
    if len(result) < 2:
        return []
    else:
        return result


def covertPoint(point, mean_angle, center):
    x1, y1 = point['center_point']
    x_center, y_center = center
    a = math.radians(mean_angle)
    x2 = (x1 - x_center) * math.cos(a) + (y1 - y_center) * math.sin(a) + x_center
    y2 = (x1 - x_center) * math.sin(a) + (y1 - y_center) * math.cos(a) + y_center
    point['center_point'] = (x2, y2)
    return point


def getangle(p1, p2):
    if p1[0] == p2[0]:  # 处理除数为0的情况
        slope = float('inf')
    else:
        slope = (p2[1] - p1[1]) / (p2[0] - p1[0])

    # 计算这条线与垂直线的夹角（单位为度）
    if slope != float('inf'):
        angle_to_rotate = math.degrees(math.atan(1 / slope))  # atan表示求反正切
    else:
        angle_to_rotate = 90  # 如果斜率为无穷，那么这条线已经垂直

    # 为正确旋转到垂直位置，将右侧的点的y值与左侧的对比，如果右侧的点位于左侧的点的下方，那么需要逆时针旋转，否则就需要顺时针旋转
    if angle_to_rotate != 90:  # 如果线已经垂直，就不需要进一步旋转
        if (p2[1] > p1[1] and p2[0] > p1[0]) or (p2[1] < p1[1] and p2[0] < p1[0]):
            angle_to_rotate = -angle_to_rotate  # 逆时针旋转
    return -angle_to_rotate


def rotation_img(result, full_image, outpath):
    img = cv2.cvtColor(full_image, cv2.COLOR_RGB2BGR)
    (h, w) = img.shape[:2]
    center = (w / 2, h / 2)
    angles = []
    for index in range(len(result) - 1):
        p1, p2 = result[index]['center_point'], result[index + 1]['center_point']
        angle = getangle(p1, p2)
        angles.append(angle)
    mean_angle = sum(angles) / len(angles)
    M = cv2.getRotationMatrix2D(center, mean_angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h))
    cv2.imwrite(outpath, rotated)
    return (mean_angle, center, h)


def calculate_ground_sample_distance(actual_height, pixel_height):
    return -actual_height / pixel_height


# 可视化水位尺数值
def virsionnumber(version, image_name):
    # 假设img是你的图片数据，predictions是你的预测结果
    img = version.image
    # 创建一个副本
    img_copy = np.copy(img)

    # 将 BGR 图片转换为 RGB 图片用于显示
    # img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)

    # 获取预测结果中的箱子数据
    bboxes = version.prediction.bboxes_xyxy

    for bbox in bboxes:
        # 获取bbox的坐标
        start_point = (int(bbox[0]), int(bbox[1]))
        end_point = (int(bbox[2]), int(bbox[3]))
        # 绘制矩形框到图片上
        img_copy = cv2.rectangle(img_copy, start_point, end_point, (0, 0, 255), 3)
    if not os.path.exists(os.path.join(r"C:\Users\dell\Pictures\version_waterrule", image_name.split('.')[0])):
        os.makedirs(os.path.join(r"C:\Users\dell\Pictures\version_waterrule", image_name.split('.')[0]))
    plt.imshow(img_copy)
    plt.savefig(os.path.join(r"C:\Users\dell\Pictures\version_waterrule", image_name.split('.')[0], image_name))
    plt.imshow(img_copy)
    # 利用 matplotlib 来显示图片

    # plt.show()
