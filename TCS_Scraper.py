from bs4 import BeautifulSoup

import urllib.request

def get_teams():
    url = "https://compete.tespa.org/tournament/75/phase/1"
    page = urllib.request.urlopen(url)
    # "wb" because page.read() gives us bytes so we write bytes
    with open("teams_page.html", "wb") as teams_page:
        content = page.read()
        teams_page.write(content)

def soup():
    with open("teams_page.html", "rb") as teams_page:
        soup = BeautifulSoup(teams_page.read(), "html.parser")

    # Print page
    # print("soup.prettify:", soup.prettify())

    # Print all tags
    print("\nEach tag in soup")
    for tag in soup:
        print(tag)

    # Print table
    tableTag = soup.table
    print("\ntableTag:", tableTag)
    print("\ntableTag.name:", tableTag.name)
    tableAttributes = tableTag.attrs
    print("\ntableAttributes:", tableAttributes)

soup()