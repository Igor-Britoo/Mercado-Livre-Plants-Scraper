import requests
import json
import csv

from urllib.parse import quote

# Base URL for the Mercado Livre search API
REQUEST_URL = 'https://api.mercadolibre.com/sites/MLB/search'

def fetch_products_by_query(query):
  """
  Fetches products from the Mercado Livre API based on a search query.
      
  Parameters:
    query (str): The search term.
    
  Returns:
    list: A list of dictionaries with product details.
  """
      
  # Encode the query to be URL-safe
  query_encoded = quote(query)
  products = []
  offset = 0

  try:
    # Initial API request
    response = requests.get(f'{REQUEST_URL}?q={query_encoded}').json()

    # Continue fetching products while offset is within the total number of products
    while (offset <= (response['paging']['total'] - 50)) and (offset <= 950):
      offset += 50
      response = requests.get(f'{REQUEST_URL}?q={query_encoded}&offset={offset}').json()

      # Extract relevant product details and add them to the products list
      for product in response['results']:
        products.append({
          'id': product['id'],
          'title': product['title'],
          'permalink': product['permalink'],
          'price': product['price'],
        })

  except requests.RequestException as e:
    # Handle any request-related exceptions
    print(f'An error occurred while fetching products: {e}')
  except Exception as e:
    # Handle any other unexpected exceptions
    print(f'An unexpected error occurred: {e}')
    print(query, offset)

  return products

def fetch_products_by_query_and_category(query, category_id):
  """
  Fetches products from the Mercado Livre API based on a search query and category ID.
      
  Parameters:
    query (str): The search term.
    category_id (str): The category ID.
    
  Returns:
    list: A list of dictionaries with product details.
  """

  # Encode the query to be URL-safe
  query_encoded = quote(query)
  products = []
  offset = 0

  try:
    # Initial API request
    response = requests.get(f'{REQUEST_URL}?q={query_encoded}&category={category_id}').json()

    # Continue fetching products while offset is within the total number of products
    while (offset <= (response['paging']['total'] - 50)) and (offset <= 950):
      # Update offset and request the next batch of products
      offset += 50
      response = requests.get(f'{REQUEST_URL}?q={query_encoded}&category={category_id}&offset={offset}').json()

      # Extract relevant product details and add them to the products list
      for product in response['results']:
        products.append({
          'id': product['id'],
          'title': product['title'],
          'permalink': product['permalink'],
          'price': product['price'],
        })

  except requests.RequestException as e:
    # Handle any request-related exceptions
    print(f'An error occurred while fetching products: {e}')
  except Exception as e:
    # Handle any other unexpected exceptions
    print(f'An unexpected error occurred: {e}')
    print(query, category_id, offset)

  return products

def fetch_products_across_categories(query, categories_list):
  """
  Fetches products for a query across multiple categories from the Mercado Livre API.
  Also fetches products for a query without any category.
      
  Parameters:
    query (str): The search term.
    categories_list (list): A list of category dictionaries.
    
  Returns:
    dict: A dictionary with category names as keys and lists of products as values.
  """
      
  products_by_categories = {}
  for category in categories_list:
    # Fetch products for each category and store them in the dictionary
    products_by_categories[category['name']] = fetch_products_by_query_and_category(query, category['id'])

  # Fetch products without any category and store them under 'Sem Categoria'
  products_by_categories['Sem Categoria'] = fetch_products_by_query(query)

  #print(query, '(OK)')
  return products_by_categories

def fetch_and_save_products_for_plants(categories_list, plant_list):
  """
  Fetches products for a list of plants (by scientific and popular names) from the Mercado Livre API
  and saves the results to CSV and JSON files.

  Parameters:
    categories_list (list): A list of category dictionaries.
    plant_list (list): A list of tuples with plant scientific and popular names.

  Returns:
    None
  """
      
  for plant in plant_list:
    # Fetch products by scientific and popular names for each plant
    products = {
      'by_scientific_name': fetch_products_across_categories(query=plant[0], categories_list=categories_list),
      'by_popular_name': fetch_products_across_categories(query=plant[1], categories_list=categories_list),
    }

    # Save the fetched products to a JSON file named after the plant's popular name
    with open(f'../outputs/json/{plant[1]}.json', 'w') as json_file:
      json_file.write(json.dumps(products, indent=2))
    
    # Save the fetched products to a CSV file named after the plant's popular name
    with open(f'../outputs/csv/{plant[1]}.csv', mode='w', newline='') as csv_file:
      writer = csv.writer(csv_file)
      
      # Write the header
      writer.writerow(['ID', 'TITLE', 'PERMALINK', 'PRICE', 'CATEGORY', 'BY_POPULAR_NAME'])
      
      # Write the products queried by popular name
      for category in products['by_popular_name']:
        for product in products['by_popular_name'][category]:
          writer.writerow([
            product.get('id', ''),
            product.get('title', ''),
            product.get('permalink', ''),
            product.get('price', ''),
            category,
            True
          ])

      # Write the products queried by scientific name
      for category in products['by_scientific_name']:
        for product in products['by_scientific_name'][category]:
          writer.writerow([
            product.get('id', ''),
            product.get('title', ''),
            product.get('permalink', ''),
            product.get('price', ''),
            category,
            False
          ])

    print(plant, '(OK)')