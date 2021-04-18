import requests
import telebot
from telebot.types import InputMediaPhoto, InputMediaDocument
from pprint import pprint
# import logging
import time
# import datetime
import tokens
import traceback

TOKEN_VK = tokens.TOKEN_VK
TOKEN_TG = tokens.TOKEN_TG

bot = telebot.TeleBot(TOKEN_TG)

def attachments(data_attachments, chat_id, message):
    attachment = {'photo' : [], 'posted_photo' : [], 'video' : [], 'doc' : [], 'graffiti' : [], 'note' : [], 'app' : [], 'poll' : [], 'album' : [], 'market' : [], 'market_album' : [], 'sticker' : [], 'pretty_cards' : []}
    for element in data_attachments:
        print(element['type'])
        if element['type'] == 'photo':
            # try:
            #     attachment['photo'].append(InputMediaPhoto(element['photo']['sizes'][-1]['url']))
            # except(telebot.apihelper.ApiTelegramException):
            photo = requests.get(element['photo']['sizes'][-1]['url']).content
            attachment['photo'].append(InputMediaPhoto(photo))
        elif element['type'] == 'posted_photo':
            posted_photo = highest_photo(element['posted_photo'])
            attachment['posted_photo'].append(InputMediaPhoto(element['posted_photo'][posted_photo]))
        elif element['type'] == 'video':
            attachment['video'].append(element['video']['image'][-1]['url'])
            attachment['video'].append('Видео: ' + element['video']['title'])
        elif element['type'] == 'audio':
            message += '\n\nАудио: ' + element['audio']['artist'] + ' - ' + element['audio']['title']
        elif element['type'] == 'doc':
            # attachment['doc'].append(InputMediaDocument(element['doc']['url']))
            message += '\n\nДокумент ' + element['doc']['title'] + ' ' + element['doc']['url']
        elif element['type'] == 'graffiti':
            graffiti = highest_photo(element['graffiti'])
            attachment['graffiti'].append(InputMediaPhoto(element['graffiti'][graffiti]))
        elif element['type'] == 'link':
            if element['link']['url'] not in message:
                message += ('\n\n' + element['link']['title'] + ': ' + element['link']['url'])
        elif element['type'] == 'note':
            title = element['note']['title']
            text = element['note']['text']
            url = element['note']['view_url']
            note = title + '\n\n' + text + '\n\n' + url
            attachment['note'].append(note)
        elif element['type'] == 'app':
            attachment['app'].append(highest_photo(element['app']))
            attachment['app'].append('Приложение: ' + element['app']['name'])
        elif element['type'] == 'poll':
            attachment['poll'].append(element['poll']['question'])
            answers = []
            for answer in element['poll']['answers']:
                answers.append(answer['text'])
            attachment['poll'].append(answers)
            attachment['poll'].append(element['poll']['multiple'])
            print(attachment['poll'])
        elif element['type'] == 'page':
            message += ('\n\n' + element['page']['title'] + ': ' + element['page']['view_url'])
        elif element['type'] == 'album':
            attachment['album'].append(element['album']['thumb']['sizes'][-1]['url'])
            attachment['album'].append(element['album']['title'])
        elif element['type'] == 'market':
            attachment['market'].append(element['market']['thumb_photo'])
            attachment['market'].append(element['market']['title'] + ' - ' + element['market']['price']['text'])
        elif element['type'] == 'market_album':
            attachment['market_album'].append(element['market_album']['photo']['sizes'][-1]['url'])
            attachment['market_album'].append('Подборка товаров ' + element['market_album']['title'])
        elif element['type'] == 'sticker':
            attachment['sticker'].append(element['sticker']['animation_url'])
        elif element['type'] == 'pretty_cards':
            attachment['pretty_cards'].append(element['pretty_cards']['images'][0]['url'])
            attachment['pretty_cards'].append(element['pretty_cards']['title'] + ': ' + element['pretty_cards']['link_url'])
        elif element['type'] == 'event':
            message += '\n\n' + 'Встреча'
            if 'text' in element['event']:
                message += '\n' + element['event']['text']
            if 'address' in element['event']:
                message += '\nГде: ' + element['event']['address']
            if 'time' in element['event']:
                message += '\nКогда: ' + time.ctime(element['event']['time'])
    if message:
        bot.send_message(chat_id, message)
    for element in attachment:
        if attachment[element]:
            if element == 'photo' or element == 'posted_photo' or element == 'graffiti' or element == 'sticker':
                # try:
                attachment[element] = attachment[element][:8]
                bot.send_media_group(chat_id, attachment[element])
                # except(telebot.apihelper.ApiTelegramException):
                #     bot.send_message(chat_id, '[Не удалось загрузить изображение]')
            elif element == 'video' or element == 'app' or element == 'album' or element == 'market' or element == 'market_album' or element == 'pretty_cards':
                # try:
                bot.send_photo(chat_id, attachment[element][0], attachment[element][1])
                # except(telebot.apihelper.ApiTelegramException):
                #     message = '[Не удалось загрузить]\n' + attachment[element][1]
                #     bot.send_message(chat_id, message)
            # elif element == 'doc':
            #     bot.send_document(chat_id, attachment[element])
            elif element == 'note':
                bot.send_message(chat_id, attachment[element])
            elif element == 'poll':
                if len(attachment[element][1]) == 1:
                    attachment[element][1].append('-')
                bot.send_poll(chat_id, attachment[element][0], attachment[element][1], True, allows_multiple_answers=attachment[element][2])

def highest_photo(sizes):
    photos = []
    for size in sizes.keys():
        if "photo_" in size:
            photos.append(size[6:])
    photos.sort()
    photo = "photo_" + photos[-1]
    return photo
            
def remove_symbols(text):
    while '[' in text and '|' in text and ']' in text:
        symbols = []
        symbols.append(text.find('['))
        symbols.append(text.find('|') + 1)
        symbols.append(text.find(']'))
        symbols.append(text.find(']') + 1)
        text = text[: symbols[0]] + text[symbols[1] : symbols[2]] + text[symbols[3] :]
    return text

def unpack(data, message = '', is_resend = False):
    # Дата
    data_date = data['date']
    message += (time.ctime(data_date) + '\n')
    # Отправитель
    data_from = data['from_id']
    if data_from != data['owner_id'] or is_resend:
        if data_from < 0:
            data_from = requests.get('https://api.vk.com/method/groups.getById/', params={'access_token' : TOKEN_VK, 'v' : '5.130', 'group_id' : -data_from}).json()['response'][0]['name']
        else:
            data_from = requests.get('https://api.vk.com/method/users.get/', params={'access_token' : TOKEN_VK, 'v' : '5.130', 'user_ids' : data_from}).json()['response'][0]
            data_from = data_from['first_name'] + ' ' + data_from['last_name']
        # pprint(data_from)
        message += 'От ' + data_from + ':\n\n'
    # Текст
    data_text = data['text']
    if data_text:
        data_text = remove_symbols(data_text)
        message += str(data_text)
    # Вложения
    if 'attachments' in data:
        data_attachments = data['attachments']
        attachments(data_attachments, "@nadorad", message)
    else:
        if message:
            bot.send_message("@nadorad", message)
        print("There is no attachments")
    # Пересланное сообщение
    if 'copy_history' in data:
        data_from = data['copy_history'][0]['from_id']
        message = 'Пересланное сообщение\n'
        unpack(data['copy_history'][0], message, True)

count = 0
data = requests.get('https://api.vk.com/method/wall.get/', params={'access_token' : TOKEN_VK, 'v' : '5.130', 'domain' : 'pushnoy_nadorad', 'count' : 1, 'offset' : 0}).json()['response']
offset = data['count'] - 1 - 5603
pause = 120
# while True:
while count < 1:
    print(count)
    data = requests.get('https://api.vk.com/method/wall.get/', params={'access_token' : TOKEN_VK, 'v' : '5.130', 'domain' : 'pushnoy_nadorad', 'count' : 1, 'offset' : offset}).json()['response']
    data_count = data['count']
    # pprint(data)
    # if data_count - count > 0:
    unpack(data['items'][0])

    count += 1
    offset = data_count - 1 - count - 5603

    # time.sleep(30)

    if count % 10 == 0:
        pprint(data_count)
        print("offset", offset)
        print("pause", pause)
        time.sleep(pause)

# bot.polling()
