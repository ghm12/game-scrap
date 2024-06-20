import requests
import json
from bs4 import BeautifulSoup

class ScrapGOG:
  def __init__(self):
    self.base_url = 'https://www.gog.com/en/games'

  # Pega os dados de {amount_of_games} jogos
  def get_games_data(self, amount_of_games):
    ret = list()
    counter = 0
    current_page = 0

    while counter < amount_of_games:
      page_url = self.get_next_page_url(current_page)
      urls = self.parse_page(page_url)

      # Se não tem nenhuma URL de página de jogo, não tem jogos para pegar dados
      if not urls:
        break

      for url in urls:
        name, genre, companies, price = self.parse_game_page(url)
        counter += 1

        data = {"URL": url,
                #"Number": counter,
                "Name": name,
                "Genre": genre,
                "Companies": companies,
                "Price": price}

        ret.append(data)

        #print("Number:", counter)
        print("URL:", url)
        print("Name:", name)
        if genre != "Not specified":
          print("Genre:", ', '.join(genre))
        else:
          print("Genre:", genre)
        print("Companies:", ', '.join(companies))
        print("Price:", price)

        if counter >= amount_of_games:
          break

        print(".....")

      current_page += 1

    return ret

  # Pega o URL da próxima página
  def get_next_page_url(self, current_page_number):
    return self.base_url + f"?page={current_page_number+1}"

  # Dado um URL, retorna uma lista de URLs da página dos jogos listados
  def parse_page(self, url):
    urls = list()

    req = requests.get(url)
    html_parse = BeautifulSoup(req.content, 'html.parser')
    listed_games = html_parse.findAll("product-tile")

    for game in listed_games:
      link = game.find("a").get("href")
      urls.append(link)

    return urls

  # Dado um URL de uma página de jogo, retorna o nome, gênero, companhias e o preço do jogo
  def parse_game_page(self, url):
    name = ""
    genres = list()
    companies = list()
    price = list()

    req = requests.get(url)
    html_parse = BeautifulSoup(req.content, 'html.parser')

    # Obtém o nome
    name = html_parse.find("h1", class_="productcard-basics__title").string.strip()

    # Obtém a lista de gêneros
    genre_details = html_parse.findAll("div", class_="table__row details__row")
    for details in genre_details:
      label = details.find("div", string="Genre:")

      if label:
        genre_div = details.findAll("a")
        for genre in genre_div:
          if genre.string not in genres:
            genres.append(genre.string)
        break

    # Obtém o nome das companhias
    company_details = html_parse.findAll("div", class_="table__row details__rating details__row")
    for details in company_details:
      labels = details.findAll("div")

      for i in range(len(labels)):
        if labels[i].string and "Company" in labels[i].string:
          company_div = labels[i+1].findAll("a")
          for company in company_div:
            if company.string not in companies:
              companies.append(company.string)
          break

      if companies:
        break

    # Obtém o preço
    price_details = html_parse.find("script", type="application/ld+json")
    price_json = json.loads(price_details.string)
    price.append(price_json["offers"]["price"])
    price.append(price_json["offers"]["priceCurrency"])

    price = ' '.join(price)

    return name, genres, companies, price

  # Escreve os dados de data para um arquivo json e realiza o download
  def to_file(self, data):
    with open('games_gog.json', 'w') as games:
      games.write(str(json.dumps(data, indent=4)))


class ScrapNuuvem:
  def __init__(self):
    self.base_url = "https://www.nuuvem.com/br-en/catalog/drm/steam/platforms/pc/types/games/"


  def get_games_data(self, amount_of_games):
    ret = list()
    counter = 0
    current_page = 0

    while counter < amount_of_games:
      page_url = self.get_next_page_url(current_page)
      urls = self.parse_page(page_url)

      # Se não tem nenhuma URL de página de jogo, não tem jogos para pegar dados
      if not urls:
        break

      for url in urls:
        name, genre, companies, price = self.parse_game_page(url)
        counter += 1

        data = {"URL": url,
                #"Number": counter,
                "Name": name,
                "Genre": genre,
                "Companies": companies,
                "Price": price}

        ret.append(data)

        #print("Number:", counter)
        print("URL:", url)
        print("Name:", name)
        if genre != "Not specified":
          print("Genre:", ', '.join(genre))
        else:
          print("Genre:", genre)
        print("Companies:", ', '.join(companies))
        print("Price:", price)

        if counter >= amount_of_games:
          break

        print(".....")

      current_page += 1

    return ret

  # Pega o URL da próxima página
  def get_next_page_url(self, current_page_number):
    return self.base_url + f"/page/{current_page_number+1}"

  # Dado um URL, retorna uma lista de URLs da página dos jogos listados
  def parse_page(self, url):
    urls = list()

    req = requests.get(url)
    html_parse = BeautifulSoup(req.content, 'html.parser')
    listed_games = html_parse.findAll("div", {"class": "product-card--grid"})

    for game in listed_games:
      link = game.find("a").get("href")
      urls.append(link)

    return urls

  def parse_game_page(self, url):
    name = ""
    genres = list()
    companies = list()
    price = list()

    req = requests.get(url)
    html_parse = BeautifulSoup(req.content, 'html.parser')

    # Obtém o nome
    name = html_parse.find("meta", {"itemprop": "name"}).get("content")

    # Obtém a lista de gêneros
    genre_details = html_parse.find("meta", {"itemprop": "genre"})
    if genre_details:
      genre_details = genre_details.get("content")
      genres = genre_details.split(", ")
    else:
      genres = "Not specified"

    # Obtém o nome das companhias
    developer = html_parse.find("meta", {"itemprop": "author"})
    if developer: # sometimes there's no developer
      developer = developer.get("content").split(", ")
      companies += developer

    publisher = html_parse.find("meta", {"itemprop": "publisher"})
    if publisher: # sometimes there's no publisher
      publisher = publisher.get("content").split(", ")
      companies += publisher

    companies = list(set(companies)) # set removes duplicates in case author = publisher

    # Obtém o preço
    currency = html_parse.find("meta", {"itemprop": "priceCurrency"}).get("content")
    value = float(html_parse.find("meta", {"itemprop": "price"}).get("content"))
    price = '{:.2f}'.format(value) + ' ' + currency

    return name, genres, companies, price

    # Escreve os dados de data para um arquivo json e realiza o download
  def to_file(self, data):
    with open('games_nuuvem.json', 'w') as games:
      games.write(str(json.dumps(data, indent=4)))

print("---- GOG SCRAPPER ----")
gog = ScrapGOG()
data_gog = gog.get_games_data(500)
gog.to_file(data_gog)

print("\n")

print("---- NUUVEM SCRAPPER ----")
nuuvem = ScrapNuuvem()
data_nuuvem = nuuvem.get_games_data(500)
nuuvem.to_file(data_nuuvem)
