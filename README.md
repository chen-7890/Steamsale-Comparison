# Steamsale-Comparison

This is a Python based webscraper that fetches from the Steam "Specials" page then compares them against the historial all time low using CheapShark API. The data is then exported to a CSV file in the same directory.

##### Prerequisties

This script was made in Python 3.13. 

```pip install requests beautifulsoup4 tqdm```

##### Usage

1. Run Script
```python steamsale.py```

2. Enter page number: When prompted, enter the starting and ending page numbers you wish to scrape from the Specials page
  - _Each page usually contains 50 items_

3. There is a two second delay between calls to respect rate limits

4. Once finished, a summary will appear in the terminal and the full data will be available in ```steam_deals.csv```

###### CSV Output Format

| Column | Description |
| ------ | ----------- |
| AppID | Unique Steam Game Identifier |
| Title | Name of Game |
| Original Price | Base MSRP price |
| Current Price | Current Sale price |
| All-Time Low | Lowest price recorded on CheapShark |
| Status | Shows either 'Historic Low" or "% above low" | 
| Days since Low | Days elapsed since the historical low date |
| Date of Low | The date the lowest price was recorded |

