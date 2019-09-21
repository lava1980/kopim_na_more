import bs4 
import email
import imaplib
import logging
import os 
import requests
import subprocess
import sys
import time

import config

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    level = logging.INFO,
                    filename = 'tgbot.log'
                    )


def ibank_get_summ(login, password):
    print('Стартуем проверку денег на балансе...\n')
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36'
    }
    # Работает без заголовка. Вставил на всякий случай, вдруг на сервере будет защита от ботов
    login_data = {'login': login,
                  'password': password,
                  'typeSessionKey': '1'
                  }
    with requests.Session() as s: # создаём объект Session
        url = 'https://login.belinvestbank.by/signin' # блок action в html-коде
        url2 = 'https://login.belinvestbank.by/signin2'
        s.post(url, data=login_data, headers=headers) # в POST-запросе передаём параметры и заголовки
        s.get(url2)
        print('Проверяем мыло...\n')
        time.sleep(15)
        send_code(url2, headers, s)
        ibank_page = s.get('https://ibank.belinvestbank.by') # в GET-запросе получаем код страницы
        s.get('https://login.belinvestbank.by/logout') # Разлогиниваемся
        print('Успешно зашли на страницу. Смотрим сумму...\n')

    soup = bs4.BeautifulSoup(ibank_page.text, features='lxml')
    summ = soup.select('#dLabel p')[0].getText()
    summ = summ.strip()
    print('Сумма: ' + summ + '\n')    
    return summ


def send_code(url, headers, session):
    login, passw = config.auth_data.get('mail_auth_data')
    print('Получаем код авторизации...\n')
    code = get_ibank_code(login, passw)
    code_data = {'action': '1',
                    'key': code}
    session.post(url, data=code_data, headers=headers)


def get_ibank_code(login, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(login, password)
    mail.list()
    # Выводит список папок в почтовом ящике.
    mail.select('inbox')  # Подключаемся к папке "входящие".
    result, data = mail.uid('Search', None, '(FROM "info@belinvestbank.by")')
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]  # Тело письма в необработанном виде 

    email_message = email.message_from_bytes(raw_email)
    # из содержимого можно достать кодировку (charset)

    body = email_message.get_payload(decode=True) # формат bytes
    body = body.decode('ISO-8859-5')
    # декодируем байты обратно в кодировку письма. Берём из
    # заголовков письма: Content-Type: text/plain; charset=ISO-8859-5

    code = body.find('банкинг": ', 240, 250)
    code = body[244:248]
    print('Код авторизации успешно получен: ' + code + '\n')
    return code


def check_account(summa_deneg_string):
    print('Проверяем или был приход...\n')
    path_to_settings = os.path.join(os.getcwd(), 'ibank_settings.ini')
    summ = summa_deneg_string.replace(',', '.')
    substr_num = summ.find('BYN') - 1
    summa_string = summ[:substr_num]
    summa_float = float(summa_string)

    with open(path_to_settings, 'r') as old_summ:
        old_summ = old_summ.read()
        float_old_summ = float(old_summ)

    if summa_float > float_old_summ:
        summa_prihod = summa_float - float_old_summ
        summa_prihod_string = str(summa_prihod).replace('.', ',') + ' BYN'
        os.remove(path_to_settings)
        with open(path_to_settings, 'w') as ibank_settings_file:
            ibank_settings_file.write(summa_string)
        print('Пришли деньги. Сумма = ' + str(summa_float))
        return summa_float  
    else: print('Прихода не было.')  

    if summa_float != float_old_summ:
        os.remove(path_to_settings)
        ibank_settings_file = open(path_to_settings, 'w')
        ibank_settings_file.write(summa_string)
        ibank_settings_file.close()
    return -1



    





if __name__ == "__main__":
    login, passw = config.auth_data.get('ibank_auth_data')
    summ = ibank_get_summ(login, passw)
    p = check_account(summ) # сумма -- строка формата 35,05 BYN
    print(str(p))
