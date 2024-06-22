import urllib.parse
import os
import shutil


import xml.dom.minidom
import base64

import pymupdf
import zipfile

from settings.settings import db_file, logging, api_keys_file, login_params


def extract_cover_from_fb2(filename, path):
    file = f'{path}/{filename}'
    doc = xml.dom.minidom.parse(file)
    pictures_links = doc.getElementsByTagName('binary')
    minimal = 0
    for pictures_link in pictures_links:
        nodes = pictures_link.childNodes
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                base64_pictures_bytes = node.data.encode('utf-8')
                full_pictures_name = file.replace('.fb2', '.png')
                pictures_name = filename.replace('.fb2', '.png')
                with open(full_pictures_name, 'wb') as file_to_save:
                    decoded_image_data = base64.decodebytes(base64_pictures_bytes)
                    file_to_save.write(decoded_image_data)
                    minimal = int(minimal)
                    minimal = minimal + 1
                    return pictures_name


def extract_genres_from_fb2(filename, path):
    genres = []
    file = f'{path}/{filename}'
    doc = xml.dom.minidom.parse(file)
    genre_links = doc.getElementsByTagName('genre')
    for genre_link in genre_links:
        node = genre_link.childNodes[0]
        if node.nodeType == node.TEXT_NODE:
                genre_text = node.data
                genres.append(genre_text)
    return genres


def delect_section_from_fb2(filename, path):
    genres = []
    file = f'{path}/{filename}'
    doc = xml.dom.minidom.parse(file)
    genre_links = doc.getElementsByTagName('genre')
    for genre_link in genre_links:
        node = genre_link.childNodes[0]
        if node.nodeType == node.TEXT_NODE:
                genre_text = node.data
                genres.append(genre_text)
    return genres


def extract_zip(archive, path):
    archive = f'{path}/{archive}'
    with zipfile.ZipFile(archive, 'r') as zip_file:
        filename = zip_file.namelist()[0]
        
        zip_file.extractall(path)
        os.remove(archive)
    return filename


def convert_fb2_to_pdf(filename, path):
    # filename = extract_zip(filename, path)
    # filename = filename.lower()
    pdf_filename = filename.replace('.fb2', '.pdf')
    pdf_full_filename = f'{path}/{pdf_filename}'
    filename = f'{path}/{filename}'
    doc = pymupdf.open(filename) 
    pdfbytes = doc.convert_to_pdf()
    pdf = pymupdf.open("pdf", pdfbytes)
    pdf.save(pdf_full_filename)
    return pdf_filename


def download_file(url, path, session):
    print(f'Загружаем файл книги по ссылке {url}')
    logging.info(f'Загружаем файл книги по ссылке {url}')
    response = session.get(url)
    if response.status_code == 200:
        headers = response.headers
        content_disposition = headers['content-disposition']
        filename = content_disposition.split("filename*=UTF-8''")[-1]
        filename = urllib.parse.unquote(filename)
        with open(f'{path}/{filename}', 'wb') as file:
            file.write(response.content)
            new_filename = extract_zip(filename, path)
            return new_filename
    else:
        print(f'Requests error in download_file: {response.status_code}')
        logging.error(f'Requests error in download_file: {response.status_code}')
        return False

def login_by_tg():
    import requests

    headers = {
        'Referer': 'https://searchfloor.org/popular?category=books&period=today',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    session = requests.Session()
    response = session.get('https://searchfloor.org/login', params=login_params, headers=headers)
    return session, response.status_code


def add_title_to_db(title):
    if not os.path.exists(db_file):
        with open(db_file, 'w') as file:
            pass
    with open(db_file, 'a') as file:
        file.write(title + '\n')
    print('Title книги успешно добавлен в файл БД.')
    logging.info('Title книги успешно добавлен в файл БД.')


def check_is_title_exists(title):
    if not os.path.exists(db_file):
        with open(db_file, 'w') as file:
            pass
    with open(db_file, 'r') as file:
        titles_set = set(word.strip() for word in file)
        return title in titles_set
    

def get_file_size(filename, path):
    full_filename = f'{path}/{filename}'
    filesize = os.path.getsize(full_filename)
    return filesize


def get_api_key():
    """Возвращает первую строку из файла или False, если файл пустой."""
    try:
        with open(api_keys_file, 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("Файл не найден.")
        return False
    except IOError:
        print("Ошибка при чтении файла.")
        return False

def remove_api_key():
    """Удаляет первую строку из файла и возвращает True, если строка была удалена, иначе False."""
    try:
        with open(api_keys_file, 'r+') as file:
            # Читаем весь файл в память
            content = file.read()
            # Если файл пустой, возвращаем False
            if not content:
                return False
            # Удаляем первую строку и записываем обратно в файл
            file.seek(0)  # Перемещаемся в начало файла
            file.truncate()  # Удаляем содержимое файла
            file.write(content[content.find('\n'):])  # Сохраняем оставшуюся часть файла
            return True
    except FileNotFoundError:
        print("Файл не найден.")
        return False
    except IOError:
        print("Ошибка при чтении/записи файла.")
        return False


def move_first_key_to_end():
    with open(api_keys_file, 'r') as file:
        lines = file.readlines()
    if not lines:
        return False
    first_line = lines.pop(0)
    with open(api_keys_file, 'w') as file:
        file.writelines(lines)
    with open(api_keys_file, 'a') as file:
        file.write(first_line)
    return True


def delete_all_files_in_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"Директория {directory_path} не существует.")
        return
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    


