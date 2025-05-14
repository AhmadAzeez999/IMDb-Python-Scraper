import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import os
import time
import random

# Downloading necessary NLTK data
nltk.download('stopwords')  # For NLTK’s built-in list of common “stop words” (like, “and”, “the”, “is”) for filtering out these words
nltk.download('punkt')  # Fetches the pre-trained Punkt tokenizer models, which are used for splitting raw text into sentences and words (tokenization basically).

class IMDbScraper:
    def __init__(self):
        self.baseUrl = "https://www.imdb.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Creating an output directory for word clouds (if it doesn't exist already of course)
        os.makedirs("wordclouds", exist_ok=True)

    def getTopMoviesByGenre(self, genre, count=50):
        # To get all the top movies for a specific genre
        url = f"{self.baseUrl}/search/title/?genres={genre}&sort=user_rating,desc&title_type=feature&num_votes=25000,&view=advanced"
        print(f"Fetching top {count} movies for genre: {genre}")

        movies = []
        page = 1
        while len(movies) < count:
            pageUrl = f"{url}&start={(page-1)*50+1}" if page > 1 else url
            response = requests.get(pageUrl, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Updated selector for movie items
            movieItems = soup.select('.lister-item-content h3 a')

            if not movieItems:
                print(f"No movies found on page {page}. Trying alternative selector...")
                movieItems = soup.select('.titleColumn a')  # Alternative selector

            if not movieItems:
                print(f"Still no movies found. Breaking loop.")
                break

            for movie in movieItems:
                if len(movies) >= count:
                    break

                title = movie.text.strip()
                movieUrl = self.baseUrl + movie['href'].split('?')[0]  # Remove query parameters
                movies.append({'title': title, 'url': movieUrl})

            # Check if there's a next page
            nextPage = soup.select_one('.lister-page-next')
            if not nextPage:
                break

            page += 1
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))

        print(f"Found {len(movies)} movies for genre: {genre}")
        return movies[:count]

    def getTopMovies(self, count=50):
        # Getting overall top movies regardless of genre
        url = f"{self.baseUrl}/chart/moviemeter/?ref_=nv_mv_mpm"  # Changed to moviemeter chart
        print(f"Fetching top {count} movies overall")

        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        movies = []

        # Trying different selectors for movie items
        # This took a WHILE to get right, so in case IMDB decides to change their structure again
        # I'll try a bunch of selectors to see what works :)
        selectors = [
            '.titleColumn a',
            '.cli-children a',
            'h3.ipc-title__text a',
            '.lister-item-header a'
        ]

        for selector in selectors:
            movieItems = soup.select(selector)
            if movieItems:
                print(f"Found movies using selector: {selector}")
                break

        if not movieItems:
            # Just fallback to most popular movies chart
            url = f"{self.baseUrl}/chart/popular/"
            print(f"No movies found. Trying fallback URL: {url}")
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            movieItems = soup.select('.titleColumn a')

        for movie in movieItems[:count]:
            title = movie.text.strip()
            href = movie.get('href', '')
            if href:
                # Handling both absolute and relative URLs
                if href.startswith('/title/'):
                    movieUrl = self.baseUrl + href.split('?')[0]
                else:
                    movieUrl = href.split('?')[0]  # Removing query parameters
                movies.append({'title': title, 'url': movieUrl})

        print(f"Found {len(movies)} top movies overall")
        return movies[:count]

    def getMovieDetails(self, movie):
        # Getting the plot summary and genre for a movie
        print(f"Fetching details for: {movie['title']}")

        try:
            response = requests.get(movie['url'], headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get plot summary - try different selectors
            plotSummary = ""
            plotSelectors = [
                '[data-testid="plot"] span.sc-466bb6c-0',
                '[data-testid="plot-xl"]',
                '.summary_text',
                '[data-testid="storyline-plot-summary"]',
                '.plot_summary .text-muted'
            ]

            for selector in plotSelectors:
                plotSection = soup.select_one(selector)
                if plotSection:
                    plotSummary = plotSection.text.strip()
                    break

            # Getting genres (trying different selectors again, just in case)
            genres = []
            genreSelectors = [
                'div.ipc-chip-list a.ipc-chip',
                'div.subtext a[href*="genres"]',
                '.genre a',
                '[data-testid="genres"] a',
                '[data-testid="genres"] span.ipc-metadata-list-item__list-content-item'
            ]

            for selector in genreSelectors:
                genreLinks = soup.select(selector)
                if genreLinks:
                    for genre in genreLinks:
                        genres.append(genre.text.strip())
                    break

            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))

            return {
                'title': movie['title'],
                'plot': plotSummary,
                'genres': genres
            }
        except Exception as e:
            print(f"Error fetching details for {movie['title']}: {str(e)}")
            return {
                'title': movie['title'],
                'plot': "",
                'genres': []
            }

    def processText(self, text):
        # Process text for word cloud by removing stopwords and cleaning
        if not text or text.isspace():
            return []

        # Converting to lowercase and removing special characters
        text = re.sub(r'[^\w\s]', '', text.lower())

        # Tokenize and remove stopwords (might not be perfect, but it works...I think)
        try:
            stopWords = set(stopwords.words('english'))
            customStopwords = {
                'movie', 'film', 'story', 'character', 'one', 'two', 'three', 
                'may', 'also', 'would', 'could', 'must', 'however', 'new',
                'man', 'woman', 'find', 'gets', 'goes', 'going', 'go', 'get',
                'way', 'make', 'made', 'making', 'takes', 'take', 'taking',
                'young', 'old', 'even', 'will', 'become', 'becomes', 'becoming',
                'day', 'night', 'year', 'month'
            }
            stopWords.update(customStopwords)

            # Use simple tokenization as fallback if nltk fails
            try:
                words = nltk.word_tokenize(text)
            except LookupError:
                print("NLTK tokenizer not available, using simple tokenization")
                words = text.split()

            return [word for word in words if word.isalpha() and word not in stopWords and len(word) > 2]
        except Exception as e:
            print(f"Error processing text: {str(e)}")
            # Simple fallback
            return [w for w in text.split() if len(w) > 2]

    def generateGenreWordcloud(self, movies):
        # Generate a word cloud for the most common genres
        allGenres = []
        for movie in movies:
            details = self.getMovieDetails(movie)
            allGenres.extend(details['genres'])

        # Count genres
        genreCounts = Counter(allGenres)

        if not genreCounts:
            print("No genres found to create word cloud")
            return {}

        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                              max_words=100, colormap='viridis').generate_from_frequencies(genreCounts)

        # Save and display the word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('wordclouds/top_genres_wordcloud.png')
        plt.close()

        return genreCounts

    def generatePlotWordcloud(self, genre=None):
        # Generate a word cloud for plot summaries of movies in a genre or overall top movies
        if genre:
            movies = self.getTopMoviesByGenre(genre)
            filename = f'wordclouds/{genre}_plot_wordcloud.png'
            title = f"Plot Keywords for Top {len(movies)} {genre.capitalize()} Movies"
        else:
            movies = self.getTopMovies()
            filename = 'wordclouds/overall_plot_wordcloud.png'
            title = f"Plot Keywords for Top {len(movies)} Movies Overall"

        if not movies:
            print("No movies found to analyze")
            return {}

        allPlots = ""
        for movie in movies:
            details = self.getMovieDetails(movie)
            allPlots += " " + details['plot']

        # Process text
        words = self.processText(allPlots)

        if not words:
            print("No words found to create word cloud")
            return {}

        wordFreq = Counter(words)

        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                              max_words=100, colormap='viridis').generate_from_frequencies(wordFreq)

        # Save and display the word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

        return wordFreq