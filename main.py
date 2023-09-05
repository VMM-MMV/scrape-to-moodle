# -*- coding: utf-8 -*-
import requests, re, time, os
from bs4 import BeautifulSoup

def make_connection(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def find_link(question_number, soup):
    question_link = soup.find('a', string=lambda t: t and f'Question {question_number}' in t)

    if question_link:
        return question_link['href']
    else:
        return None


def find_text(soup):
    entry_content_div = soup.find('div', class_='entry-content')

    lis = []

    if entry_content_div:
        current_element = entry_content_div.next_element
        count = 0
        while count < 3 and current_element:
            if current_element.name == 'p':
                cleaned_text = clean_text(current_element.text)

                if "rightAnswer" in str(current_element):
                    lis.append(("rightAnswer " + cleaned_text).split("\n"))
                else:
                    lis.append(cleaned_text.split("\n"))

                count += 1

            current_element = current_element.next_element
        return [x for y in lis for x in y] #flatten the list: 2D -> 1D, then return it
    else:
        return None


def text_to_moodle(lis, num):
        xml_string = ""
        xml_string += f"""\n    <question type="multichoice">
        <name>
            <text>Q-{num:03}</text>
        </name>
        <questiontext format="html">
            <text><![CDATA[<p>{lis[0]}</p>]]></text>
        </questiontext>
        <generalfeedback format="html">
            <text></text>
        </generalfeedback>
        <defaultgrade>1.0000000</defaultgrade>
        <penalty>0.3333333</penalty>
        <hidden>0</hidden>
        <single>true</single>"""
        
        for i in range(1,5):
            if "rightAnswer" in lis[i]:
                xml_string += f"""\n        <answer fraction="100">
            <text>{lis[i].replace("rightAnswer ", "")[2:]}</text>
        </answer>"""
            else:
                xml_string += f"""\n        <answer fraction="0">
            <text>{lis[i][2:]}</text>
        </answer>"""   
        xml_string += "\n    </question>"
        return xml_string    
    

def write_to_file(xml_string):
    xml_full_string = """<?xml version="1.0" encoding="UTF-8"?>\n<quiz>"""

    xml_full_string += xml_string

    xml_full_string += """\n</quiz>"""

    with open("moodle.xml", "w") as file:
        file.write(xml_full_string)


def clean_text(text):
    text = text.replace("Explanation:","").replace("Show Answer","").replace("&","and")
    return re.sub(r'[^a-zA-Z0-9 .,\n]', '', r"{}".format(text.strip()))


def display_broken_questions(li):
    for i in li:
        print("Question Number:", i[0], i[1])

# Different links
# [https://www.briefmenow.org/emc/which-implementation-of-distributed-content-architecture-provides-for-both-content-and-metadata-to-be-synchronized-across-multiple-repositories/
# https://www.briefmenow.org/emc/what-is-created-by-the-content-server-as-a-result-of-the-copy-operation/
# ]


# Make a first connection
url = "https://www.briefmenow.org/emc/which-implementation-of-distributed-content-architecture-provides-for-both-content-and-metadata-to-be-synchronized-across-multiple-repositories/"
soup = make_connection(url)

xml_body = ""
num_of_questions = 233
list_of_broken_questions = []

broken = 0
i = 1
while(1):
    print(round((i-2)*100/(num_of_questions),1), "%")
    
    url = find_link(i, soup)

    if url is None: 
        print(f"No URL found for question number {i}. Exiting loop.")
        os.system("clear")
        break

    try:
        soup = make_connection(url)
    except ConnectionError:
        time.sleep(60)
        soup = make_connection(url)
    text = find_text(soup)

    try:
        xml_body += text_to_moodle(text, i-broken-1)
    except IndexError:
        list_of_broken_questions.append((i, text))
        broken+=1
    os.system("clear")
    i += 1

write_to_file(xml_body)

print("100.0 %")
print("The Amount Of Broken Questions:", broken)
print(display_broken_questions(list_of_broken_questions))


# Legacy code
# if entry_content_div:
    #     p_val = entry_content_div.find_all('p')

    #     big_lis = []

    #     counter = 0
    #     for i in p_val:
    #         counter+=1
    #         if counter < 4:
    #             val_of_i = str(i).split("\n")
    #             lis = []
    #             for j in val_of_i:
    #                 if ("<p" in j):
    #                     lis.append(clean_text(j))

    #             if lis:
    #                 big_lis.append([x for x in lis if x]) #append all the non empty values of the list

    #     return [x for y in big_lis for x in y] #flatten the list: 2D -> 1D, then return it
    # else:
    #     return None