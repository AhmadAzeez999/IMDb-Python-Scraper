[![Steam Data Explorer](https://media.licdn.com/dms/image/v2/D5622AQFVTp4dOFxYPg/feedshare-shrink_2048_1536/B56ZbQzN75H4Ao-/0/1747259809992?e=1750291200&v=beta&t=nc0OCnGeG8bnfBUQL2VN-jsZyIe4VVYQdaG6PTdMeow)](https://github.com/AhmadAzeez999/IMDb-Python-Scraper/)

# IMDb Top Movie Plots: Word Cloud Generator

This Python project scrapes the **Top 50 (or Top 25) movies on IMDb** (or from a specified genre), extracts their **plot summaries**, and generates a **word cloud** to visualize the most common themes and keywords in today's popular films.

---

## Features

* Scrapes plot summaries from IMDb’s Top 50 movies
* Supports genre-specific analysis (e.g., Action, Comedy, Horror)
* Generates a word cloud showing the most frequently used words in plots
* Cleans and processes text using NLTK
* Visualizes data using `WordCloud` and `matplotlib`
* Also generates the most common genres (as a bonus)

---

## Requirements

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Key dependencies:

* `requests`
* `beautifulsoup4`
* `nltk`
* `wordcloud`
* `matplotlib`

---

## How to Use

To run the script and analyze IMDb's top 50 movies:

```bash
python topMoviesScraper.py
```

To analyze the top 50 movies in a specific genre (e.g., Action, Comedy):

```bash
python topMoviesScraper.py --genre Action
```

> Make sure to use genre names that IMDb recognizes (e.g., `Drama`, `Sci-Fi`, `Thriller`).

---

## Author

Created by [Ahmad Azeez](https://github.com/AhmadAzeez999)

---

## Acknowledgments

* IMDb for the publicly accessible movie data
* Python community for the powerful open-source libraries :)
