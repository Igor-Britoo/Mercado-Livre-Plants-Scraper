from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import parse
import time
import json
import csv

# Constants
BASE_URL = 'https://lista.mercadolivre.com.br'

# Install and setup ChromeDriver
CHROME_DRIVER = ChromeDriverManager().install()

# Chrome options
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_experimental_option('detach', True)  # Keep the browser open after the script finishes
OPTIONS.add_argument('window-size=1200,800')
# OPTIONS.add_argument("--headless=new")  # Uncomment for headless mode
OPTIONS.add_argument("--disable-extensions")
OPTIONS.add_argument("--no-sandbox")
OPTIONS.add_argument("--disable-dev-shm-usage")
OPTIONS.add_argument("--disable-gpu")
OPTIONS.add_argument("--disable-browser-side-navigation")

def scrape_product_info_from_page_in_stack_layout(browser, wait, product_element, product_xpath):
  """
  Extract product information from a product element in stack layout.
      
  Parameters:
    browser (webdriver.Chrome): The browser instance.
    wait (WebDriverWait): WebDriverWait instance for explicit waits.
    product_element (WebElement): The product element to extract info from.
    product_xpath (str): The XPath of the product element.
      
  Returns:
    tuple: Product title and price elements.
  """
  # Check for label
  product_label_element = product_element.find_elements(By.CLASS_NAME, 'ui-search-item__highlight-label')
  has_label = len(product_label_element) > 0

  title_div_index = 2 if has_label else 1

  # Check for variations
  search_variations_element = product_element.find_elements(By.CLASS_NAME, 'ui-search-item__pds-options')
  has_search_variations = len(search_variations_element) > 0

  # Extract the product price element according to whether the product has variants.
  if has_search_variations:
    product_price_xpath = f'{product_xpath}/div/div/div[2]/div[{title_div_index+1}]/div[1]/div/div[1]/div/span'
    wait.until(EC.presence_of_element_located((By.XPATH, product_price_xpath)))
    product_price_element = browser.find_element(By.XPATH, product_price_xpath)
  else:
    product_price_element = product_element.find_element(By.CLASS_NAME, 'ui-search-price__part--medium')
      
  # Extract product title element
  product_title_xpath = f'{product_xpath}/div/div/div[2]/div[{title_div_index}]/a'
  wait.until(EC.presence_of_element_located((By.XPATH, product_title_xpath)))
  product_title_element = browser.find_element(By.XPATH, product_title_xpath)

  return product_title_element, product_price_element

def scrape_product_info_from_page_in_grid_layout(browser, wait, product_element, product_xpath):
  """
  Extract product information from a product element in grid layout.
      
  Parameters:
    browser (webdriver.Chrome): The browser instance.
    wait (WebDriverWait): WebDriverWait instance for explicit waits.
    product_element (WebElement): The product element to extract info from.
    product_xpath (str): The XPath of the product element.
      
  Returns:
    tuple: Product title and price elements.
  """
  # Check for label
  product_label_xpath = f'{product_xpath}/div/div/div[2]/div/div[1]/div/label'
  product_label_element = browser.find_elements(By.XPATH, product_label_xpath)
  has_label = len(product_label_element) > 0

  # Check for variations
  search_variations_xpath = f'{product_xpath}/div/div/div[2]/div/div[1]/div[@class="ui-search-variations-pill"]'
  search_variations_element = browser.find_elements(By.XPATH, search_variations_xpath)
  has_search_variations = len(search_variations_element) > 0

  title_div_index = 2 if has_label or has_search_variations else 1

  # Extract product title
  product_title_xpath = f'{product_xpath}/div/div/div[2]/div/div[{title_div_index}]/a'
  wait.until(EC.presence_of_element_located((By.XPATH, product_title_xpath)))
  product_title_element = browser.find_element(By.XPATH, product_title_xpath)
      
  # Extract product price
  product_price_xpath = f'{product_xpath}/div/div/div[2]/div/div[{title_div_index+1}]/div/div/div/span[1]'
  wait.until(EC.presence_of_element_located((By.XPATH, product_price_xpath)))
  product_price_element = browser.find_element(By.XPATH, product_price_xpath)

  return product_title_element, product_price_element

def scrape_products_by_query(query):
  """
  Scrape products from Mercado Livre based on a search query.
      
  Parameters:
    query (str): Search query string
      
  Returns:
    list: List of dictionaries containing product information
  """
  products = []

  # Initialize the browser
  browser = webdriver.Chrome(options=OPTIONS, service=ChromeService(CHROME_DRIVER))
  browser.get(f'{BASE_URL}/{parse.quote(query)}')  # Open URL with encoded query
  wait = WebDriverWait(browser, 20)

  # Wait for page to load
  time.sleep(7)

  # XPath for the 'Next' page button
  next_page_element_xpath = '//a[@class="andes-pagination__link" and @title="Seguinte"]'

  # Check the page layout
  products_list_element_xpath = '//ol[@class="ui-search-layout ui-search-layout--stack shops__layout"]'
  products_list_element = browser.find_elements(By.XPATH, products_list_element_xpath)
  is_stack_layout = len(products_list_element) > 0

  while True:
    # Get product elements
    products_elements_xpath = f'{products_list_element_xpath}/li[@class="ui-search-layout__item shops__layout-item ui-search-layout__stack"]' if is_stack_layout else '//ol[@class="ui-search-layout ui-search-layout--grid"]/li[@class="ui-search-layout__item"]'
    products_elements = browser.find_elements(By.XPATH, products_elements_xpath)

    for product_index in range(len(products_elements)):
      product_xpath = f'{products_elements_xpath}[{product_index+1}]'

      # Scroll into product
      browser.execute_script("arguments[0].scrollIntoView();", products_elements[product_index])
      
      if is_stack_layout:
        product_title_element, product_price_element = scrape_product_info_from_page_in_stack_layout(browser=browser, wait=wait, product_element=products_elements[product_index], product_xpath=product_xpath)
      else:
        product_title_element, product_price_element = scrape_product_info_from_page_in_grid_layout(browser=browser, wait=wait, product_element=products_elements[product_index], product_xpath=product_xpath)

      # Get title, permalink, and price
      product_title = product_title_element.get_attribute('innerText')
      product_permalink = product_title_element.get_attribute('href')
      product_price = float(product_price_element.get_attribute('innerText').replace('\n', '').replace('R$', '').replace(',', '.'))

      products.append({
        'title': product_title,
        'permalink': product_permalink,
        'price': product_price,
      })

    # Check for the 'Next' page button
    next_page_element = browser.find_elements(By.XPATH, next_page_element_xpath)
    next_page_exists = len(next_page_element) > 0
    if next_page_exists:
      try: 
        browser.execute_script("arguments[0].scrollIntoView();", next_page_element[0])
        next_page_element[0].click()
        time.sleep(7)
      except Exception:
        break
    else:
      break

  browser.close()
  return products

def scrape_and_save_products_for_plants(plant_list):
  """
  Scrape products for a list of plants (by scientific and popular names) from Mercado Livre
  and save the results to CSV and JSON files.

  Parameters:
    plant_list (list): A list of tuples with plant scientific and popular names.

  Returns:
    None
  """
  for plant in plant_list:
    # Scrape products by scientific and popular names for each plant
    products = {
      'by_scientific_name': scrape_products_by_query(query=plant[0]),
      'by_popular_name': scrape_products_by_query(query=plant[1]),
    }

    # Save the fetched products to a JSON file named after the plant's popular name
    with open(f'../outputs/json/{plant[1]}.json', 'w') as json_file:
      json_file.write(json.dumps(products, indent=2))

    # Save the fetched products to a CSV file named after the plant's popular name
    with open(f'../outputs/csv/{plant[1]}.csv', mode='w', newline='') as csv_file:
      writer = csv.writer(csv_file)
      
      # Write the header
      writer.writerow(['TITLE', 'PERMALINK', 'PRICE', 'BY_POPULAR_NAME'])
      
      # Write the products queried by popular name
      for product in products['by_popular_name']:
        writer.writerow([
          product.get('title', ''),
          product.get('permalink', ''),
          product.get('price', ''),
          True
        ])

      # Write the products queried by scientific name
      for product in products['by_scientific_name']:
        writer.writerow([
          product.get('title', ''),
          product.get('permalink', ''),
          product.get('price', ''),
          False
        ])

    print(plant, '(OK)')
