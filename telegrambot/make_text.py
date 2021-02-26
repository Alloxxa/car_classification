import pandas as pd
import os

path = 'cars_info.xlsx'
table = pd.read_excel(path).drop(columns=['Unnamed: 0'])

roman_numerals = {'I' : '1',
                'II' : '2',
                'III' : '3',
                'IV' : '4',
                'V' : '5',
                'VI' : '6',
                'VII' : '7',
                'VIII' : '8',
                'IX' : '9',
                'X' : '10',
                'рестайлинг' : '%D1%80%D0%B5%D1%81%D1%82%D0%B0%D0%B9%D0%BB%D0%B8%D0%BD%D0%B3%0A'}

def text_for_cars(name):
    model = table[table['full_name'] == name]['model'].iloc[0]
    sub_table = table[table['model'] == model]
    s = sub_table.shape[0]
    str_list = []
    first_str = ''
    standard_URL = 'https://www.google.com/search?q='
    for i in range(s):
        output = sub_table['output'].iloc[i]
        output_upd = output + '.'
        final_age = sub_table['final_age'].iloc[i]
        min_price = sub_table['min_price'].iloc[i]
        space = '\n'
        if min_price >= 1000:
            space = ''
            min_price = str(min_price)[0] + ',' + str(min_price)[1:]
        space2 = ' '
        max_price = sub_table['max_price'].iloc[i]
        if max_price >= 1000:
            space2 = ''
            max_price = str(max_price)[0] + ',' + str(max_price)[1:]
        words_list = output_upd.split('.')[0].split(' ')
        words_list = [(word if word not in roman_numerals else roman_numerals[word]) for word in words_list]
        words_list[-1] = words_list[-1] + '.'
        words_list.append(final_age)
        google_ref = standard_URL + '+'.join(words_list)
        if sub_table['full_name'].iloc[i] == name:
            first_str =  f'{output_upd}\nГоды выпуска: {final_age}\nСтоимоcть:{space}{min_price},000 - {space2}{max_price} ,000 рублей \n{google_ref}'
        else:
            common_str = f'{output_upd}\nГоды выпуска: {final_age}\nСтоимоcть:{space}{min_price},000 - {space2}{max_price},000 рублей \n'
            str_list.append(common_str)
    text = '🚗 '+first_str+'\n'+'\n\n\nА также другие поколения:\n\n' +'\n'.join(str_list)
    return text
