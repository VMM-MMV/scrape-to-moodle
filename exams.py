import requests
from bs4 import BeautifulSoup

URL = "https://www.briefmenow.org/emc/"
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

exam_links = soup.find_all('a', href=True, title=True, target='_blank')

for link in exam_links:
    exam_name = link['title']
    exam_code = link.text
    print(f"{exam_code}: {exam_name}")

