import re
import csv
import logging

import numpy as np
import tensorflow as tf
# set gpu memory using parameters on the private local server
# cause keras/tf takes all avaiable gpu memory on default

# gpus = tf.config.experimental.list_physical_devices('GPU')
# if gpus:
#   try:
#     tf.config.experimental.set_virtual_device_configuration(gpus[0],
#     [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1560)])
#   except RuntimeError as error:
#       print(error)
#       pass

physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    try:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    except:
        pass # Invalid device or cannot modify virtual devices once initialized.

from keras.models import load_model
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from callback_data import car_callback

# setup logging
logging.basicConfig(level=logging.INFO)


with open('car_models.csv', newline='') as f:
    reader = csv.reader(f)
    car_models = tuple(reader)

decoder = dict(enumerate(car_models))


# NASNetLarge model trained on our dataset for target car classification
model_classifier = load_model('./models/car/')
model_classifier.compile()

# Predict the car class from user input photo
def prediction_classifier(img_array):
    return model_classifier.predict(img_array)

def prediction_decoder(preds):
    # define car names dictionary for decode prediction

    index_top_pred = np.argsort(preds[0])[-4:]


    car1 = str(decoder.get(index_top_pred[3]))[2:-6]
    car2 = str(decoder.get(index_top_pred[2]))[2:-6]
    car3 = str(decoder.get(index_top_pred[1]))[2:-6]
    car4 = str(decoder.get(index_top_pred[0]))[2:-6]



    top4_percent, top3_percent, top2_percent, top1_percent = np.sort(preds[0])[-4:]

    pred_1 = car1[:-10]+', '+'{:.1%}'.format(float(top1_percent))
    pred_2 = car2[:-10]+', '+'{:.1%}'.format(float(top2_percent))
    pred_3 = car3[:-10]+', '+'{:.1%}'.format(float(top3_percent))
    pred_4 = car4[:-10]+', '+'{:.1%}'.format(float(top4_percent))

    logging.info(f'callback_data = {pred_1, pred_2, pred_3, pred_4}')

    return (pred_1, pred_2, pred_3, pred_4, car1, car2, car3, car4), index_top_pred

def reply_markup_compiler(first_button_name,
                          second_button_name,
                          thrird_button_name,
                          fourth_button_name,
                          car1, car2, car3, car4):

    keyboard = InlineKeyboardMarkup(row_width=1)

    first = InlineKeyboardButton(text='1️⃣ '+ first_button_name,
                                 callback_data=car_callback.new(auto_name=car1))

    second = InlineKeyboardButton(text='2️⃣ '+ second_button_name,
                                 callback_data=car_callback.new(auto_name=car2))

    thrird = InlineKeyboardButton(text='3️⃣ '+ thrird_button_name,
                                 callback_data=car_callback.new(auto_name=car3))

    fourth = InlineKeyboardButton(text='4️⃣ ' + fourth_button_name,
                                 callback_data=car_callback.new(auto_name=car4))

    keyboard.add(first, second, thrird, fourth)

    return keyboard
