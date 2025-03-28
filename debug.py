import requests
from bs4 import BeautifulSoup
import csv
import uuid
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

'''
# Parse HTML with BeautifulSoup
#soup = BeautifulSoup(url, 'html.parser')

# Step-by-step check for each level of nesting
def debug_class_search(class_name):
    found = soup.find_all(class_=class_name)
    if found:
        print(f"Found elements with class '{class_name}':")
        for elem in found:
            print('-'*50)
            #print(elem.prettify())  # Prints the HTML structure of the element
            product_block = elem.find('div', class_='snippets-product-block')
            if product_block:
                product_title = product_block.get('data-product-title')
                product_url = product_block.get('data-product-url')
                variant_sku = product_block.get('data-variant-sku')

                print("Product Title:", product_title)
                print("Product URL:", product_url)
                print("Variant SKU:", variant_sku)
            else:
                print("Product block not found.")

            prices_block = elem.select(".snippets-product-block__price")
            for block in prices_block:
                highlighted_price = block.select_one(".snippets-product-block__price_highlight")
                original_price = block.select_one(".snippets-product-block__price_disabled")

                final_price = highlighted_price.text.   strip() if highlighted_price else "N/A"
                old_price = original_price.text.strip() if original_price else "N/A"

                print("Final Price:", final_price)
                print("Old Price:", old_price)


    else:
        print(f"Class '{class_name}' not found.")


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

session = requests.Session()  # Use a session to handle cookies and reuse connections



url = "https://shop.luvmehair.com/collections/best-sellers"
# Send request to the main collection page using the session
response = session.get(url, headers=headers)
response.encoding = 'utf-8'  # Ensure proper encoding
response.raise_for_status()
print("RESPONSE")
#print(response.headers)  # Check what content type the server is returning
#print(response.apparent_encoding)  # Detect encoding
#print(response.text[:500])  # Print first 500 characters of decoded text
print("END RESPONSE")

# Parse HTML with BeautifulSoup
response.encoding = response.apparent_encoding  # Detect and set the right encoding
soup = BeautifulSoup(response.content, 'html.parser')
print("SOUP")
#print(soup.prettify())  # See if product elements are in the HTML
print("END SOUP")

# Check each class separately
#class_list = ["container cf", "shopify-section", "collection", "filter-listing", "listing", "product-list", "product-per-row-4", "product-per-row-mobile-2"]
#class_list = ["product-per-row-mobile-2"]
class_list = ["list-item"]


for class_name in class_list:
    debug_class_search(class_name)
'''

#Global definition for beautifulsoup
def cook_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    session = requests.Session()  # Use a session to handle cookies and reuse connections

    try:
        # Send request to the main collection page using the session
        response = session.get(url, headers=headers)
        response.encoding = 'utf-8'  # Ensure proper encoding
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # Detect and set the right encoding
    
        #Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        return soup

    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to download and save images
def download_image(image_url, product_id, img_index):
    try:
        # Make the directory for storing images if not already present
        image_dir = f"product_images/{product_id}"
        os.makedirs(image_dir, exist_ok=True)

        # Send GET request to the image URL
        img_response = requests.get(image_url, stream=True)
        img_response.raise_for_status()  # Raise an exception for bad status codes

        # Extract the image file name and save the image
        img_filename = os.path.join(image_dir, f"{img_index+1}.jpg")
        with open(img_filename, 'wb') as img_file:
            for chunk in img_response.iter_content(chunk_size=128):
                img_file.write(chunk)

        print(f"Image {img_index + 1} saved for product {product_id}.")
        return img_filename
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


# Step-by-step check for each level of nesting
def debug_class_search(url, class_name):
    soup = cook_soup(url)
    found = soup.find_all(class_=class_name)
    product_list = []
    if found:
        print(f"Found elements with class '{class_name}':")
        for elem in found:
            product_block = elem.find('div', class_='snippets-product-block')
            if product_block:
                variant_sku = product_block.get('data-variant-sku')
                product_title = product_block.get('data-product-title')
                product_url = product_block.get('data-product-url')
                #print("Product URL:", product_url)
                #print("Variant SKU:", variant_sku)
                #print("Product Title:", product_title)
            else:
                print("Product block not found.")
            prices_block = elem.select(".snippets-product-block__price")
            for block in prices_block:
                highlighted_price = block.select_one(".snippets-product-block__price_highlight")
                original_price = block.select_one(".snippets-product-block__price_disabled")
                final_price = highlighted_price.text.   strip() if highlighted_price else "N/A"
                old_price = original_price.text.strip() if original_price else "N/A"
                #print("Final Price:", final_price)
                #print("Old Price:", old_price)
            #Add product details to list
            product_list.append({
                'product_url': product_url,
                'variant_sku': variant_sku,
                'product_title': product_title,
                'final_price': final_price,
                'old_price': old_price
            })
        return product_list
    else:
        print(f"Class '{class_name}' not found.")


def scrape_img(url, class_to_find):
    print('Starting...')
    try:
        product_list = debug_class_search(url, class_to_find)

        # Extract product link (example: products/premax-super-natural-hairline...)
        product_count = 0
        for product in product_list[:2]:
            print('-'*50)
            product_url = f"https://shop.luvmehair.com{product['product_url']}"
            print(product_url)

            # Construct a unique product ID
            product_id = str(uuid.uuid4())
            print(f"Scraping product: {product['product_title']} at {product_url}")

            # Find image URLs using the provided CSS selector
            #image_urls = []

            # Visit product detail page using the session
            soup = cook_soup(product_url)
            found_product = soup.select('a.show-gallery')
            print('*'*50)
            #print('Found product images:', found_product)

            for img_index, img in enumerate(found_product[:20]):  # Limit to 20 images
                img_url = 'https:' + img['href']
                print(img_url)
                if img_url:
                    # Download and save the image
                    saved_image_path = download_image(img_url, product_id, img_index)
                    if saved_image_path:
                        return saved_image_path

        return None
    except Exception as e:
        print(f"Error scraping image: {e}")
        return None


url = 'https://shop.luvmehair.com/collections/best-sellers'
class_to_find = 'list-item'
scrape_img(url, class_to_find)