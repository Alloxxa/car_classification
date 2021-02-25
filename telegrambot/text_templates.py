# Static text of ignoring not target user message types
NOT_TARGET_CONTENT_TYPES = [
'text','audio', 'document', 'sticker',
'video', 'video_note', 'voice','location','contact', 'new_chat_members',
'left_chat_member','new_chat_title', 'new_chat_photo', 'delete_chat_photo',
'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'
]

# Define static texts with %s replace operator
HELLO_TEXT = """
Привет, %s!
Я могу помочь распознать автомобиль, который тебе приглянулся.
Скидывай фотку машины, и мы начнём.
"""

NOT_TARGET_TEXT = """
Неверный тип данных!
\nСмотри, %s, всё просто!
Ты отправляешь фотографию, желательно с крупным изображением автомобиля.
И я расскажу тебе, какая конкретно тачка там изображена.
Фотку нужно прислать как изображение, а не как файл.
"""

ERROR_NOT_CAR = """
Где моя тачка, чувак?!
\nЯ внимательно рассмотрел твою фотку.
\nИ увы, на ней нет автомобиля.
"""

ERROR_LITTLE_CAR = """
Где моя тачка, чувак?!
\nЯ внимательно рассмотрел твою фотку. Здесь автомобиль уж очень мелкий или на заднем плане.
\nПопробуй прислать фото покрупнее, пожалуйста.
"""

WAITING_TEXT = """
Спасибо, %s! Подожди секунду...
"""

HINT_TEXT = """
Номер на фото соответствует номеру кнопки предсказания.
\nНажми на кнопку для подробной информации.
"""
