from playwright.sync_api import sync_playwright
from dataclasses import asdict, dataclass,  field
import pandas as pd
import argparse
import time


    
def get_shop_urls_and_scroll(page):
    shop_urls = set()
    flag = True
    attempt = 0
    max_attempts = 3
    while True:
            # Scroll the feed container
            try:
                print("Scrolling")
                shop_elements = page.locator('//*[@class="hfpxzc"]').all()
                print(len(shop_elements))
                page.hover('//*[@role="feed"]')
                page.mouse.wheel(0, 30000)
                shop_elements[0].click()
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
                            try:
                                rating_element = page.locator('//div[contains(@class, "LBgpqf")]//div[contains(@class, "skqShb")]//div[contains(@class, "fontBodyMedium dmRWX")]//div[contains(@class, "F7nice")]//span/span[@aria-hidden="true"]')
                                # Locate the total reviews element using XPath
                                reviews_element = page.locator('//div[contains(@class, "LBgpqf")]//div[contains(@class, "skqShb")]//div[contains(@class, "fontBodyMedium dmRWX")]//div[contains(@class, "F7nice")]//span/span[contains(text(), "(")]')
                                # Fetch the rating text
                                rating_texts = rating_element.all_text_contents()
                                if rating_texts:
                                    rating = rating_texts[0]
                                else:
                                    rating = "N/A"
                                reviews_texts = reviews_element.all_text_contents()
                                if reviews_texts:
                                    # Extract just the number part from the text, e.g., "(6,212)" -> "6212"
                                    reviews = reviews_texts[0].strip("()").replace(",", "").strip()
                                    print("Total Reviews:", reviews, "Rating:", rating)
                                else:
                                    reviews = "N/A"
                                    print("Total reviews not found.")
                            except Exception as e:
                                print("Error:", e)
                                rating = "N/A"
                                reviews = "N/A"

                            try:
    # Locate the timing element using XPath
                                timings_element = page.locator('//div[contains(@class, "OqCZI fontBodyMedium WVXvdc")]//div[@aria-label]')
                                
                                # Fetch the text content of the timings
                                timings_texts = timings_element.all_text_contents()
                                if timings_texts:
                                    # Clean and parse the timing string
                                    timing_str = timings_texts[0].replace("Suggest new hours", "")
                                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                                    timing_dict = {}
                                    
                                    for day in days:
                                        try:
                                            # Find the start index of the day
                                            start_idx = timing_str.find(day)
                                            if start_idx != -1:
                                                # Find the start of the next day or end of string
                                                next_day_idx = len(timing_str)
                                                for next_day in days:
                                                    next_start = timing_str.find(next_day, start_idx + len(day))
                                                    if next_start != -1 and next_start < next_day_idx:
                                                        next_day_idx = next_start
                                                
                                                # Extract and clean the timing for the current day
                                                time_slot = timing_str[start_idx + len(day):next_day_idx].strip()
                                                # Clean up the time slot string by removing special characters
                                                time_slot = time_slot.encode('ascii', 'ignore').decode().strip()
                                                timing_dict[day] = time_slot if time_slot else "Closed"
                                            else:
                                                timing_dict[day] = "N/A"
                                        except Exception as e:
                                            timing_dict[day] = "N/A"
                                            print(f"Error parsing {day}: {str(e)}")
                                    
                                    timings = timing_dict
                                    print("Timings:", timings)
                                else:
                                    timings = {day: "N/A" for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
                                    print("Timings not found.")
                            except Exception as e:
                                print("Error:", e)
                                timings = {day: "N/A" for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}


                            # print(name, phone_number_text, address_text, website_text, rating)
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
        search_keyword_location = "hair salon in singapore"
        location = "singapore"
        output_file = "shop_list.csv"

        main(search_keyword_location, location, output_file)
