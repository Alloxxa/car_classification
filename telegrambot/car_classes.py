import re
import logging

from make_text import text_for_cars

# setup logging
logging.basicConfig(level=logging.INFO)


def car_description(callback_data):
    # logging.info(f'callback_data = {callback_data}')
    start = callback_data.find("car:") + len("car:")
    car = callback_data[start:]
    # logging.info(f'car in description = {car}')
    description = text_for_cars(car)
    return description
