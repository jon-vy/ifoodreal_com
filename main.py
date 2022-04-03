import re
import time
import requests
from bs4 import BeautifulSoup
import lxml
from user_agent import generate_user_agent
import asyncio
import aiohttp
import json
from random import randint


total_list = []

def get_url():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": generate_user_agent()
    }
    url = "https://ifoodreal.com/clean-eating-recipes-dinners/"
    r = requests.get(url=url, headers=headers)
    html_cod = r.text
    soup = BeautifulSoup(html_cod, "lxml")
    urls = soup.find_all("h3")
    links_list = []
    for link in urls:
        try:
            links_list.append(link.contents[0].attrs['href'])
        except: pass
    return links_list


async def pars_date(session, url):
    try:
        await asyncio.sleep(randint(1, 5))
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "User-Agent": generate_user_agent()
        }
        async with session.get(url=url, headers=headers) as r:
            html_cod = await r.text()
            soup = BeautifulSoup(html_cod, "lxml")
            name = soup.find("h2", class_=re.compile('wprm-recipe-name')).text
            description = soup.find("div", class_=re.compile('wprm-recipe-summary')).text

            try:
                photo = soup.find_all("figure", class_=re.compile("wp-block-image"))[0].find('img').get('data-lazy-srcset').split(',')[0].split(' ')[0]
            except IndexError:
                p_list = soup.find_all("p")
                for p in p_list:
                    if p.find('img') != None:
                        photo = p.find('img').get('data-lazy-src')
                        break
                    else:
                        pass
            except AttributeError:
                photo = soup.find_all("figure", class_=re.compile("wp-block-image"))[0].find('img').get('srcset').split(',')[0].split(' ')[0]

            wprm_recipe_time = soup.find_all("span", class_=re.compile('wprm-recipe-time'))
            Prep_Time = wprm_recipe_time[1].text
            Cook_Time = wprm_recipe_time[3].text

            try:
                Total_Time = wprm_recipe_time[5].text
            except IndexError:
                Total_Time = "No data"

            try:
                Servings = soup.find_all("span", class_=('wprm-recipe-servings-with-unit'))[0].text
            except IndexError:
                Servings = soup.find_all("span", class_=re.compile("wprm-recipe-servings"))[1].text

            Calories = soup.find_all("span", class_=('wprm-recipe-nutrition-with-unit'))[0].text

            ingredients_list = []
            ingredients = soup.find_all("li", class_=('wprm-recipe-ingredient'))
            for ingredient in ingredients:
                ingredients_list.append(ingredient.text)

            instruction_dict = {}
            div_instructions_group = soup.find_all("div", class_=('wprm-recipe-instruction-group'))
            for instruction in div_instructions_group:
                try:
                    chek = instruction.find('ul').find_all('li')[0].text  # если здесь есть текст то парсить h4
                    try:
                        instruction_name = instruction.find('h4').text
                        instruction_list = []
                        instruction_text = instruction.find('ul').find_all('li')
                        for i, instruction_str in enumerate(instruction_text):
                            instruction_list.append(instruction_str.text)
                        instruction_dict[instruction_name] = instruction_list
                    except AttributeError:
                        instruction_list = []
                        instruction_text = instruction.find('ul').find_all('li')
                        for i, instruction_str in enumerate(instruction_text):
                            instruction_list.append(instruction_str.text)
                        instruction_dict['instruction'] = instruction_list
                except IndexError:
                    pass

            nutritions_dict = {}
            span_nutritions = soup.find_all("span", class_=re.compile('wprm-nutrition-label-text-nutrition-container'))
            for nutrition in span_nutritions:
                nutritions_dict[nutrition.find_all('span')[
                    0].text] = f"{nutrition.find_all('span')[1].text} {nutrition.find_all('span')[2].text}"

            total_list.append(
                {
                    "name": name,
                    "photo": photo,
                    "link": url,
                    "Prep_Time": Prep_Time,
                    "cook_time": Cook_Time,
                    "Total_Time": Total_Time,
                    "servings": Servings,
                    "Calories": Calories,
                    "ingredients": ingredients_list,
                    "description": description,
                    "instructions": instruction_dict,
                    "nutrients": nutritions_dict,
                }
            )
        print(f"Обработал {url}")
    except:
        print(f"ошибка {url}")



async def gahter_date():
    async with aiohttp.ClientSession() as session:
        links_list = get_url()
        tasks = []  # список задач
        for link in links_list:  #[4:10]
            task = asyncio.create_task(pars_date(session, link))  # создал задачу
            tasks.append(task)  # добавил её в список
        await asyncio.gather(*tasks)


def main():
    asyncio.get_event_loop().run_until_complete(gahter_date())
    with open("ifoodreal.json", "w") as f:
        json.dump(total_list, f)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Время работы {total_time}")

