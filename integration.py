import os.path

from utils import *
from roboflow import Roboflow
import torch
from super_gradients.training import models


def integration(img_paths, out_folder_segment):
    data = {'value': 0, 'msg': ''}
    segment_path = get_waterrule(model, img_paths, out_folder_segment)
    img_path = os.path.dirname(segment_path[0])
    # for i in list(range(20, 100, 5))[::-1]:
    for i in list(range(0, 35, 5))[::-1]:
        CONFIDENCE_TRESHOLD = float(i / 100)
        print(CONFIDENCE_TRESHOLD)
        result_predict = list(best_model.predict(img_path, conf=CONFIDENCE_TRESHOLD, fuse_model=False))[0]
        virsionnumber(result_predict, os.path.basename(segment_path[0]))
        if len(result_predict.prediction.bboxes_xyxy) < 2:
            print(111, result_predict.prediction.bboxes_xyxy)
            continue
        else:
            print(result_predict)
            prediction_img_center, full_image = identify_number_location(result_predict)
            if len(prediction_img_center) < 2:
                data = {'value': -1, 'msg': '定位数字个数低于2！！！'}
                continue
            # OCR数字识别
            prediction_numbers = identify_img_number(prediction_img_center)
            number_list = [item['number'] for item in prediction_numbers]
            if len(number_list) < 2:
                data = {'value': -2, 'msg': '定位数字个数低于2！！！'}
                continue
            prediction_filter_numbers = filter_number(prediction_numbers)
            prediction_filter_numbers = prediction_filter_numbers[::-1]
            if len(prediction_filter_numbers) < 2:
                data = {'value': -3, 'msg': '过滤出识别数字不符合的记录,导致数值小于1！！！'}
                continue
            outpath = os.path.join(r'C:\Users\dell\Pictures\correcting_local', os.path.basename(segment_path[0]))
            mean_angle, center, h = rotation_img(prediction_filter_numbers, full_image, outpath)
            # 识别数字中心点坐标转换
            tmp = []
            for point in prediction_filter_numbers:
                tmp.append(covertPoint(point, mean_angle, center))
            gsd_list = []
            for index in range(len(tmp) - 1):
                actual_height = tmp[index]['number'] - tmp[index + 1]['number']
                pixel_height = tmp[index]['center_point'][1] - tmp[index + 1]['center_point'][1]
                gsd = calculate_ground_sample_distance(actual_height, pixel_height)
                gsd_list.append(gsd)
            average_gsd = sum(gsd_list) / len(gsd_list)
            identify_waterrule = tmp[-1]['number'] - (h - tmp[-1]['center_point'][1]) * average_gsd
            data = {'value': identify_waterrule, 'msg': 'success！！！'}
            print('222:', data)
            return data
    return data