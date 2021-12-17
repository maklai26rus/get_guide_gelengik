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


# def get_url(url):
#     """Получаем все страницы с категориями"""
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "lxml")
#     pages_count = soup.find_all("h3", class_="category-widget__title")
#     url_page_href = [fi.find("a").get('href') for fi in pages_count]
#     url_category = [URL + i for i in url_page_href]
#     return url_category


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
            _p = get_max_page(_page)
            save_cvc_page(_p)

        # return url_category_data


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

async def gather_data():
    async with aiohttp.ClientSession() as session:
        response = await session.get(URL, headers=headers)

        soup = BeautifulSoup(await response.text(), "lxml")
        pages_count = soup.find_all("h3", class_="category-widget__title")
        url_page_href = [fi.find("a").get('href') for fi in pages_count]
        url_category = [URL + i for i in url_page_href]
        tasks = []
        # task = asynciocreate_task([URL + i for i in url_page_href])
        for page in url_category:
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    tic = time.perf_counter()
    asyncio.run(gather_data())
    toc = time.perf_counter()
    print(f"Вычисление заняло {toc - tic:0.4f} секунд")


if __name__ == "__main__":
    main()
