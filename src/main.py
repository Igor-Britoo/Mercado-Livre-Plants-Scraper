import json
import threading
from datetime import datetime

N_THREADS = 3   # Number of threads
IS_FETCHING = True  # If True its going to fetch the data from the API.
                    # If False its going to scrape the data from the marketplace website.

# Choose the appropriate import based on the IS_FETCHING flag
if IS_FETCHING:
  from fetch_products import fetch_and_save_products_for_plants
else:
  from scrape_products import scrape_and_save_products_for_plants

# Get the start time for measuring execution time
start_time = datetime.now()

# Load categories from JSON file if IS_FETCHING is True
if IS_FETCHING:
  with open('../data/categories.json') as categories_file:
    categories = (json.load(categories_file))['categories']

# Load plants from JSON file
with open('../data/plants.json') as plants_file:
  plants = list((json.load(plants_file).items()))

# Separate the plants list into N_THREADS slices
slice_size = round(len(plants) / N_THREADS)
plant_slices = []
pointer = 0
for index in range(N_THREADS):
  if (pointer + slice_size >= len(plants) or index + 1 == N_THREADS):
    slice = plants[pointer:]
    plant_slices.append(slice)
  else:
    slice = plants[pointer: pointer + slice_size]
    plant_slices.append(slice)
  pointer += slice_size

# Create threads to fetch or scrape products for each slice of plants
threads = []
for i in range(N_THREADS):
  if IS_FETCHING:
    thread = threading.Thread(target=fetch_and_save_products_for_plants, args=(categories, plant_slices[i]))
  else:
    thread = threading.Thread(target=scrape_and_save_products_for_plants, args=(plant_slices[i], ))
  threads.append(thread)
  thread.start()

# Wait for all threads to complete
for thread in threads:
  thread.join()

# Display execution summary
print('\n\n================================================================')
finish_time = datetime.now()
start_time_string = start_time.strftime('%d/%m/%Y %H:%M')
finish_time_string = finish_time.strftime('%d/%m/%Y %H:%M')
print('The execution started at ' + start_time_string)
print('The execution finished at ' + finish_time_string)
print('================================================================\n')