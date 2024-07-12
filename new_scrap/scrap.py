from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def fetch_vehicle_urls(base_url):
	options = webdriver.ChromeOptions()
	options.headless = True
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.set_capability("browserName", "chrome")
	options.set_capability("browserVersion", "126.0")
	options.set_capability("platformName", "Linux")

	driver = webdriver.Remote(
		command_executor='http://chrome:4444/wd/hub',
		options=options
	)

	all_urls = []
	max_pages = 600
	for page in range(0, max_pages + 1):
		urlcount = 0
		print("In the while loop")
		first_url = f"{base_url}"
		current_url = f"{base_url}&pagination%5Bpage%5D={page}"
		if page == 0:
			current_url = first_url
		driver.get(current_url)

		DEBUG = False
		if DEBUG:
			print(f"Starting DEBUG")
			time.sleep(5)  # Attendez que la page charge complètement
			driver.save_screenshot(f"/app/data/page_{page}.png")
			html_content = driver.page_source
			with open(f"/app/data/page_{page}.html", 'w', encoding='utf-8') as f:
				f.write(html_content)  # Sauvegarde le HTML de la page dans un fichier
		
		elements = driver.find_elements(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/main/ul/li/article/a')
		if not elements:
			print(f"No URLs found on page {page}")
			break
		
		for element in elements:
			url = element.get_attribute('href')
			print(f"Found URL: {url}")
			all_urls.append(url)
			# print le nombre d'URLs trouvées
			urlcount += 1
		if urlcount < 20:
			print(f"Last page is the {page}")
			break
		print(f"{urlcount} URLs found on page {page}")
		print()
		time.sleep(1)  # Delay pour simuler le comportement humain

	driver.quit()
	return all_urls
