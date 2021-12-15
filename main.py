from bs4 import BeautifulSoup
import requests
import time

URL = "https://gelend.spravker.ru"
FLIGHT_DATA = []


def get_url(url):
    """Получаем все страницы с категориями"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    pages_count = soup.find_all("h3", class_="category-widget__title")
    url_page_href = [fi.find("a").get('href') for fi in pages_count]
    url_category = [URL + i for i in url_page_href]
    return url_category


def get_url_category(url_category):
    """Перебираем выбраную категорию и получаем каждый элемент """
    _spisok_url = []
    for url_cat in url_category:
        response = requests.get(url_cat)
        soup = BeautifulSoup(response.text, "lxml")
        pages_count = soup.find_all("ul", class_="list-count list-count--rows list-count--inversion list-count--wide")
        url_page_href = [fi.find("a").get('href') for fi in pages_count]
        url_category_data = [URL + i for i in url_page_href]
        _spisok_url.append(url_category_data)
    return _spisok_url


# def get_data_category(category_data):
#     """Погрухаемся в глубь категорий"""
#     _spiso = []
#     for url_cat in category_data:
#         response = requests.get(url_cat[0])
#         soup = BeautifulSoup(response.text, "lxml")
#         pages_count = soup.find_all("div", class_="org-widget")
#         url_page_href = [fi.find("a").get('href') for fi in pages_count]
#         _spiso.append(url_page_href)
#
#         # url_category_data = [URL + i for i in url_page_href]
#     return _spiso


def get_max_page(url):
    """Проверка максимального количства переходов"""
    k = True
    n = 0
    list_url_page = []
    while k:
        n += 1
        ur = f'{url}page-{n}/'
        # break
        response = requests.get(ur)
        print(response.status_code, ur)
        if response.status_code == 200:
            list_url_page.append(ur)
        else:
            # del list_url_page[n - 1]
            k = False
    return list_url_page


def save_cvc_page(url):
    """получаем данные из каждой категории """
    for i in url:
        response = requests.get(i)
        soup = BeautifulSoup(response.text, "lxml")
        pages_count = soup.find_all("a", class_="org-widget-header__title-link")
        telefon = soup.find_all("div", class_="org-widget__spec")
        try:
            for ik in range(len(pages_count)):
                with open(f'BD.cvc', 'a', encoding='utf-8') as ff:
                    ff.write(str(pages_count[ik].text.strip() + ',' + telefon[ik].dd.text.strip() + "\n"))
        except AttributeError:
            pass


def main():
    tic = time.perf_counter()
    category = get_url(URL)
    category_data = get_url_category(category)
    for i in category_data:
        kt = get_max_page(i[0])
        save_cvc_page(kt)

    toc = time.perf_counter()
    print(f"Вычисление заняло {toc - tic:0.4f} секунд")


if __name__ == "__main__":
    main()
