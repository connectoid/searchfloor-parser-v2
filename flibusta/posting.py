import requests
import os
import base64
from pprint import pprint
from time import sleep

from dotenv import load_dotenv

from flibusta.tools import download_file, extract_zip
from flibusta.settings import (endpoints, title_postfix, current_date, 
                               series_category_id, exclude_category_names)

load_dotenv()
app_password = os.getenv('app_password')
user = "autoposter"
credentials = user + ':' + app_password
token = base64.b64encode(credentials.encode())
header = {'Authorization': 'Basic ' + token.decode('utf-8')}


def create_post(book):
    url = endpoints['posts']
    post = {
        'title': book['title'], # + title_postfix,
        'status': 'publish',
        'content': book['content'],
        # 'excerpt': 'Это поле EXCERPT',
        'categories': book['categories'],
        'featured_media': book['featured_media'],
        'tags': book['tags'],
        'acf': {
            "namebook": book['title'],
            "карточка_вклвыкл": "Вкл",
            "avtor": book['avtor'],
            "yazyk": book['yazyk'],
            "seriya": book['acf_series'],
            "zhanr": ', '.join(book['genres']),
            "year": current_date,
            "download_title": f"Скачать книгу {book['title']} бесплатно",
            "enable-scan-download": True,
            "reedon": book['reedon_link'],
        }
    }
    post['acf'][f"choose_fb2"] = {
            "choose_type_of_load": "file",
            "choose_file": book['choose_file_fb2'],
            "choose_link": ""
        }
    post['acf'][f"choose_epub"] = {
            "choose_type_of_load": "file",
            "choose_file": book['choose_file_epub'],
            "choose_link": ""
        }
    response = requests.post(url , headers=header, json=post)
    book_slug = response.json()['slug']
    id = response.json()['id']
    return id, book_slug


def update_post_by_reedon_link(post_id, link):
    endpoint = endpoints['posts']
    url = f'{endpoint}/{post_id}'
    post = {
        'acf': {
            "reedon": link,
        }
    }
    response = requests.post(url , headers=header, json=post)
    if response.status_code == 200:
        return True
    else:
        return False



def upload_media(filename, path):
    url = endpoints['media']
    file_data = open(f'{path}/{filename}', 'rb').read()
    headers = {
        # 'Content-Type': 'multipart/form-data',
        'Content-Type': 'image/jpeg',
        'Content-Disposition': f'attachment;filename={filename}',
        'Authorization': 'Basic ' + token.decode('utf-8')
    }
    response = requests.post(url, data=file_data, headers=headers)
    return response.json()['id']


def upload_book(filename, path):
    url = endpoints['media']
    file_data = open(f'{path}/{filename}', 'rb').read()
    headers = {
        'Content-Type': 'multipart/form-data',
        'Content-Disposition': f'attachment;filename={filename}',
        'Authorization': 'Basic ' + token.decode('utf-8')
    }
    response = requests.post(url, data=file_data, headers=headers)
    return response.json()['id']


def get_tag_by_id(id):
    endpoint = endpoints['tags']
    endpoint = f'{endpoint}/{id}'
    response = requests.get(endpoint , headers=header)
    link = response.json()['link']
    return link


def get_series_by_id(id):
    endpoint = endpoints['series']
    endpoint = f'{endpoint}/{id}'
    response = requests.get(endpoint , headers=header)
    link = response.json()['link']
    return link


def get_or_create_tag(authors):
    endpoint = endpoints['tags']
    authors_ids = []
    authors_urls = []
    author_slug = ''
    for author in authors:
        print(f'Processing Author: {author}')
        tag = {
            'name': author,
            'description': f'В нашей рубрике вы найдете бесплатные онлайн версии книг автора {author}. Сможете прочитать или же скачать их. Откройте для себя великолепный мир слов, где каждая строчка – это приглашение в увлекательное приключение.',
        }
        response = requests.post(endpoint , headers=header, json=tag)
        response_json = response.json()
        if 'code' in response_json:
            if response_json['code'] == 'term_exists':
                id = response_json['data']['term_id']
                url = get_tag_by_id(id)
                tag_endpoint = f'{endpoint}/{id}'
                tag_response = requests.post(tag_endpoint , headers=header,)
                if not author_slug:
                    author_slug = tag_response.json()['slug']
        else:
            id = response_json['id']
            url = response_json['link']
            if not author_slug:
                author_slug = response_json['slug']
        authors_ids.append(id)
        authors_urls.append(url)
    return authors_ids, authors_urls, author_slug

def get_or_create_series(series):
    endpoint = endpoints['series']
    print(f'Processing Series: {series}')
    series_json = {
        'name': series,
        'description': f"""
            Здесь вы сможете скачать или читать онлайн абсолютно бесплатно полную серию ваших любимых книг {series}. Наша цель – предоставить вам доступ к качественной литературе в удобном формате и без лишних затрат. В нашей коллекции вы найдете произведения самых разных жанров: от захватывающих фэнтези и научной фантастики до трогательных любовных романов и детективов.
            Преимущества нашего портала:
            Бесплатный доступ – Все книги доступны для скачивания и чтения онлайн абсолютно бесплатно.
            Удобный интерфейс – Наш сайт прост в использовании, что позволяет легко найти нужную книгу и начать чтение.
            Разнообразие форматов – Вы можете выбрать удобный для вас формат: FB2 и ТХТ.
            Регулярное обновление – Мы постоянно добавляем новые серии и книги, чтобы вы могли наслаждаться новыми историями.
        """,
        'parent': series_category_id,
    }
    response = requests.post(endpoint , headers=header, json=series_json)
    response_json = response.json()
    if 'code' in response_json:
        if response_json['code'] == 'term_exists':
            series_id = response_json['data']['term_id']
            series_url = get_series_by_id(series_id)
    else:
        series_id = response_json['id']
        series_url = response_json['link']
    return series_id, series_url



def find_author(author_name):
    url = endpoints['tags']
    response = requests.get(url, headers=header)
    for item in response.json():
        if item['name'] == author_name:
            return item['link']
    return False


def get_category_link_by_id(id):
    url = endpoints['categories']
    url = f'{url}/{id}'
    response = requests.get(url, headers=header)
    category_link = response.json()['link']
    return category_link


def get_categories():
    print('Запрашиваем список категорий (жанров)')
    categories_list = []
    categories_dict = {}
    url = endpoints['categories']
    url = f'{url}?per_page=100&parent=0'
    response = requests.get(url, headers=header)
    for category in response.json():
        if category['name'] not in exclude_category_names:
            category_name = category['name']
            category_id = category['id']
            categories_list.append(f'{category_name}')
            categories_dict[category_name] = category_id
    return categories_list, categories_dict

