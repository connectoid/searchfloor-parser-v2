from pprint import pprint
import shutil
from pprint import pprint

import requests
import os
from bs4 import BeautifulSoup

from flibusta.tools import (download_file, extract_zip, convert_fb2_to_pdf, init_env, slugify_title, 
                   download_cover, get_file_size, add_title_to_db, delete_all_files_in_directory, 
                   extract_title_slug_from_fb2, download_epub_file, check_is_title_exists, 
                   remove_string_with_brackets, check_is_title_exists_by_fuzz)
from flibusta.settings import (books_dir, covers_dir, MAX_PDF_SIZE, default_picture_filename, search_url, base_url,
                      MIN_FB2_SIZE)
from flibusta.gpt import get_description
from flibusta.posting import (get_category_link_by_id, get_or_create_tag, get_or_create_series, upload_media, 
                     upload_book, update_post_by_reedon_link, create_post)


book_url = 'https://flibusta.is/b/707866'

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


def get_books(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        ul = soup.find_all('ul')[1]
        li_books = ul.find_all('li')
        books = []
        count = 0
        for li_book in li_books:
            book = {}
            items = li_book.find_all('a')
            if len(items) > 1:
                count += 1
                title = items[1].text.replace('[litres]', '').replace('(СИ)', '').replace('[СИ]', '').replace('[СИ litres]', '').replace('[сборник litres]', '').replace('[АТ]', '').strip()
                title = remove_string_with_brackets(title)
                if check_is_title_exists_by_fuzz(title):
                    print(f'Книга {title} уже добавлена, пропускаем.')
                    continue 
                # if check_is_title_exists(title):
                #     print(f'Книга {title} уже добавлена, пропускаем.')
                #     continue 
                book['title'] = title
                book['authors'] = [items[0].text]
                book['url'] = base_url + items[1]['href']
            try:
                book_extended = get_one_book(book['url'])
            except Exception as e:
                print(f'Error: {e}. Skip book')
                continue
            if book_extended:
                book['series'] = book_extended['series']
                book['description'] = book_extended['description']
                book['genres'] = book_extended['genres']
                book['cover'] = book_extended['cover']
                book['fb2_link'] = book_extended['fb2_link']
                book['epub_link'] = book_extended['epub_link']
                books.append(book)
                title = book['title']
                print(f'{count}. Book {title} added')
                # if count == 3:
                #     break
            else:
                continue
        return books
    else:
        print(f'Books request error: {response.status_code}')
        return False
    

def get_one_book(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        book = {}
        genres = soup.find_all('a', class_='genre')
        genres = [genre.text for genre in genres]
        p_blocks = soup.find_all('p')
        p_blocks = [p.text for p in p_blocks]
        description = p_blocks[1]
        book['series'] = ''
        book['genres'] = genres
        book['description'] = description
        book['cover'] = ''
        try:
            book['cover'] = base_url + soup.find('img', {'alt': 'Cover image'})['src']
        except:
            try:
                book['cover'] = base_url + soup.find('img', class_='bb-image')['src']
            except:
                book['cover'] = ''
        all_links = soup.find_all('a')
        series = [link.text for link in all_links if '/s/' in link['href']]
        if series:
            series = series[0]
            series = remove_string_with_brackets(series)
            book['series'] = series
        txt_links = ''
        fb2_links = [base_url + link['href'] for link in all_links if link.text == '(fb2)']
        epub_links = [base_url + link['href'] for link in all_links if link.text == '(epub)']
        if not epub_links:
            epub_links = [base_url + link['href'] for link in all_links if link.text == '(скачать epub)']
        try:
            book['fb2_link'] = fb2_links[0]
        except:
            book['fb2_link'] = ''
            print('Отсутствует ссылка на загрузку fb2')
        try:
            book['epub_link'] = epub_links[0]
        except:
            book['epub_link'] = ''
            print('Отсутствует ссылка на загрузку epub')
        return book
    
        # if len(all_links) != 0:
        #     book['fb2_link'] = all_links[0]
        #     return book
        # else:
        #     print(f'ссылка на fb2 не найдена, пропускаем')
        #     return False
    else:
        print(f'Book request error: {response.status_code}')
        return False


def main():
    init_env()
    books = get_books(search_url)
    count = 0
    for book in books:
        if count > 5:
            break
        if not book['fb2_link'] or not book['epub_link']:
            print('Отсутствуют ссылки на fb2 или epub. Пропускаем')
            continue
        slug_title = slugify_title(book['title'])
        fb2_book_filename = download_file(book['fb2_link'], books_dir, slug_title)
        fb2_file_size = os.path.getsize(f'{books_dir}/{fb2_book_filename}')
        if fb2_file_size < MIN_FB2_SIZE:
            print('Файл слишком маленький, пропускаем')
            continue
        epub_book_filename = download_epub_file(book['epub_link'], books_dir, slug_title)
        cover_filename = download_cover(book['cover'], covers_dir, slug_title)
        pdf_book_filename = convert_fb2_to_pdf(fb2_book_filename, books_dir)



        # txt_filename = extract_txt_from_fb2(fb2_book_filename, books_dir)
        if get_file_size(pdf_book_filename, books_dir) > MAX_PDF_SIZE:
            print(f'Файл {pdf_book_filename} слишком большой, пропускаем')
            continue
        if not cover_filename:
            cover_filename = default_picture_filename
            shutil.copy(cover_filename, covers_dir)
        description, genres_names, genres_ids = get_description(pdf_book_filename, books_dir)

        if description and genres_names and genres_ids:
            print(f'Genres IDS: {genres_ids}')
            genres_urls = [get_category_link_by_id(id) for id in genres_ids]
            genres_dict = dict(zip(genres_names, genres_urls))
            genres = [f'<a href=\"{genres_dict[genre]}">{genre}</a>' for genre in genres_dict]
            book['genres'] = genres[:3]
            book['content'] = f'[xyz-ips snippet="Card"]\n<h2>Содержание книги</h2>\n{description}'
            book['categories'] = genres_ids
            authors_ids, authors_urls, author_slug = get_or_create_tag(book['authors'])
            book['tags'] = authors_ids
            authors_dict = dict(zip(book['authors'], authors_urls))
            authors = [f'<a href=\"{authors_dict[book]}">{book}</a>' for book in authors_dict]
            book['acf_series'] = ''
            if book['series']:
                series_name = book['series']
                series_id, series_url = get_or_create_series(series_name)
                book['categories'].append(series_id)
                series = f'<a href=\"{series_url}">{series_name}</a>'
                book['acf_series'] = series
            book['authors'] = authors
            book['avtor'] = ', '.join(book['authors'])
            book['yazyk'] = 'Русский'
            book['year'] = '2024'
            book['featured_media'] = upload_media(cover_filename, covers_dir)
            book['choose_file_fb2'] = upload_book(fb2_book_filename, books_dir)
            book['choose_file_epub'] = upload_book(epub_book_filename, books_dir)
            title_slug  = extract_title_slug_from_fb2(fb2_book_filename, books_dir)
            if not title_slug:
                print(f'Не найдено название книги в мета тегах FB2. Пропускаем.')
                continue
            reedon_link = f'https://electrobook.ru/read/{title_slug}'
            book['reedon_link'] = reedon_link
            count += 1
            id, book_slug = create_post(book)
            add_title_to_db(book['title'])
            delete_all_files_in_directory(books_dir)
            delete_all_files_in_directory(covers_dir)
        else:
            print(f'Описание и жанр не получены, возможно закончилась подписка на ChatPDF')
            # count += 1
            # add_title_to_db(book['title'])
            continue


if __name__ == '__main__':
    main()