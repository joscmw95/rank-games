# rank-games
Ranking games using data from [Google Trends](https://www.google.com/trends/)

Get Game List
-------------
To obtain a snapshot of the current trending games, we adopt the lists of games that are streamed on one of the most renowned live-streaming video platform – [Twitch.tv](http://twitch.tv/). A Python script (getTwitchGameList.py) is written to parse the data given by the Twitch API at the endpoint https://api.twitch.tv/kraken/games/top which returns a list of games objects sorted by number of current viewers on Twitch, most popular first; in JSON format.

Get Suggested Keywords
----------------------
To obtain data from Google Trends, we used an unofficial Python API pytrends. There are several parameters that are used in the trend search:
* q – the search query string
* cat – the category of the trend search
* geo – the geographical area of the trend search
* date – the time range of the trend search

To ensure that the query string used is accurate, we need to know the advanced keywords that are suggested by Google Trends as shown in the figure below:

![Keywords suggestion in Google Trends dashboard](/images/advancedkeywords.png?raw=true)

It turns out that each of these keywords are encoded in a unique format. For example, the keyword for the Pokémon GO Mobile Game is ‘/g/11bw4tm1l9’. To find out this keyword, we used the method in pytrends that returns a list of additional suggested keywords that can be used to refine a trend search. A sample output of the method when searching for ‘Pokemon Go’ is shown below:

```
{
    'default': {
        'topics': [
            {
                'mid': '/g/11bw4tm119',
                'title': 'Pokémon GO',
                'type': 'Mobile game'
            },
            {
            'mid': '/m/05xwg',
            'title': 'Pokémon',
            'type': 'Brand'
            }
        ]
    }
}
```

The Python script (getSuggestedWords.py) reads the csv file previously generated and looks for the keywords of each game title. To determine which keyword in the list to be selected, we choose the one with the least Levenshtein distance with the game title. As seen from the JSON structure, the refined keyword is the value of the key ‘mid’.

Get Games Trend Data
--------------------
There are a few factors to consider when scraping data from Google Trends. First of all, each trend search is limited to 5 keywords as in the web application. Multiple calls to the method is needed to obtain the trend data of the 1,200+ video game titles that we have. Furthermore, the data from each trend search is normalized according to the total search volume of the queried keywords. Essentially, trend searches with different keywords have different weights, a value of 60 in one game title is different from a same value for another.

![Trend data of League of Legends](/images/dataleagueoflegends.png?raw=true "Trend data of League of Legends")
![Trend data of Pokémon GO and League of Legends](/images/dataleaguepokemon.png?raw=true "Trend data of Pokémon GO and League of Legends")

Here, the value 100 is normalized to only 2 when compared with Pokémon GO. To ensure that the weights are sufficiently uniform across all trend searches, we only search 1 game title from our list and pair it with a ‘benchmark’ keyword per trend search. This gives the relative value of the game title to the benchmark keyword. In practice, we paired each game title to the keyword ‘book’ which is seen to have a steady search volume throughout all times.

For this task, we wrote the Python script getTrendData.py. The API method in pytrends returns the historical trend data in the form of a pandas (a Python Data Analysis Library) data frame. The mean of the values is calculated and used to rank the games.

Results
-------
The final output is further checked for abnormalities and stored in a csv file. The data is analyzed using R. The figure below shows the R plot of the top 10 games in the ranking generated using ggplot:

![Top 10 Games from May 2016 – August 2016](/results/top10games.png?raw=true "Top 10 Games from May 2016 – August 2016")

Credits
-------
* This project uses the pesudo API for Google Trends provided by [pytrends](https://github.com/GeneralMills/pytrends)
