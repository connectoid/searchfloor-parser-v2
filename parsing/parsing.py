import requests
from bs4 import BeautifulSoup

from settings.settings import base_url, logging

def get_books(url, session):
    books = []
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        main_div = soup.find('div', class_='tab-content')
        # book_divs = main_div.find_all('div', class_='container')
        book_divs = main_div.find_all('div', {'style': 'margin-top: 1rem;'})
        count = 0
        skiped = 0
        for book in book_divs:
            book_json = {}
            items = book.find_all('p')
            title = items[0].find('b').text
            if items[0].find('a'):
                count += 1
                skiped += 1
                print(f'{count}. Найдена донатная книга {title}')
                logging.info(f'{count}. Найдена донатная книга {title}')
            book_json['title'] = title
            book_json['namebook'] = title
            authors = items[1].find_all('a')
            authors = [author.text for author in authors]
            book_json['authors'] = authors
            try:
                book_json['series'] = items[2].find('a').text
            except:
                book_json['series'] = ''
            try:
                book_json['url'] = base_url + book.find('button')['data-url']
            except:
                print(f'Пропускаем донатную книгу {title}, так как нет подписки')
                logging.warning(f'Пропускаем донатную книгу {title}, так как нет подписки')
                continue
            count += 1
            # print(f'{count}. Добавляем книгу {title}')
            # logging.info(f'{count}. Добавляем книгу {title}')
            books.append(book_json)
        print(f'Донатных книг {skiped} из {count}')
        logging.info(f'Донатных книг {skiped} из {count}')
        return books
    else:
        print(f'Request error: {response.status_code}')
        logging.error(f'Request error: {response.status_code}')
        return False
    

def is_autorised(url, session):
    response = session.get(url=url)
    soup = BeautifulSoup(response.text, 'lxml')
    loginbar = soup.find('div', class_='loginbar')
    try:
        button = loginbar.find('a').text
        return True
    except:
        return False


def extract_txt_from_fb2(filename, path):
    fb2_file = f'{path}/{filename}'
    txt_file = filename.replace('.fb2', '.txt')
    txt_file_full_path = f'{path}/{txt_file}'
    with open(fb2_file, "r") as file:
        soup = BeautifulSoup(file, "xml")

    text = soup.find('body').text

    with open(txt_file_full_path, "w") as file:
        file.write(text)
    return txt_file
