import os
import re

from PIL import Image
import requests
import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, executor, types

from image_proccessing import img_preproccessing
from image_proccessing import photos_in_frame
from model_functions import prediction_classifier
from model_functions import prediction_decoder
from model_functions import reply_markup_compiler
from detection import car_inspector
from car_classes import car_description

# Static text of ignoring not target user message types
from text_templates import NOT_TARGET_CONTENT_TYPES, HELLO_TEXT, WAITING_TEXT
from text_templates import NOT_TARGET_TEXT, ERROR_NOT_CAR, ERROR_LITTLE_CAR, HINT_TEXT

# Make sure that u got telegram api token from @BotFather
TOKEN = os.getenv('TELEGRAM_API_TOKEN_CARBOT')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Base command messages for start and exceptions (not target content inputs)
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    text = HELLO_TEXT %user_name
    await message.reply(text)

@dp.message_handler(content_types=NOT_TARGET_CONTENT_TYPES)
async def handle_docs_photo(message):
    user_name = message.from_user.first_name
    text = NOT_TARGET_TEXT %user_name
    await message.reply(text)


# Main functions of this bot with target content type of message
@dp.message_handler(content_types=['photo'])
async def handle_photo_for_prediction(message):
    chat_id = message.chat.id

    # check for 'single photo - single message'
    # None media_group_id - means single photo at message
    if message.media_group_id is None:
        ### Get user's variables
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        message_id = message.message_id

        text = WAITING_TEXT %user_name
        await bot.send_message(chat_id, text)

        # define input photo local path
        photo_name = './input/carphoto_%s_%s.jpg' %(user_id, message_id)
        await message.photo[-1].download(photo_name) # extract photo for further procceses

        ### Detection of car on photo with Detectron2

        # output photo local path
        detection_photo_name = './output/detection/photo_%s_%s.jpg' %(user_id, message_id)
        cropped_photo_name = './output/detection/detected_car_photo_%s_%s.jpg' %(user_id, message_id)
        # detector predictions
        num_cars, little_car = car_inspector(photo_name, detection_photo_name, cropped_photo_name)

        # Find proper car bounding box for futher manipulations
        if num_cars == 0:

            logging.info(f'call "car_inspection_results" = {num_cars} - it means: no car here!')
            #it means - no proper car on the photos
            # error message for notcar input photo
            await message.reply(ERROR_NOT_CAR)
            await bot.send_photo(chat_id, photo=open(detection_photo_name, 'rb'))

        # car inspector found the car!
        else:
            # set output path for internal use

            if little_car == True:
                await message.reply(ERROR_LITTLE_CAR)
                await bot.send_photo(chat_id, photo=open(detection_photo_name, 'rb'))
            else:
                await message.reply('Смотри-ка! Мы нашли её!')
                await bot.send_photo(chat_id, photo=open(detection_photo_name, 'rb'))
                await bot.send_photo(chat_id, photo=open(cropped_photo_name, 'rb'))

                ### Main car classifier prediction below
                img_array = img_preproccessing(cropped_photo_name)
                preds = prediction_classifier(img_array) # raw predictions from keras model

                # Massive prediction extraction
                decoded_result, index_top_pred = prediction_decoder(preds) # and decode to text form

                # inline keyboard compilation
                keyboard = reply_markup_compiler(*decoded_result)

                # output prediction collage parameters
                car_classes_path = './output_car_classes'
                height = 300
                width = 400
                frame_width = 10

                # take preds index for top-4 for collage generation
                index1 = str(index_top_pred[3])+'.jpg'
                index2 = str(index_top_pred[2])+'.jpg'
                index3 = str(index_top_pred[1])+'.jpg'
                index4 = str(index_top_pred[0])+'.jpg'

                # make collage image
                pred_img = photos_in_frame(height, width, frame_width,
                                           car_classes_path,
                                           index1, index2, index3, index4)

                pred_collage_path = './output/output_%s_%s.jpg' %(user_id, message_id)
                pred_img.save(pred_collage_path)

                # little pause before send prediction message in seconds
                await asyncio.sleep(3)

                # resulting massage of prediction
                await bot.send_photo(chat_id,
                                     photo=open(pred_collage_path, 'rb'),
                                     caption=HINT_TEXT,
                                     reply_markup=keyboard)

                # Inline buttons callback query handlers
                @dp.callback_query_handler(lambda callback_query: True)
                async def callback_handler(call: types.CallbackQuery):
                    # set time  in seconds that callback query results may be cached by client-side
                    await call.answer(cache_time=60)

                    # define callback data
                    callback_data = call.data
                    logging.info(f'call = {callback_data}')
                    # make car description for inline buttons response
                    # by car dictionary decoder and resulting text generator
                    description = car_description(callback_data)
                    await call.message.answer(description, disable_web_page_preview=True)

    else:
        # if more than one photo in  message
        await message.reply("Пожалуйста, пришли одну фотографию, а не вот столько!")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
