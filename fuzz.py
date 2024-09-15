from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from flibusta.tools import remove_non_letters_and_digits, remove_string_with_brackets, check_is_title_exists_by_fuzz

# str1 = 'Крепкий орешек'
# str2 = 'Крепкий союз'
# a = fuzz.ratio(str1, str2)
# print(f'Сравниваем строку "{str1}" со строкой "{str2}" Результат: {a}%')

# result = check_is_title_exists_by_fuzz('Кто внутри 2')
# print(result)

# Пример использования функции
# input_string = 'Алхимик [3 сент. 2024, litres] aaaa ssss'
# output_string = remove_string_with_brackets(input_string)
# print(output_string)  # Выведет: Hello, 123! This is a test string with numbers.

from flibusta.tools import extract_title_slug_from_fb2

slug = extract_title_slug_from_fb2('book.fb2', 'books')
print(slug)