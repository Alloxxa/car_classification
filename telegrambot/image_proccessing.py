import os
import numpy as np
from PIL import Image
from keras.preprocessing.image import img_to_array


num_path = './digits' # Путь к файлу с цифрами.
path = './output_car_classes' # Путь к файлу с фотографиями.


def img_preproccessing(photo_path):
    img = Image.open(photo_path)
    max_size = max(img.size)
    new_size = (max_size, max_size)
    new_im = Image.new("RGB", new_size)
    new_im.paste(img, (round((new_size[0]-img.size[0])/2),round((new_size[1]-img.size[1])/2)))
    new_im = new_im.resize((331,331))
    _img_arr = img_to_array(new_im)  # Numpy array with shape (331, 331, 3)
    _img_arr = _img_arr.reshape((1,) + _img_arr.shape)  # Numpy array with shape (1, 331, 331, 3)
    _img_arr /= 255 # Rescale by 1/255
    return _img_arr


def framed_concat(img_1, img_2, img_3, img_4, A, B, C):

    # Функция получает на вход 4 np-массива и параметры желаемого изображения:
    # А - ширина каждого изображения (width)
    # B - высота каждого изображения (height)
    # С - ширина рамки (frame_width)

    first_row = np.concatenate((np.zeros((B, C, 3), dtype='int'),
                            img_1, np.zeros((B, C, 3), dtype='int'),
                            img_2, np.zeros((B, C, 3), dtype='int')), axis=1)

    second_row = np.concatenate((np.zeros((B, C, 3), dtype='int'),
                                 img_3, np.zeros((B, C, 3), dtype='int'),
                                 img_4, np.zeros((B, C, 3), dtype='int')), axis=1)

    picture = np.concatenate((np.zeros((C, 2*A + 3*C, 3), dtype='int'),
                              first_row, np.zeros((C, 2*A + 3*C, 3), dtype='int'),
                              second_row, np.zeros((C, 2*A + 3*C, 3), dtype='int')))
    return picture

def photos_in_frame (height:int, width:int, frame_width:int, directory_path, *fnames):

    # Функция приводит 4 фотографии к размерам width, height,
    # на выход выдает соединенное изображение 4-х фотографий с рамкой (frame_width)
    # и номерами в формате изображения библиотеки PIL.

    img_1, img_2, img_3, img_4 = [Image.open(os.path.join(directory_path, fname)) for fname in fnames[:4]]
    img_1 = img_1.resize((width, height))
    img_2 = img_2.resize((width, height))
    img_3 = img_3.resize((width, height))
    img_4 = img_4.resize((width, height))
    num_1, num_2, num_3, num_4 = [Image.open(os.path.join(num_path, fname)) for
                                  fname in sorted(os.listdir(num_path))[:4]]

    min_dim = min(width, height)
    step = 30 # ~ 1 / (отступ квадрата с цифрой от края рамки)

    num_1 = num_1.resize((min_dim // 5, min_dim // 5))
    img_1.paste(num_1, (width - min_dim//step - num_1.size[0], height - min_dim//step - num_1.size[1]))

    num_2 = num_2.resize((min_dim // 5, min_dim // 5))
    img_2.paste(num_2, (width - min_dim//step - num_2.size[0], height - min_dim//step - num_2.size[1]))

    num_3 = num_3.resize((min_dim // 5, min_dim // 5))
    img_3.paste(num_3, (width - min_dim//step - num_3.size[0], height - min_dim//step - num_3.size[1]))

    num_4 = num_4.resize((min_dim // 5, min_dim // 5))
    img_4.paste(num_4, (width - min_dim//step - num_4.size[0], height - min_dim//step - num_4.size[1]))

    #next work with numpy
    img_1 = np.array(img_1)
    img_2 = np.array(img_2)
    img_3 = np.array(img_3)
    img_4 = np.array(img_4)

    return Image.fromarray(np.uint8(framed_concat(img_1, img_2, img_3, img_4, width, height, frame_width)))
