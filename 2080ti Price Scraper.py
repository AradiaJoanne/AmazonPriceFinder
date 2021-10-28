from os import name
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd

# Declare some vars
s = HTMLSession()
item_listings = []

search_term = '2080Ti'
url = f'https://www.amazon.co.uk/s?k={search_term}&ref=nb_sb_noss_2'

def get_html(url):
    r = s.get(url)
    # YOU MUST RENDER THE FULL HTML OR YOU WILL GET FLAGGED AS A BOT
    r.html.render(sleep = 1)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    return soup

def parse_html(soup):
    # Grab the whole section of products from the page
    products = soup.find_all('div', {'data-component-type':'s-search-result'})
    # Exctract the needed info from each listing
    for item in products:
        # Check if the item even has a price at all
        price_check = item.find_all('span',{'class':'a-offscreen'})
        if price_check != []:

            title = item.find('a', {'class':'a-link-normal a-text-normal'}).text.strip()
            short_title = item.find('a', {'class':'a-link-normal a-text-normal'}).text.strip()[:30]
            link = item.find('a', {'class':'a-link-normal a-text-normal'})['href']
            #Check if the price is standard or sale
            try:
                new_price = float(item.find_all('span', {'class':'a-offscreen'})[0].text.replace('£','').replace(',','').strip())
                prev_price = float(item.find_all('span', {'class':'a-offscreen'})[1].text.replace('£','').replace(',','').strip())
            except:
                prev_price = float(item.find('span', {'class':'a-offscreen'}).text.replace('£','').replace(',','').strip())
            
            # Store in a dictionary so it can be a df later
            item_listing = {
                'title':title, 
                'short_title':short_title,
                'current_price':new_price,
                'previous_price':prev_price,
                'link':link
            }
    # add the info from each listing to a list
        item_listings.append(item_listing)
    return item_listings

# Check to see if the next page button exists, if so return it, else return nothing
def pagination(soup):
    pages = soup.find('ul',{'class':'a-pagination'})
    if not pages.find('li',{'class':'a-disabled a-last'}):
        url = 'https://www.amazon.co.uk' + str(pages.find('li',{'class':'a-last'}).find('a')['href'])
        return url
    else:
        return


# While Pagination IS NOT at the end of the pages
while True:
    soup = get_html(url)
    parse_html(soup)
    url = pagination(soup)
    if not url:
        break
    else:
        print(url)
        print(len(item_listings))

df = pd.DataFrame(item_listings)

# Calculate some price differences for later use 
df['percent_discount'] = 100 - ((df.current_price/df.previous_price)*100)
df['price_difference'] = (df.previous_price - df.current_price)

df.to_csv(f'Amazon_{search_term}_Prices.csv', index = False)
print('Data Saved to CSV')