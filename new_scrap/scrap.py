from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def fetch_vehicle_urls(base_url):
    # Configuration pour utiliser Remote WebDriver
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor='http://chrome:4444/wd/hub',  # Notez l'adresse du Selenium server dans Docker
        desired_capabilities=DesiredCapabilities.CHROME,
        options=options
    )

    all_urls = []
    max_pages = 6000  # Nombre maximum de pages à scraper
    for page in range(1, max_pages + 1):
        print("In the while loop")
        first_url = f"{base_url}"
        current_url = f"{base_url}&pagination%5Bpage%5D={page}"
        if page == 1:
            current_url = first_url
        driver.get(current_url)
        
        # Utiliser Selenium pour extraire les URLs
        elements = driver.find_elements_by_xpath('//*[@id="__next"]/div/div[2]/div[1]/main/ul/li/article/a')
        if not elements:
            print(f"No URLs found on page {page}")
            break
        
        for element in elements:
            url = element.get_attribute('href')
            print(f"Found URL: {url}")
            all_urls.append(url)

        time.sleep(1)  # Delay pour simuler le comportement humain

    driver.quit()
    return all_urls
