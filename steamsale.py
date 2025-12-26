import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from datetime import datetime
from tqdm import tqdm

# ----
USE_MOCK_DATA = False
# ----

def get_clean_price(price_string):
    """Removes currency symnols and converts to float."""
    if not price_string or price_string == "N/A":
        return None
    try:
        # Removes currency symbols and handles Steam's formatting
        return float(price_string.replace('$', '').replace('€', '').replace('£', '').strip())
    except ValueError:
        return None

def get_historical_low(app_id):
    if app_id == "N/A":
        return "N/A", "N/A"
    
    if USE_MOCK_DATA:
        return f"{round(random.uniform(1.0,30.0), 2)}", "2023-12-25"
    
    api_url = f"https://www.cheapshark.com/api/1.0/games?steamAppID={app_id}"
    for attempt in range(3):
        try:
            resp = requests.get(api_url)
            
            if resp.status_code == 429:
                print("Rate Limited, waiting 10 seconds")
                time.sleep(10)
                continue
            
            data = resp.json()
            if not data: 
                return "N/A", "N/A"
        
            game_id = data[0]['gameID']
        
            detail_url = f"https://www.cheapshark.com/api/1.0/games?id={game_id}"
            detail_data = requests.get(detail_url).json()
            price = detail_data['cheapestPriceEver']['price']
            
            timestamp = detail_data['cheapestPriceEver']['date']
            readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            
            return price, readable_date
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for ID {app_id}: {e}")
            time.sleep(2)
    return "Error", "Error"
        
def get_steam_specials():
    url = "https://store.steampowered.com/search/?specials=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # User enters how much pages to search
    while True:
        try:
            start_page = int(input("Enter starting page number (eg. 1, 2...) "))
            end_page = int(input("Enter ending page number: "))
            # Ensuring value is acceptable      
            if start_page > 0 and end_page >= start_page:
                break
            else:
                print("Invalid Range, ensure start is more than 0 and end is more than start.")
        except ValueError:
            print("Please enter a whole number (1, 2, 3 ,4....)")
    
    seen_ids = set()
    today = datetime.now()  
    
    # Summary initialization
    total_scraped = 0
    hist_count = 0
    best_deals = []
    
    # tqdm help
    total_pages = (end_page - start_page) + 1
    total_expected_games = total_pages * 50
      
    with open('steam_deals.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['AppID', 'Title', 'Original Price', 'Current Price', 'All-Time Low', 'Status', 'Days Since Low', 'Date of Low'])
        
        with tqdm(total=total_expected_games, desc="Total Progress", unit="game") as pbar:
            
            for page_num in range(start_page, end_page + 1):
                start_index = (page_num - 1) * 50
                url = f"https://store.steampowered.com/search/?specials=1&start={start_index}"
                print(f"\n---Scraping page {page_num} (starting at item {start_index}) ---")
                
                soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
                games = soup.find_all('a', class_='search_result_row')
                
                if not games:
                    pbar.write(f"No more games found on page {page_num}. Ending early.")
                    break
            
                for game in games:
                    app_id = game.get('data-ds-appid', "N/A")
                    
                    # Making sure all entries are unique
                    if app_id in seen_ids:
                        pbar.update(1)
                        continue
                    seen_ids.add(app_id)
                    
                    # Getting title of game
                    title_el = game.find('span', class_='title')
                    title = title_el.text if title_el else "Unknown"
                    
                    # Scrap the current sale price and original price on steam
                    price_div = game.find('div', class_='discount_final_price')
                    current_price = price_div.get_text(strip=True) if price_div else "N/A"
                    price_div = game.find('div', class_='discount_original_price')
                    original_price = price_div.get_text(strip=True) if price_div else "N/A"
                    
                    low_price, low_date = get_historical_low(app_id)

                    # Cleaning the price from $
                    curr_val = get_clean_price(current_price)
                    hist_val = get_clean_price(low_price)
                    
                    # Calculate the price difference between current and lowest
                    if curr_val is not None and hist_val is not None:
                        diff = round(curr_val - hist_val, 2)
                        if diff <= 0:
                            status = "Historic Low"
                            hist_count += 1
                            best_deals.append(title)
                        else:
                            perc = round((diff/hist_val) * 100, 1)
                            status = f"{perc}% above low"
                    else:
                        status = "N/A"
                        
                    # Calculate the days since the lowest price 
                    try:                 
                        low_dt_obj = datetime.strptime(low_date, '%Y-%m-%d')
                        days_since = (today - low_dt_obj).days
                    except:
                        days_since = "N/A"
                        
                    writer.writerow([app_id, title, original_price, current_price, low_price, status, days_since, low_date])
                    total_scraped +=1
                    
                    pbar.set_postfix({"Current": title[:20]}) 
                    pbar.update(1)
                    
                    time.sleep(1 if USE_MOCK_DATA else 2)
    
    # Print summary
    print("Scraping Success")
    print("\n" + "="*30)
    print("     SCRAPING SUMMARY")
    print("="*30)
    print(f" ▶ Total Scraped: {total_scraped}")
    print(f" ▶ Historical Lows: {hist_count}")
    if best_deals:
        print("\nTop Deals: ")
        for deal in best_deals[:5]:
            print(f" - {deal}")
    print("="*30)
    print("Results saved to 'steam_deals.csv'")
        
if __name__ == "__main__":
    get_steam_specials()