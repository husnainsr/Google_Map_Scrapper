from playwright.sync_api import sync_playwright
from dataclasses import asdict, dataclass,  field
import pandas as pd
import argparse
import time


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

    
def get_shop_urls_and_scroll(page):
    shop_urls = set()
    flag = True
    attempt = 0
    max_attempts = 3
    while True:
            # Scroll the feed container
            try:
                page.hover('//*[@role="feed"]')
                page.mouse.wheel(0, 30000)
                shop_elements = page.locator('//*[@class="hfpxzc"]').all()
                for shop_element in shop_elements:
                    try:
                        url = shop_element.get_attribute("href")
                        if url and url not in shop_urls:
                            shop_urls.add(url)
                            shop_element.click()
                            page.wait_for_timeout(2000)
                            try:
                                name  = page.locator('//*[@class="DUwDvf lfPIob"]').inner_text()
                            except:
                                name = "N/A"
                            try:
                                phone_number = page.locator('//*[@class="CsEnBe" and contains(@aria-label, "Phone")]')
                                phone_number_text = phone_number.get_attribute("aria-label").replace("Phone: ", "")
                            except:
                                phone_number_text = "N/A"
                            try:
                                address = page.locator('//*[@class="CsEnBe" and contains(@aria-label, "Address")]')
                                address_text = address.get_attribute("aria-label").replace("Address: ", "")
                            except:
                                address_text = "N/A"
                            try:
                                website = page.locator('//*[@class="CsEnBe" and contains(@aria-label, "Website")]')
                                website_text = website.get_attribute("aria-label").replace("Website: ", "")
                            except:
                                website_text = "N/A"
                            print(name, phone_number_text, address_text, website_text)

                        else:
                            continue
                    except Exception as e:
                        print(f"Error clicking on shop element: {str(e)}")

                page.wait_for_timeout(1000)
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    print(f"Max attempts reached. Exiting loop.")
                    break
                print(f"Error scrolling feed container: {str(e)}")



            
                
    
            
    return list(shop_urls)


def main(search_keyword_location: str, location: str, output_file: str):
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                try:
                    page.goto("https://www.google.com/maps", timeout=10000)
                except Exception as e:
                    print(f"Error accessing Google Maps: {str(e)}")
                    return

                try:
                    page.wait_for_timeout(10000)
                    search_box = page.locator('//*[@id="searchboxinput"]')
                    search_box.fill(search_keyword_location)
                    page.keyboard.press("Enter")
                except Exception as e:
                    print(f"Error performing search: {str(e)}")
                    return

                all_shop_urls = get_shop_urls_and_scroll(page)

                # shop_list = ShopList()
                # for i, shop_element in enumerate(all_shop_urls[:10]):
                #     try:
                #         shop_element.click()
                #         page.wait_for_timeout(10000)

                #         name_xpath='//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1'
                #         address_xpath='//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]'
                #         website_xpath='//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[6]/a/div'
                #         phonenumber_xpath='//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[7]/button/div'
                #         timing_xpath='//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[4]/div[2]'

                #         shop_info = ShopInformation()

                #         try:
                #             shop_info.name = page.locator(name_xpath).inner_text()
                #         except:
                #             shop_info.name = "Name not found"
                            
                #         try:
                #             shop_info.address = page.locator(address_xpath).inner_text()
                #         except:
                #             shop_info.address = "Address not found"
                            
                #         try:
                #             shop_info.website = page.locator(website_xpath).inner_text()
                #         except:
                #             shop_info.website = "Website not found"
                            
                #         try:
                #             shop_info.phonenumber = page.locator(phonenumber_xpath).inner_text()
                #         except:
                #             shop_info.phonenumber = "Phone number not found"
                            
                #         try:
                #             shop_info.timing = page.locator(timing_xpath).inner_text()
                #         except:
                #             shop_info.timing = "Timing not found"

                #         shop_list.shopList.append(shop_info)
                #         print(f"Successfully processed shop {i+1}/10")
                        
                #     except Exception as e:
                #         print(f"Error processing shop {i+1}: {str(e)}")
                #         continue

                # try:
                #     shop_list.save_to_csv(output_file)
                #     print(f"Successfully saved data to {output_file}")
                # except Exception as e:
                #     print(f"Error saving to CSV: {str(e)}")
                #     return
                    
                # time.sleep(10)
                
            except Exception as e:
                print(f"Browser error: {str(e)}")
            finally:
                try:
                    browser.close()
                except:
                    print("Error closing browser")
                    
    except Exception as e:
        print(f"Playwright initialization error: {str(e)}")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Scrape shop information from Google Maps")
    # parser.add_argument("-s","--search", type=str, help="The search keywords to use for the search")
    # parser.add_argument("-l","--location", type=str, help="The location to search for the shop")
    # parser.add_argument("-o","--output", type=str, help="The output file name")
    # args = parser.parse_args()


    # if not args.search or not args.location or not args.output:
    #     parser.error("All arguments are required")
    # else:
    #     search_keywords = args.search
    #     location = args.location
    #     output_file = args.output
        
    #     search_keyword_location = f'{search_keywords}  {location}'

    #     print(f"Searching for {search_keyword_location}")

        search_keyword_location = "hair salon in singapore"
        location = "singapore"
        output_file = "shop_list.csv"

        main(search_keyword_location, location, output_file)
