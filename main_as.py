from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio
import time

URL = "https://gelend.spravker.ru"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/81.0.4044.96 YaBrowser/20.4.0.1461 Yowser/2.5 Safari/537.36',
    'accept': '*/*'}


async def gather_data():
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        response = await session.get(URL, headers=headers)

        soup = BeautifulSoup(await response.text(), "lxml")
        pages_count = soup.find_all("h3", class_="category-widget__title")
        url_page_href = [fi.find("a").get('href') for fi in pages_count]
        url_category = [URL + i for i in url_page_href]
        tasks = []
        for page in url_category:
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def get_page_data(session, page):
    """Перебираем выбраную категорию и получаем каждый элемент в выбраной категории
    https://gelend.spravker.ru/avto.htm
    получаем
    'https://gelend.spravker.ru/avtoaksessuary/"""

    async with session.get(url=page, headers=headers) as response:
        url_page_href = []
        url_category_data = []
        soup = BeautifulSoup(await response.text(), "lxml")
        pages_count = soup.find("ul",
                                class_="list-count list-count--rows list-count--inversion list-count--wide").find_all(
            'li')
        for i in pages_count:
            try:
                _url_cat = i.a.get('href')
                url_page_href.append(_url_cat)
            except AttributeError:
                continue
        url_category_data = [URL + i for i in url_page_href]
        for _page in url_category_data:
            _list_page = get_max_page(_page)
            await save_cvc_page(session, _list_page)


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


async def save_cvc_page(session, page):
    """получаем данные из каждой категории """
    _d = None
    for i in page:
        with open(f'save_url.txt', 'a', encoding='utf-8') as ff:
            ff.write(i + "\n")
        async with session.get(url=i, headers=headers) as response:
            try:
                soup = BeautifulSoup(await response.text(), "lxml")
                _name_org = soup.find_all("a", class_="org-widget-header__title-link")
                _phone = soup.find_all("div", class_="org-widget__spec")
                for _data in range(len(_name_org)):
                    _d = str(_name_org[_data].text.strip())
                    with open(f'BD20.cvc', 'a', encoding='utf-8') as ff:
                        ff.write(str(_name_org[_data].text.strip() + ',' + _phone[_data].dd.text.strip() + "\n"))
            except AttributeError as err:
                with open(f'BD_none.cvc', 'a', encoding='utf-8') as ff:
                    ff.write(_d + f' нету номера {err} \n')
                continue


def main():
    tic = time.perf_counter()
    asyncio.run(gather_data())
    toc = time.perf_counter()
    print(f"Вычисление заняло {toc - tic:0.4f} секунд")


if __name__ == "__main__":
    main()

# def save_cvc_page1():
#     """получаем данные из каждой категории """
#     # for i in url:
#     kki = ['https://gelend.spravker.ru/shtrafstoianki/page-1/', 'https://gelend.spravker.ru/avtosalony/']
#     _d = None
#     for i in kki:
#         response = requests.get(i)
#         try:
#             soup = BeautifulSoup(response.text, "lxml")
#             _name_org = soup.find_all("a", class_="org-widget-header__title-link")
#             _phone = soup.find_all("div", class_="org-widget__spec")
#             for _data in range(len(_name_org)):
#                 _d = str(_name_org[_data].text.strip())
#                 with open(f'BD.cvc', 'a', encoding='utf-8') as ff:
#                     # print(_phone[_data].dd.text.strip())
#                     ff.write(str(_name_org[_data].text.strip() + ',' + _phone[_data].dd.text.strip() + "\n"))
#         except AttributeError as err:
#             with open(f'BD.cvc', 'a', encoding='utf-8') as ff:
#                 ff.write(_d + ' нету номера \n')
#             continue
#
#
# save_cvc_page1()
