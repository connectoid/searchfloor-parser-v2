from flibusta.tools import remove_non_letters_and_digits

from flibusta.settings import db_file

def convert(filename):
    titles_list = []
    with open(filename, 'r') as file:
        for line in file:
            title = remove_non_letters_and_digits(line)
            titles_list.append(title)
    new_filename = f'new_{filename}'
    with open(new_filename, 'w') as f:
        for item in titles_list:
            f.write(item + '\n')

if __name__ == '__main__':
    convert(db_file)
