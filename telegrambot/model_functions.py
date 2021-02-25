import re
import numpy as np

# set gpu memory using parameters on the private local server
# cause keras/tf takes all avaiable gpu memory on default
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    tf.config.experimental.set_virtual_device_configuration(gpus[0],
    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1560)])
  except RuntimeError as error:
    print(error)

from keras.models import load_model

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from callback_data import car_callback

from car_dict import CAR_DICT


# NASNetLarge model trained on our dataset for target car classification
model_classifier = load_model('./models/car/')
model_classifier.compile()

# Predict the car class from user input photo
def prediction_classifier(img_array):
    return model_classifier.predict(img_array)

def prediction_decoder(preds):
    # define car names dictionary for decode prediction
    decoder = CAR_DICT

    index_top_pred = np.argsort(preds[0])[-4:]

    car1 = decoder.get(index_top_pred[3])
    car2 = decoder.get(index_top_pred[2])
    car3 = decoder.get(index_top_pred[1])
    car4 = decoder.get(index_top_pred[0])

    top1_percent = np.sort(preds[0])[-1]
    top2_percent = np.sort(preds[0])[-2]
    top3_percent = np.sort(preds[0])[-3]
    top4_percent = np.sort(preds[0])[-4]

    pred_1 = car1[:-10]+', '+'{:.1%}'.format(float(top1_percent))
    pred_2 = car2[:-10]+', '+'{:.1%}'.format(float(top2_percent))
    pred_3 = car3[:-10]+', '+'{:.1%}'.format(float(top3_percent))
    pred_4 = car4[:-10]+', '+'{:.1%}'.format(float(top4_percent))

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
