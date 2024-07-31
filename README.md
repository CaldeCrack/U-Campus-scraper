# U-Campus scraper

Tool to <ins>**scrap**</ins> the **departments** and their **courses** at FCFM from
 <ins>**U-Campus**</ins> in a specific year and semester into a [JSON](https://www.json.org/json-en.html) file.

## Usage

- Install the dependencies:

```sh
pip install -r requirements.txt
```

- Run the script in interactive mode:

```sh
python ucampus_scraper.py
```

- Or directly from the terminal:

```sh
python ucampus_scraper.py <year> <semester>
```

Year should be between **1996** and the actual year.

Semester can take four different values them being:
- 0 (Annual)
- 1 (Autumn)
- 2 (Spring)
- 3 (Summer)
