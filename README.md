# Mercado Livre Plants Scraper

The `Mercado-Livre-Plants-Scraper` repository contains Python scripts designed to scrape listings of plants available for sale on  Mercado Livre. This project focuses exclusively on fetching listings related to plants, identified by their popular and scientific names, within the categories listed in the `categories.json` file. The scraped data is organized by plant name and category and saved in JSON files within the outputs directory for further analysis or processing.

## Features

- Scrapes plant listings from MercadoLivre API based on popular and scientific names.
- Fetches listings within specified categories listed in the `categories.json` file.
- Organizes fetched listings by plant name and category.
- Saves the fetched listings in JSON files for further analysis or processing.

## Installation

1. Clone the repository:
  ```sh
  git clone https://github.com/Igor-Britoo/Mercado-Livre-Plants-Scraper.git
  ```
2. Navigate to the project directory:
  ```sh
  cd Mercado-Livre-Plants-Scraper
  ```
3. Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

## Usage

1. Ensure you have your categories and plants data in JSON format within the `data` directory. You can customize these files as needed.
2. Modify the `N_THREADS` variable in `main.py` to specify the number of threads you want to use for parallelized fetching.
3. Run the main script:
  ```sh
  python main.py
  ```

## File Structure

```
Mercado-Livre-Plants-Scraper/
│
├── data/
│ ├── categories.json
│ └── plants.json
│
├── outputs/
│ ├── babosa.json
│ ├── camomila.json
│ └── ... (other plant JSON files)
│
├── src/
│ ├── fetch_products.py
│ └── main.py
│
├── LICENSE
├── README.md
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.