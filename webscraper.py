from playwright.sync_api import sync_playwright
import pandas as pd
from geopy.geocoders import Nominatim
import time
import urllib.parse

def get_state_from_address(address):
    geolocator = Nominatim(user_agent="hotel_locator")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            # Reverse geocode to get detailed information
            reverse_location = geolocator.reverse((location.latitude, location.longitude), timeout=10)
            address_details = reverse_location.raw['address']
            return address_details.get('state', 'Unknown')
    except Exception as e:
        print(f"Error: {e}")
        return 'Unknown'
    return 'Unknown'

def scrape_hotels(state):
    with sync_playwright() as p:
        checkin_date = '2024-12-01'
        checkout_date = '2024-12-31'
        state_query = urllib.parse.quote(f'{state}, United States')
        page_url = f'https://www.booking.com/searchresults.html?ss={state_query}&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaFCIAQGYATG4ARfIAQzYAQHoAQH4AQKIAgGoAgO4AsLhkLUGwAIB0gIkZmJiMDQ0MTEtZmJlMC00ZWY4LWI1MzItZmViOGMwM2I5MjRi2AIF4AIB&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6dd697a16a6801c7&ac_meta=GhA2ZGQ2OTdhMTZhNjgwMWM3IAAoATICZW46CnVuaXRlZCBzdGFAAEoAUAA%3D&checkin=2024-12-01&checkout=2024-12-31&group_adults=1&no_rooms=1&group_children=0'

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)

        hotels = page.locator('//div[@data-testid="property-card"]').all()
        print(f'There are {len(hotels)} hotels in {state}.')

        hotels_list = []
        for i, hotel in enumerate(hotels):
            hotel_dict = {}
            try:
                hotel_dict['hotel'] = hotel.locator('//div[@data-testid="title"]').inner_text(timeout=20000)
                hotel_dict['price'] = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text(timeout=20000)
                hotel_dict['avg review'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[1]').inner_text(timeout=20000)
                hotel_dict['reviews count'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[2]').inner_text(timeout=20000).split()[0]
                hotel_dict['address'] = hotel.locator('//span[@data-testid="address"]').inner_text(timeout=20000)
            except Exception as e:
                print(f"Error extracting data for hotel {i} in {state}: {e}")
                continue

            hotels_list.append(hotel_dict)
        
        browser.close()
        
        return hotels_list

def main():
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", 
              "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", 
              "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", 
              "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
              "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
              "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

    all_hotels = []
    for state in states:
        hotels = scrape_hotels(state)
        all_hotels.extend(hotels)
        time.sleep(1)  # Sleep for a second between requests to avoid being rate-limited

    df = pd.DataFrame(all_hotels)
    df['state'] = df['address'].apply(get_state_from_address)

    df.to_excel('hotels_list.xlsx', index=False) 
    df.to_csv('hotels_list.csv', index=False) 

if __name__ == '__main__':
    main()
