import zipfile
import itertools
import string
from tqdm import tqdm

zip_file = 'password_protected.zip'
charset = string.ascii_lowercase + string.digits


def crack_zip_password(zip_file, charset, min_length=1, max_length=8):
    for password_length in range(min_length, max_length + 1):
        print(f'Testing password length {password_length}')

        passwords = itertools.product(charset, repeat=password_length)
        for guess in tqdm(passwords, unit='attempts'):
            guess = ''.join(guess)

            try:
                zipfile.ZipFile(zip_file).extractall(pwd=guess.encode('utf-8'))
                print(f'Password found: {guess}')
                return guess
            except RuntimeError:
                continue

    print('Password not found, failed with given criteria.')
    return None


if __name__ == '__main__':
    password = crack_zip_password(zip_file, charset)
    if password:
        print('Password found:', password)
    else:
        print('Password not found')