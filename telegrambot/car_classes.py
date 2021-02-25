import re
from make_text import text_for_cars


def car_description(callback_data):

    start = callback_data.find('car:') + len('car:')
    end = len(callback_data)
    car = callback_data[start:end]
    description = text_for_cars(car)

    return description
