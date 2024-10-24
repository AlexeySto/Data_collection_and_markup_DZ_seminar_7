from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import csv


# Прокручиваем страницу и записываем все ссылки,
def get_links(url, request, driver):
    
    # Открываем ссылку
    driver.get(url)
    time.sleep(4)

    # Ищем строку поиска
    input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchInput")))
    # Вводим фразу поиска и нажимаем Enter
    input.send_keys(request)
    input.send_keys(Keys.ENTER)
    time.sleep(4)
    while True:
        count = None # Счетчик элементов на странице
        while True:
            time.sleep(4)
            # Ждем загрузки объекта
            cards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//article[@id]')))
            if len(cards) == count: # Выходим из цикла, если при прокрутке страницы, количество товаров не меняется
                break
            count = len(cards)
            
            driver.execute_script('window.scrollBy(0, 1800)') # Прокручиваем страницу выполняя JAVA Script
            time.sleep(2)

        # На полностью загруженной странице соберём ссылки на товары
        url_list = [card.find_element(By.XPATH, './div/a').get_attribute('href') for card in cards]

        # Проверяем есть ли кнопка next
        try:
            button = driver.find_element(By.CLASS_NAME, "pagination-next")
            actions = ActionChains(driver)
            actions.move_to_element(button).click()
            actions.perform()
        except:
            break
    
    print(f'Всего получено: {len(url_list)} ссылок на книги')
    return set(url_list) # Возвращаем список ссылок

# Просматриваем все ссылки
def get_items_info(url_list, driver):
    wait = WebDriverWait(driver, 10)
    items_list = []
    for url_item in url_list:
        driver.get(url_item)
        # Собираем информацию о товарах
        name = wait.until(EC.presence_of_element_located((By.XPATH, "//h1"))).text
        price = get_price(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'price-block__final-price'))))
        brend = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-page__header-brand"))).text
        url = url_item
        description = get_description(labels = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//th'))), params = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//td'))))

        items_list.append([name, price, brend, url, description])
    return items_list # Возвращаем список товаров

def get_price(price_items):
    try:
        return float(re.sub(r'[^\d.]+', '', price_items[len(price_items) - 1].text))
    except Exception:
        return None
    
def get_description(labels, params):
    return {label.text: param.text for label, param in zip(labels, params)}
    
# сохраняем данные в csv
def save_to_csv(items_list, file_name):
    with open(file_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='excel', delimiter=';')
        writer.writerow(['name', 'price', 'brend', 'url', 'description'])
        writer.writerows(items_list)
        print(f'Данные срхранены в файл: {file_name}.')
    
    
if __name__ == '__main__':
    # Ссылка на сайт
    url = 'https://www.wildberries.ru'
    request = input('Введите название интересующего вас товара: ')
    file_name = request + ' data.csv' # Имя файла для записи
    
    options = Options()
    # Запуск браузера с развернутым экраном
    options.add_argument('start-maximized')
    
    # Будем использовать браузер Chrom
    driver = webdriver.Chrome(options=options)
    
    url_list = get_links(url, request, driver)
    items_list = get_items_info(url_list, driver)
    save_to_csv(items_list, file_name)
