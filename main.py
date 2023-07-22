import os
import requests
import scrap

URLS = {
    "URL_clio":     "https://www.autoscout24.ch/fr/voitures/renault--clio?hpfrom=170&hpto=185&make=66&model=460&vehtyp=10",
    "URL_tuonoV4":  "https://www.motoscout24.ch/fr/motos/aprilia--tuono?kmto=10000&ccmfrom=1000&make=93&model=1259&typename=fact"
}

def generate_url(base_url, page_number=1):
    if page_number == 1:
        return base_url
    else:
        return f"{base_url}&page={page_number}"

def page_exists(url):
    response = requests.get(url)
    return response.status_code == 200

def main():
    for key, base_url in URLS.items():
        page_number = 1
        while True:
            url = generate_url(base_url, page_number)
            if page_exists(url):
                os.environ[f'{key}_{page_number}'] = url
                page_number += 1
            else:
                break
    scrap.run_scraping()

if __name__ == "__main__":
    main()
