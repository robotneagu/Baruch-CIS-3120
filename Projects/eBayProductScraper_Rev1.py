#Created by Robert Neagu.
#Please note that this code should only be used for educational purposes.
#import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#Ask user to search for a product.
link = input('Enter product to search.')
#Ask user how many pages to look through.
pages = int(input('Enter how many pages to search'))

#Sets URL based on user input. Start at page 1.
url = f'https://www.ebay.com/sch/i.html?_nkw={link}&_pgn=1'

#Create lists to store scraped data
titles = []
prices = []
condition = []
seller = []
seller_reviews = []
seller_rating = []

for i in range(pages):

    #Set status code of page to a variable
    page = requests.get(url)

    #Store html content into soup variable if connection is successful, code 200.
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')

        #Create main variable that has the div class outside all elements below
        div_tags = soup.find_all('div', class_ = 's-item__wrapper clearfix')

        #For loop to look through various elements inside div_tags. Cycles for every product in the webpage.
        for div_tag in div_tags:
            #Find product name (and model). Name was inside a div element with specific class.
            div_title = div_tag.find('div', class_ = 's-item__title').get_text().strip()
            #Remove New Listing, then store name inside the titles list
            div_title = div_title.replace('New Listing', '')
            #Store product name inside titles list.
            titles.append(div_title)
            #Find price of product and get its cost.
            div_price = div_tag.find('div', class_ = 's-item__detail s-item__detail--primary')
            #Remove $ from prices and store price in prices list.
            prices.append(div_price.get_text().strip('$'))
            #Find condition of product stored inside a span element.
            span_condition = div_tag.find('span', class_ = 'SECONDARY_INFO')
            #Store product condition inside condition list.
            condition.append(span_condition.get_text().strip())
            #Find general seller information
            span_seller = div_tag.find('span', class_ = 's-item__seller-info')
            if type(span_seller) == type(None):
                continue
            else:
                seller_info = span_seller.get_text()
                seller_info = seller_info.replace(')', '').replace('(', '').replace(',', '').replace('%', '')
                seller_info = seller_info.split(' ')
                #Store seller info inside seller tag
                seller.append(seller_info[0])
                seller_reviews.append(int(seller_info[1]))
                seller_rating.append(float(seller_info[2]))
    
        #Move on to second page
        url = f'https://www.ebay.com/sch/i.html?_nkw={link}&_pgn={i+1}'
  
#Remove unnecessary data.
titles.remove('Shop on eBay')
del(prices[0])
 
#Adjust prices to allow calculations. Done by transforming into floats. Stores in a new list, prices_adj.
prices_adj = []
for i in prices:
    i = i.replace(',', '')
    try:
        i = float(i)
        prices_adj.append(i)
    except:
        continue
 
#Products dict formation and dataframe result inspired from: https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
#Create dictionary using arrays to fill in missing info, if any.
products = dict(Product = np.array(titles), Price = np.array(prices_adj), Condition = np.array(condition), Seller = np.array(seller), SellerReviewCount = np.array(seller_reviews), SellerRating = np.array(seller_rating))
 
#Create dataframe through dictionary comprehension. Inspired from https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
#State the key and value parameters. Series(values) allows NaN to be in place for missing data.
#For loop takes keys and values from products dictionary listed as tuples. 
#Dataframe is then built with NaN values
df = pd.DataFrame({key:pd.Series(value) for key, value in products.items()})
#Remove any product row with a NaN name.
df = df[df.Product.notnull()]
#Remove any product with NaN price.
df = df[df.Price.notnull()]
print(df.describe())
pd.set_option('display.max_rows', 1000)
print(df)