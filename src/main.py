import json
import threading
from fetch_products import fetch_products_for_plants
from datetime import datetime

N_THREADS = 3

# Get the start time for measuring execution time
start_time = datetime.now()

# Load categories from JSON file
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

# Create threads to fetch products for each slice of plants
threads = []
for i in range(N_THREADS):
  thread = threading.Thread(target=fetch_products_for_plants, args=(categories, plant_slices[i]))
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