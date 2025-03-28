import requests
from bs4 import BeautifulSoup
import csv
import uuid
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By


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



# Function to scrape product data and save it into CSV
def scrape_and_save_to_csv(url, class_to_find="list-item", csv_file_path='products.csv', max_products=20):

    # Open the CSV file in write mode (create if doesn't exist)
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header row to CSV
        writer.writerow(['product_link', 'variant_sku', 'product_title', 'final_price', 'old_price', 'image_urls']) 

        product_list = debug_class_search(url, class_to_find)

        # Extract product link (example: products/premax-super-natural-hairline...)
        product_count = 0
        for product in product_list:
            print('-'*50)
            product_url = f"https://shop.luvmehair.com{product['product_url']}"
            print(product_url)

            # Construct a unique product ID
            product_id = str(uuid.uuid4())
            print(f"Scraping product: {product['product_title']} at {product_url}")

            # Find image URLs using the provided CSS selector
            image_urls = []

            # Visit product detail page using the session
            soup = cook_soup(product_url)
            found_product = soup.select('a.show-gallery')

            for img_index, img in enumerate(found_product[:20]):  # Limit to 20 images
                img_url = "https:" + img['href']
                if img_url:
                    # Download and save the image
                    saved_image_path = download_image(img_url, product_id, img_index)
                    if saved_image_path:
                        image_urls.append(saved_image_path) 
            # Write product details to CSV
            writer.writerow([
                product_url, 
                product['variant_sku'],
                product['product_title'],
                float(product['final_price'].strip('$').replace(',', '')),  # Price as float
                float(product['old_price'].strip('$').replace(',', '')),
                ';'.join(image_urls)  # List of image paths (relative)
                ])  
            product_count += 1
            print(f"Product '{product['product_title']}' added to CSV with {len(image_urls)} images.")  


# Example usage
scrape_and_save_to_csv('https://shop.luvmehair.com/collections/best-sellers', class_to_find="list-item", csv_file_path='products.csv', max_products=20)
