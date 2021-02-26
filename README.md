# Whata Car?!

https://t.me/whatacar_bot

## Аннотация
Проект состоит из нескольких параллельно реализованных нами модулей и исследований, которые формируют сервис для определения марки, поколения и рестайлинга автомобиля по его фотографии.

## Сбор данных
Для обучения нашей модели был собран датасет изображений автомобилей. Мы взяли 25 самых продаваемых в России
моделей машин в 2020 году, а также все их существующие поколения и рестайлинги. Всего, таким образом,
было выбрано 89 категорий автомобилей. Датасет собирался с сайта Auto.ru. Для парсинга данных с сайта мы использовали программу, написанную на основе библиотеки 'Scrapy'.  Таким образом, для каждго из наших классов было собрано 500-600 фотографий.
Затем мы удалили из датасета снимки, на которых был изображен салон, отдельные детали (колесо, фара, и.т.д) или только часть
автомобиля. Также мы исключили фотографии машин с открытым багажником или открытыми дверями. Таким образом, в каждой
категории у нас осталось в среднем ~200 фотографий автомобилей. В итоге мы получили датасет, содержащий ~19000 изображений.

## Препроцессинг

1. На первом этапе мы обработали каждый снимок в датасете с помощью нейросети Detectron2. Она выделяла на снимке самый крупный объект-автомобиль. Затем картинка обрезалась по размеру ограничивающей рамки, которую обозначала нейросеть.
![Самый крупный объект-автомобиль](/telegrambot/static_images/bounding_photo.jpg "Автомобиль")

2. Далее надо было привести снимки к одинаковому квадратному виду размера 331x331, без искажения (растягивания/сжатия) фотографии. Именно разрешение 331x331 оптимально для нейросети NASNetLarge, из которой мы осуществляли transfer learning для обучения своей нейросети.
3. На завершающем этапе препроцессинга мы сделали небольшую аугументацию изображений, для того чтобы наша нейросеть не начинала быстро переобучаться. Это должно было позволить нам достичь большего прогресса классификации на валидационной выборке.

![Аугументация](/telegrambot/static_images/augmentation.png "Аугументация")

## Обучение
Для нашей цели классификации моделей/поколений/рестайлингов автомобилей мы использовали transfer learning из нейросети NASNetLarge,  показавшей на датасете ImageNet самый лучший результат из всех моделей, доступных в библиотеке Keras.
Мы заменили голову (последние слои) NASNetLarge на новую, с помощью которой делали предсказания наших 89 классов.
Первоначально обучали нейросеть, заморозив основную часть, кроме последнего слоя. Затем разморозили часть тела нейросети и дообучили.
Основная метрика результатов обучения для нас была accuracy-Top-4, так как для telegram-bot мы решили выводить 4 первых предсказания модели автомобиля.
По итогам нашего обучения на валидационной выборке мы достигли точности 86% для ТОП-4.  

## Имплементация в telegram бота
Для реализации проекта в сервис telegram была использована библиотека aiogram — ассинхронный фреймворк для Telegram Bot API основанный на asyncio и aiohttp.

#### Структура бота:

##### bot.py
Основной модуль, где реализованы обработчики сообщений: стартовое сообщение, проверка на необходимый тип медиа вложения — фотография, сохранение входной фотографии, отправка на препроцессинг, после подготовленная фотография приходит на вход в модель и производится вывод результатов предсказания модели. Далее формируется коллаж 2x2 "эталонных" пронумерованных фотографий соответствующих классов автомобилей — пользователь может сравнить визуально автомобиль перед ним и фотографию предсказанного класса. После этого формируется встроенная клавиатура с соответствующими предсказаниями, по нажатию на кнопку генерируется более подробное описание: дополнительно выводятся дипазон цен покупки, поисковая ссылка и остальные поколения и рестайлинги для данной предсказанной модели
![Объект-автомобиль](/telegrambot/static_images/screen1.png "Автомобиль")
##### detection.py
Фотография попадает в detectron2 — происходит отбраковка фотографий без авто и выделение bounding box на фото. После первичной проверки на наличие автомобиля, на фотографии box самого большого найденного автомобиля должен быть по площади не менее 70% от самого большого найденного box'а (в том числе не автомобиля). По выделению происходит обрезка снимка и сохранение полученной фотографии для последующей отправки в модель классификации автомобиля.
![Объект-автомобиль](/telegrambot/static_images/screen2.png "Автомобиль")
##### image_proccessing.py
Преобразование входной фотографии к требованиям входа NASNetLarge модели (которая лежит в основе нашей обученной модели). В данном модуле также реализованы функции генерации коллажа эталонных фотографий.

##### model_functions.py
Здесь происходит настройка среды и загрузка предобученной нами модели. Обрезанная фотография после препроцессинга попадает в модель. Далее происходит декодирование результатов предсказания. Формирование "клавиатуры" для пользователя.
![Клавиатура](/telegrambot/static_images/screen3.png "Клавиатура")
##### make_text.py
В модуле рализуются функция генерации текста для подробного описания. Используются табличные данные о каждом классе автомобиля.

##### car_classes.py
Модуль использует данные о нажатии инлайн кнопок, получает ответ и формирует текст описания, который далее будет передаваться в сообщение к пользователю.
![Текст](/telegrambot/static_images/screen4.png "Текст")

### Заключение

По результатам проекта мы получили модель с точностью предсказания ТОП-4 равной 86% (количество определяемых классов 89).

Альтернативный вариант — предсказание марки и модели (без рейстайлинга) дал результат 97% (количество определяемых классов 25).

Возможно несколько путей улучшения точности модели:
1. расширение объёма и разнобразия датасета и увеличение времени обучения
2. нахождение оптимальной тонкой настройки параметров обучения (fine tuning)
3. использовать более эффективные архитектуры нейросетей

Возможно расширение количества используемых в обучении марок и моделей, чтобы любой встреченный автомобиль мог быть корректно распознан.

### Авторы
https://github.com/Alloxxa

https://github.com/Chelibosik

https://github.com/ulyumdzhi
