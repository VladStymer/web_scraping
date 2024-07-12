#!/usr/bin/env python3

import scrap
import time

def main():
    # print that the script is starting
    print("Starting the script...")
    time.sleep(10)
    # Call the correct function with a base URL parameter
    #base_url = "https://www.autoscout24.ch/fr/s?hadNoAccidentOnly=true&fuelTypes%5B0%5D=petrol&fuelTypes%5B1%5D=hev-petrol&fuelTypes%5B2%5D=mhev-petrol&fuelTypes%5B3%5D=phev-petrol&fuelTypes%5B4%5D=electric&horsePowerFrom=100&cubicCapacityFrom=1000"
    base_url = "https://www.autoscout24.ch/fr/s?hadNoAccidentOnly=true&fuelTypes%5B0%5D=petrol&fuelTypes%5B1%5D=hev-petrol&fuelTypes%5B2%5D=mhev-petrol&fuelTypes%5B3%5D=phev-petrol&fuelTypes%5B4%5D=electric&horsePowerFrom=100&cubicCapacityFrom=1000&mileageTo=4000&priceFrom=275000&priceTo=300000"
    urls = scrap.fetch_vehicle_urls(base_url)
    # print the number of URLs found
    print(f"Found {len(urls)} URLs")


if __name__ == "__main__":
    main()
