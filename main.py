from playwright.sync_api import sync_playwright
from dataclasses import asdict, dataclass,  field
import pandas as pd
import argparse



@dataclass
class ShopInformation:
    name: str = field(default="")
    address: str = field(default="")
    website: str = field(default="")
    phonenumber: str = field(default="")
    shopLink: str = field(default="")
    bookingLink: str = field(default="")
    timing: str = field(default="")

@dataclass
class ShopList:
    shopList: list[ShopInformation] = field(default_factory=list)
    def dataframe(self):
        return pd.json_normalize([asdict(shop) for shop in self.shopList], sep="")

    def save_to_excel(self, filename: str):
        self.dataframe().to_excel(filename, index=False)
    
    def save_to_csv(self, filename: str):
        self.dataframe().to_csv(filename, index=False)
        
    def save_to_json(self, filename: str):
        self.dataframe().to_json(filename, orient="records")

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape shop information from Google Maps")
    parser.add_argument("-s","--search", type=str, help="The search keywords to use for the search")
    parser.add_argument("-l","--location", type=str, help="The location to search for the shop")
    parser.add_argument("-o","--output", type=str, help="The output file name")
    args = parser.parse_args()


    if not args.search or not args.location or not args.output:
        parser.error("All arguments are required")
    else:
        search_keywords = args.search
        location = args.location
        output_file = args.output
        
        search_keyword_location = f'{search_keywords}  {location}'

        print(f"Searching for {search_keyword_location}")

