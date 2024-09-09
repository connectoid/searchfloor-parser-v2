from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from flibusta.tools import remove_non_letters_and_digits, remove_string_with_brackets

# str1 = 'Ваше Сиятельство 9'
# str2 = 'Ваше Сиятельство 10'
# a = fuzz.ratio(str1, str2)
# print(f'Сравниваем строку "{str1}" со строкой "{str2}" Результат: {a}%')


# Пример использования функции
input_string = 'Алхимик [3 сент. 2024, litres] aaaa ssss'
output_string = remove_string_with_brackets(input_string)
print(output_string)  # Выведет: Hello, 123! This is a test string with numbers.
