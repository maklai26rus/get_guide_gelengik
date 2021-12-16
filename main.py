from bs4 import BeautifulSoup
import requests
import time

URL = "https://gelend.spravker.ru"


def get_url(url):
    """Получаем все страницы с категориями"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    pages_count = soup.find_all("h3", class_="category-widget__title")
    url_page_href = [fi.find("a").get('href') for fi in pages_count]
    url_category = [URL + i for i in url_page_href]
    return url_category


def get_url_category(url_category):
    """Перебираем выбраную категорию и получаем каждый элемент в выбраной категории
    https://gelend.spravker.ru/avto.htm
    получаем
    'https://gelend.spravker.ru/avtoaksessuary/"""
    url_page_href = []
    url_category_data = []
    for url_cat in url_category:
        response = requests.get(url_cat)
        soup = BeautifulSoup(response.text, "lxml")
        pages_count = soup.find("ul",
                                class_="list-count list-count--rows list-count--inversion list-count--wide").find_all(
            'li')
        try:
            for i in pages_count:
                _url_cat = i.a.get('href')
                url_page_href.append(_url_cat)
        except AttributeError:
            continue
        url_category_data = [URL + i for i in url_page_href]

    return url_category_data


def get_max_page(url):
    """Проверка максимального количства переходов"""
    _true = True
    _page = 0
    list_url_page = []
    while _true:
        _page += 1
        ur = f'{url}page-{_page}/'
        response = requests.get(ur)
        if response.status_code == 200:
            list_url_page.append(ur)
        else:
            _true = False
    return list_url_page


def save_cvc_page(url):
    """получаем данные из каждой категории """
    for i in url:
        response = requests.get(i)
        soup = BeautifulSoup(response.text, "lxml")
        _name_org = soup.find_all("a", class_="org-widget-header__title-link")
        _phone = soup.find_all("div", class_="org-widget__spec")
        try:
            for _data in range(len(_name_org)):
                with open(f'BD.cvc', 'a', encoding='utf-8') as ff:
                    ff.write(str(_name_org[_data].text.strip() + ',' + _phone[_data].dd.text.strip() + "\n"))
        except AttributeError:
            pass


def main():
    tic = time.perf_counter()
    category = get_url(URL)
    category_data = get_url_category(category)
    for i in category_data:
        kt = get_max_page(i)
        save_cvc_page(kt)
    #
    toc = time.perf_counter()
    print(f"Вычисление заняло {toc - tic:0.4f} секунд")


if __name__ == "__main__":
    main()
