from draft import *
a = ['r', 'e', 'a', 's', 'd']
for i, x in enumerate(a):
    print(f"{i} {x}")

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
                "directions": description,
                "instructions": instruction_dict,
                "nutrients": nutritions_dict,
            }
        )


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
