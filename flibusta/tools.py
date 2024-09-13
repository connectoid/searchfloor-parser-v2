import os
import urllib.parse
import requests
import re

import pymupdf
import zipfile
from slugify import slugify
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


from flibusta.settings import *


def init_env():
    if not os.path.exists(books_dir):
        os.mkdir(books_dir)
    if not os.path.exists(covers_dir):
        os.mkdir(covers_dir)
    

def extract_zip(archive, path):
    archive = f'{path}/{archive}'
    with zipfile.ZipFile(archive, 'r') as zip_file:
        filename = zip_file.namelist()[0]
        
        zip_file.extractall(path)
        os.remove(archive)
    return filename


def convert_fb2_to_pdf(filename, path):
    pdf_filename = filename.replace('.fb2', '.pdf')
    pdf_full_filename = f'{path}/{pdf_filename}'
    filename = f'{path}/{filename}'
    doc = pymupdf.open(filename) 
    pdfbytes = doc.convert_to_pdf()
    pdf = pymupdf.open("pdf", pdfbytes)
    pdf.save(pdf_full_filename)
    return pdf_filename



def download_file(url, path, slug_title):
    print(f'Загружаем файл книги по ссылке {url}')
    response = requests.get(url)
    filename = slug_title + '.zip'
    if response.status_code == 200:
        with open(f'{path}/{filename}', 'wb') as file:
            file.write(response.content)
            new_filename = extract_zip(filename, path)
            return new_filename
    else:
        print(f'Requests error in download_file: {response.status_code}')
        return False


def download_epub_file(url, path, slug_title):
    print(f'Загружаем файл книги по ссылке {url}')
    response = requests.get(url)
    filename = slug_title + '.epub'
    if response.status_code == 200:
        with open(f'{path}/{filename}', 'wb') as file:
            file.write(response.content)
            # new_filename = extract_zip(filename, path)
            return filename
    else:
        print(f'Requests error in download_file: {response.status_code}')
        return False


def download_cover(url, path, slug_title):
    print(f'Загружаем файл облложки по ссылке {url}')
    response = requests.get(url)
    filename = slug_title + '.jpg'
    if response.status_code == 200:
        with open(f'{path}/{filename}', 'wb') as file:
            file.write(response.content)
            return filename
    else:
        print(f'Requests error in download_file: {response.status_code}')
        return False


def add_title_to_db(title):
    if not os.path.exists(db_file):
        with open(db_file, 'w') as file:
            pass
    with open(db_file, 'a') as file:
        file.write(title + '\n')
    print('Title книги успешно добавлен в файл БД.')


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
    

def extract_title_slug_from_fb2(filename, path):
    fb2_file = f'{path}/{filename}'
    with open(fb2_file, "r") as file:
        soup = BeautifulSoup(file, "xml")
    title = soup.find('book-title').text
    if title == 'Unknown':
        return False
    first_name = soup.find('first-name').text
    last_name = soup.find('last-name').text
    full_title = f'{title} {first_name} {last_name}'
    slug_title = slugify(full_title, replacements=[
                                            ['я', 'ya'],
                                            ['щ', 'sch'],
                                            ['ё', 'yo'],
                                            ['й', 'y'],
                                            ['х', 'h'],
                                            ['ю', 'yu'],
                                            ['Я', 'ya'],
                                            ['Щ', 'sch'],
                                            ['Ë', 'yo'],
                                            ['Й', 'y'],
                                            ['Х', 'h'],
                                            ['Ю', 'yu'],
                                        ])
    return slug_title


def slugify_title(title):
    slug_title = slugify(title, replacements=[
                                            ['я', 'ya'],
                                            ['щ', 'sch'],
                                            ['ё', 'yo'],
                                            ['й', 'y'],
                                            ['х', 'h'],
                                            ['ю', 'yu'],
                                            ['Я', 'ya'],
                                            ['Щ', 'sch'],
                                            ['Ë', 'yo'],
                                            ['Й', 'y'],
                                            ['Х', 'h'],
                                            ['Ю', 'yu'],
                                        ])
    return slug_title


def remove_string_with_brackets(string):
    print(string)
    pattern_1 = r'\s*\(.*?\)\s*'
    pattern_2 = r'\s*\[.*?\]\s*'
    output_string = re.sub(pattern_1, '', string)
    output_string = re.sub(pattern_2, '', output_string)
    print(output_string)
    return output_string


def remove_non_letters_and_digits(input_string):
    pattern = re.compile(r'[^а-яА-Яa-zA-Z0-9 ]')
    output_string = pattern.sub('', input_string)
    output_string = output_string.replace("  ", " ")
    output_string = output_string.lower()
    return output_string


def check_is_title_exists_by_fuzz(main_title):

    if not os.path.exists(db_file):
        with open(db_file, 'w') as file:
            pass
    with open(db_file, 'r') as file:
        titles_list = [word.strip() for word in file]
        for title in titles_list:
            equal_ratio = fuzz.ratio(main_title, title)
            if equal_ratio > 90:
                print(f'{main_title} and {title} is equal by {equal_ratio}%')
                return True
        return False


