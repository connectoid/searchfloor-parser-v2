import datetime

db_file = 'titles.txt'
api_keys_file = 'api_keys'
books_dir = 'books'
covers_dir = 'cover'


search_url = 'https://flibusta.is/stat/24'
base_url = 'https://flibusta.is'

title_postfix = ': скачать или читать онлайн'

endpoints = {
    'posts': 'https://electrobook.ru/wp-json/wp/v2/posts',
    'media': 'https://electrobook.ru/wp-json/wp/v2/media',
    'tags': 'https://electrobook.ru/wp-json/wp/v2/tags',
    'categories': 'https://electrobook.ru/wp-json/wp/v2/categories',
    'series': 'https://electrobook.ru/wp-json/wp/v2/categories',
}
prompt_description =  """
    Пиши просто и понятно как писал бы обычный человек, нужно чтобы не было понятно что это пишет ИИ!! Разбей текст на абзацы! Не пиши название самой книги!
    Текстом около 400-500 слов и не менее 4 абзацев, опиши о чем книга. Не нужно добавлять свои рассуждения, пиши только сухую информацию которая есть в книге очень простыми словами!
    Постарайся избегать фраз: "кроме того", "таким образом", "в заключении" и других подобных клише! 
    Избегай фраз "В этой книге рассказывается" и "Книга рассказывает". Включи разнообразные структуры предложений при вступлении. Избегай слова "переплетаются".    
"""

MAX_PDF_SIZE = 4000000
MIN_FB2_SIZE = 200000

api_keys_file = 'api_keys.txt'

login_params = {
    'id': '327720091',
    'first_name': 'Alexey',
    'username': 'alex_web',
    'photo_url': 'https://t.me/i/userpic/320/YLAbyzjRm0fLnTm8v4d3FS2IWEhMvyO13Fnj2_DPuF4.jpg',
    'auth_date': '1718334865',
    'hash': 'b896af95593ae3d817437d2741d442d081afdeff430d079141fe32ee5d7e15e0',
}


current_year = datetime.datetime.now().strftime("%Y")
current_date = datetime.datetime.now().strftime("%d.%m.%Y")

PARSE_INTERVAL = 0 # seconds

series_category_id = 12
exclude_category_names = ['Серия', 'read']
default_picture_filename = 'cover.jpg'
