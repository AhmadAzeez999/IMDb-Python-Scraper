# Author: Ahmad Azeez
# This program scrapes top movies on IMDB to  check what the most popular genres and plots are.

from iMDbScraper import IMDbScraper

def main():
    scraper = IMDbScraper()
    
    genre = input("Enter a genre to analyze (e.g., action, drama, comedy) or press Enter for overall analysis: ")
    
    if genre:
        # Genre-specific analysis
        print(f"\nAnalyzing plot summaries for top movies in genre: {genre}")
        plot_keywords = scraper.generatePlotWordcloud(genre)
        if plot_keywords:
            print(f"\nTop 20 plot keywords for {genre} movies:")
            for word, count in plot_keywords.most_common(20):
                print(f"{word}: {count}")
            print(f"\nPlot word cloud saved to wordclouds/{genre}_plot_wordcloud.png")
    
    # Overall top movies analysis
    print("\nAnalyzing overall top movies...")
    plot_keywords = scraper.generatePlotWordcloud()
    if plot_keywords:
        print("\nTop 20 plot keywords for overall top movies:")
        for word, count in plot_keywords.most_common(20):
            print(f"{word}: {count}")
    
    # Generate genre word cloud from top movies
    print("\nAnalyzing genres of top movies...")
    top_movies = scraper.getTopMovies()
    if top_movies:
        genre_counts = scraper.generateGenreWordcloud(top_movies)
        if genre_counts:
            print("\nMost common genres in top movies:")
            for genre, count in genre_counts.most_common():
                print(f"{genre}: {count}")
            print("\nGenre word cloud saved to wordclouds/top_genres_wordcloud.png")

if __name__ == "__main__":
    main()