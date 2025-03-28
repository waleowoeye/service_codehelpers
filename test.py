import requests
from bs4 import BeautifulSoup
import csv
import uuid
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By


# Function to scrape product data and save it into CSV
def scrape_and_save_to_csv(url, csv_file_path='products.csv', max_products=20):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    session = requests.Session()  # Use a session to handle cookies and reuse connections

    try:
        # Send request to the main collection page using the session
        response = session.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        print("try for product container!")
        # Find product containers using the updated CSS selector
        product_containers = soup.find(attrs={"class": ["listing", "product-list", "product-per-row-4", "product-per-row-mobile-2", "list-item"]})
        print('Here are the product containers')
        print(product_containers)

        # Get all nested elements with classes
        if product_containers:
            nested_classes = {tuple(element.get('class')) for element in product_containers.find_all(True) if element.get('class')}
            print(nested_classes)
        else:
            print("Class not found!")

        product_count = 0
        for product in product_containers:
            # Extract product link (example: products/premax-super-natural-hairline...)
            print("Printing product link")
            product_link = product.find('a')['href']
            product_url = f"https://shop.luvmehair.com{product_link}"
            print(product_url)
    
    except Exception as e:
        print(f"Error: {e}")

# Example usage
scrape_and_save_to_csv('https://shop.luvmehair.com/collections/best-sellers', csv_file_path='products.csv', max_products=20)

