import os, json, random
import cv2
import numpy as np
import torch, torchvision
import detectron2
from detectron2.utils.logger import setup_logger
from PIL import Image
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog


# setup_logger()

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
# Find a model from detectron2's model zoo
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)

def car_inspector(path_to_file, detected_path, cropped_path):
    # detection of all objects on the photo
    img = cv2.imread(path_to_file)
    outputs = predictor(img)
    v = Visualizer(img[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2.imwrite(detected_path, out.get_image()[:, :, ::-1])

    bound_area = (outputs["instances"].pred_boxes.area().tolist())
    bound_classes = (outputs["instances"].pred_classes.tolist())
    num_cars = sum([bound_class==2 for bound_class in bound_classes])
    little_car = True
    if num_cars > 0:

        biggest_area = sorted(bound_area)[-1]
        big_area = biggest_area*0.7 # to take bounding box with area 70% and bigger of the biggest area detected

        # cars_positions = []
        # for i in range(len(bound_classes)):
        #     if str(bound_classes[i]) == '2':
        #         cars_positions.append(i)
        #         print('cars: ', cars_positions)

        detected_car = []
        for j in range(len(bound_classes)):
            if str(bound_classes[j]) == '2':
                if bound_area[j] > big_area:
                    little_car = False
                    index_area = (j, bound_area[j])
                    detected_car.append(index_area)
                    print('detected_car: ', detected_car)
                else:
                    print('so LITTLE car here!')

        if little_car == False:
            biggest_car = max(detected_car, key=lambda index_area:index_area[1])
            print(biggest_car)
            mask = outputs["instances"].pred_boxes[biggest_car[0]]
            mask = mask.tensor.tolist()

            x = int(float(mask[0][0]))
            y = int(float(mask[0][1]))
            w = int(float(mask[0][2]))
            h = int(float(mask[0][3]))

            croped_car = Image.open(path_to_file)
            croped_car = croped_car.crop((x, y, w, h)).save(cropped_path)

    return num_cars, little_car
