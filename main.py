"""
Обходим блокировки ботов CloudFlare, обращаемся к API и сохраняем html, далее парсим из этого html сам json с помощью lxml
Дело в шляпе
"""

import re
import time
import json
import undetected_chromedriver as uc
from lxml.html import fromstring

def get_product_info(result):
    """
    Забираем через API название, цену и характеристики товара и возвращаем словарь из них.
    """
    product = {}
    data = json.loads(result)
    widgets = data['widgetStates']
    for widget_name, widget_value in widgets.items():
        widget_value = json.loads(widget_value)
        if "webProductHeading" in widget_name:
            product["title"] = widget_value["title"]
        if ("webPrice" in widget_name and
                "isAvailable" in widget_value.keys()):
            if widget_value['isAvailable'] == True:
                product["price"] = widget_value["price"]
        if "webCharacteristics" in widget_name:
            product["characteristics"] = widget_value["characteristics"]
    return product

def main():
    page = input("Введите Ваш URL с OZON:\n")

    """
    Регулярное выражение для извлечения названия товара из url для дальнейшего запроса к API.
    
    Пример ссылки: https://www.ozon.ru/product/gel-dlya-stirki-laska-vosstanovlenie-color-dlya-tsvetnogo-zhidkoe-sredstvo-dlya-stirki-4l-66-stirok-176331184
    Будет получено: gel-dlya-stirki-laska-vosstanovlenie-color-dlya-tsvetnogo-zhidkoe-sredstvo-dlya-stirki-4l-66-stirok-176331184
    """
    result = re.sub(r'.*product/|/\?.*|', '', page)

    url = f'https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=/product/{result}/'

    options = uc.ChromeOptions()
    options.add_argument("--headless")
    driver = uc.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(3)
    except Exception as ex:
        print(ex)
    finally:
        source = driver.page_source
        result_json = fromstring(source).text_content()  # через lxml удаляем все html-теги
        driver.close()
        driver.quit()

        product = get_product_info(result_json)
        with open(f"{result}.json", "w", encoding="utf-8") as file:
            json.dump(product, file, ensure_ascii=False)

if __name__ == '__main__':
    while True:
        main()