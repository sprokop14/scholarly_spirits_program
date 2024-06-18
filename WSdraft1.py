import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import csv


def get_all_auction_urls():
    # Define the URL you want to scrape
    url = "https://www.scotchwhiskyauctions.com/auctions/"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> elements with class "auction"
        elements = soup.find_all('a', class_='auction')

        # Create an empty list to store modified href values
        modified_href_values = []

        # Iterate through the elements and extrach "href" values
        for element in elements:
            href_value = element.get('href')

             # Remove the substring "auctions/"
            if href_value and href_value.startswith("auctions/"):
                modified_href_value = href_value[len("auctions/"):]
                modified_href_values.append(modified_href_value)

        return modified_href_values

    else:
        print(f"Failed to retrieve data from URL: {url}")

        return modified_href_values
    

# Function to retrieve auction items
def get_all_lot_urls(auction_urls):
    base_url = "https://www.scotchwhiskyauctions.com/auctions/"
    auction_items = []

    for auction_url in auction_urls:


        i = 1
        while(True):
            try:
                # Construct the full URL
                item_url = base_url + auction_url + "?page=" + str(i)

                # Send an HTTP GET request to the item URL
                response = requests.get(item_url)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')

                    #Find and extract the desired information (ex., item name)
                    elements = soup.find_all('a', class_='lot')

                    for element in elements:
                        href_value = element.get('href')
                        if href_value and href_value.startswith("auctions/"+auction_url):
                            # modified_href_value = href_value[len("auctions/"+auction_url):]
                            auction_items.append(href_value)
                            print("Successfully captured elements: " + href_value)
                else:
                    print(f"Failed to retrieve data from URL: {item_url}")

                sleep(2)
                i += 1
                #if i == 2:
                    #break
            except:
                print("BROKE WHILE LOOP")
                break
    return auction_items

def extract_item_details(item_url):
    response = requests.get(item_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example: Extracting the item NAMES and PRICES
        # Adjust the class names and tags from HTML Inspect accoridng to needs

        json_record = {}

        whiskey_name = soup.find('h1').text
        json_record["whiskey_name"] = whiskey_name

        featured_div = soup.find('div', class_='featured')
        if featured_div:
            text = featured_div.get_text()
            # Assuming the format is consistent and 'ended' is always present
            # Splitting the text and getting the part after 'ended'
            ended_date = text.split(", ended ")[-1]
            date_obj = datetime.strptime(ended_date, '%B %d, %Y')
            iso_format_date = date_obj.strftime('%Y-%m-%d')
            json_record["ended_date"] = iso_format_date
        else:
            json_record["ended_date"] = None

        lot_number_raw = soup.find('p', class_='lotno').text
        lot_number = lot_number_raw[len("Lot number: "):]
        json_record["lot_number"] = lot_number

        winning_bid_raw = soup.find('p', class_='bidinfo won').text
        winning_bid = winning_bid_raw.split("Lot number: £")
        json_record["winning_bid"] = winning_bid
       

        
        bid_currency = 'GBP'
        json_record["bid_currency"] = bid_currency

        desc = soup.find('div', class_='descr').contents
        filtered_desc = [element for element in desc if element != '\n']

        desc_clean = filtered_desc[0].text.replace("<p>", "").replace("</p>", "")
        json_record["description"] = desc_clean

        # print(json_record)

        for item in filtered_desc[1:]:
            item_cleaned = item.text.replace("<p>", "").replace("</p>", "")

            if item_cleaned.startswith("Bottled: "):
                bottled_text = item_cleaned[len("Bottled: "):]
                json_record["bottled_at"] = bottled_text
            else: json_record ["bottled_at"] = None

            if item_cleaned.startswith("Distilled: "):
                distilled_text = item_cleaned[len("Distilled: "):]
                json_record["distilled_at"] = distilled_text
            else: json_record["distilled_at"] = None

            if item_cleaned.startswith("Age: "):
                age_text = item_cleaned[len("Age: "):]
                json_record["age"] = age_text
            else: json_record["age"] = None

            if item_cleaned.startswith("Cask Type: "):
                cask_type_text = item_cleaned[len("Cask Type: "):]
                json_record["cask_type"] = cask_type_text
            else: json_record["cask_type"] = None

            if item_cleaned.startswith("Cask Number: "):
                cask_number_text = item_cleaned[len("Cask Number: "):]
                json_record["cask_number"] = cask_number_text
            else: json_record["cask_number"] = None
        
        return json_record
        print(json_record)
    else: 
        print(f"Failed to retrieve data from URL: {item_url}")
        return None

# Example usage: 
if __name__ == "__main__":
    auction_urls = get_all_auction_urls()
    auction_items = get_all_lot_urls(auction_urls[1:2])

    extracted_data = []

    # Print the retrieved auction items
    for item in auction_items:
        data = extract_item_details("https://www.scotchwhiskyauctions.com/"+item)
        if data:
            extracted_data.append(data)

    # Write the extracted data to a CSV file
    filename = 'winningbiddata5.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = extracted_data[0].keys() if extracted_data else []
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in extracted_data:
            writer.writerow(item)
        
 