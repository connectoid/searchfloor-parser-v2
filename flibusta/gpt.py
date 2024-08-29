import requests
import os

from flibusta.settings import prompt_description   
from flibusta.posting import get_categories
from flibusta.tools import get_api_key, remove_api_key, move_first_key_to_end


def add_file(filename, path, api_key):
    print('Загружаем файл на ChatPDF')
    upload_result = {}
    files = [
        ('file', ('file', open(f'{path}/{filename}', 'rb'), 'application/octet-stream'))
    ]
    headers = {
        'x-api-key': api_key
    }
    try:
        response = requests.post(
            'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

        if response.status_code == 200:
            print('Получен Source ID:', response.json()['sourceId'])
            source_id = response.json()['sourceId']
            upload_result['success'] = True
            upload_result['source_id'] = source_id
            upload_result['status_code'] = response.status_code
            return upload_result
        else:
            print('Status:', response.status_code)
            print('ChatPDF: add_file Error:', response.text)
            upload_result['success'] = False
            upload_result['source_id'] = 0
            upload_result['status_code'] = response.status_code
            return upload_result

    except Exception as e:
        print(f'Ошибка запроса к ЧатПФД: {e}')
        print(f'Возможно закончилась подписка, пробуем следующий ключ')
        upload_result['success'] = False
        upload_result['source_id'] = 0
        upload_result['status_code'] = 0
        return upload_result



def delete_file(source_id, api_key):
    print('Удаляем файл из ChatPDF')

    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
    }

    data = {
        'sources': [source_id],
    }

    try:
        response = requests.post(
            'https://api.chatpdf.com/v1/sources/delete', json=data, headers=headers)
        response.raise_for_status()
        print(f'Файл успешно удален из ChatPDF')
    except requests.exceptions.RequestException as error:
        print(f'Ошибка удаления файла из ChatPDF')
        print('Error:', error)
        print('Response:', error.response.text)


def get_description(filename, path):
    api_key = get_api_key()
    genres_list, genres_dict = get_categories()
    prompt_genre =  f"""
        Выбери один или несколько жанров из этого списка {genres_list} к которым можно отнести эту книгу. В ответе укажи только один или несколько жанров через запятную, в точности так же как в этом списке {genres_list}
    """
    print('Получаем описание книги с ChatPDF')
    upload_result = add_file(filename, path, api_key)
    if upload_result['success']:
        source_id = upload_result['source_id']
        headers = {
            'x-api-key': f'{api_key}',
            "Content-Type": "application/json",
        }
        data_description = {
            'sourceId': source_id,
            'messages': [
                {
                    'role': "user",
                    'content': prompt_description,
                }
            ]
        }

        data_genre = {
            'sourceId': source_id,
            'messages': [
                {
                    'role': "user",
                    'content': prompt_genre,
                }
            ]
        }

        response_description = requests.post(
            'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data_description)
        if response_description.status_code == 200:
            print('Описание получено')
            description = response_description.json()['content']
            print(description[:50] + '...')
        else:
            print('Status:', response_description.status_code)
            print('ChatPDF: response_description Error:', response_description.text)
            description = False

        
        response_genre = requests.post(
            'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data_genre)
        if response_genre.status_code == 200:
            print('Жанры получены')
            genres = response_genre.json()['content']
            print(f'Список категорий на сайте приемнике: {genres_list}')
            print(f'Жанры от чатПДФ: {genres}')
            try:
                genres_names = genres.split(',')
                genres_ids = [genres_dict[genre.strip()] for genre in genres_names]
            except:
                print('ChatPDF: Error converting genres to list')
                genres_names = ['Романы']
                genres_ids = [29]
        else:
            print('Status:', response_genre.status_code)
            print('ChatPDF: response_genre Error:', response_genre.text)
            genres_ids = False
            genres_names = False
        delete_file(source_id, api_key)
        return description, genres_names, genres_ids
    elif upload_result['status_code']:
        if upload_result['status_code'] == 400:
            print('ChatPDF: Ошибка загрузки файла, закончилась подписка на ChatPDF, берем следующий ключ')
            move_first_key_to_end()
            return False, False, False
        else:
            status_code = upload_result['status_code']
            print(f'ChatPDF: Ошибка загрузки файла, status code: {status_code}')
            return False, False, False
    else:
        print(f'ChatPDF: Произошло исключение при попытке загрузить файл')
        return False, False, False

