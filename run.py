from tkinter import Tk, Label, Entry, Button
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
class Testing():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        
    def handle_captcha(self):
        link = self.driver.find_element(By.XPATH,'//div[@class="a-row a-text-center"]//img').get_attribute('src')
        captcha = AmazonCaptcha.fromlink(link)
        captcha_val = AmazonCaptcha.solve(captcha)
        input_field = self.driver.find_element(By.ID,'captchacharacters').send_keys(captcha_val)
        button = self.driver.find_element(By.CLASS_NAME,"a-button-text")
        button.click()
        
    def scrape_reviews_page(self, url):
        self.driver.get(url)
        self.handle_captcha()
        sleep(10)
        analyzer = SentimentIntensityAnalyzer()
        is_true = True
        while(is_true):
            full_review = self.driver.find_element(By.XPATH,'.//*[@id="reviews-medley-footer"]/div[2]/a').click()
            is_true = False
        reviews = []
        for i in range(10):  
            boxes = WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, './/*[@data-hook="review"]')))
            for box in boxes:
                try:
                    name = box.find_element(By.XPATH, './/*[@class="a-profile-name"]').text.strip()
                except:
                    name = 'N/A'

                try:
                    stars_element = box.find_element(By.XPATH, './/span[@class="a-icon-alt"]')
                    stars = stars_element.get_attribute('innerHTML').split(' ')[0]
                except:
                    stars='N/A'

                try:
                    title = box.find_element(By.XPATH, './/*[@data-hook="review-title"]//span[2]').text.strip()
                except:
                    title = 'N/A'

                try:
                    date_format = "Reviewed in India on %d %B %Y"
                    datetime_str = box.find_element(By.XPATH, './/*[@data-hook="review-date"]').text
                    date = datetime.strptime(datetime_str, date_format).date()
                except:
                    date = 'N/A'

                try:
                    description = box.find_element(By.XPATH, './/*[@data-hook="review-body"]').text.strip()
                    sentiment_score = analyzer.polarity_scores(description)
                    if sentiment_score['compound'] >= 0.05:
                        sentiment = 'Positive'
                    elif sentiment_score['compound'] <= -0.05:
                        sentiment = 'Negative'
                    else:
                        sentiment = 'Neutral'
                except:
                    description = 'N/A'
                    sentiment = 'N/A'

                review = [name, stars, title, date, description, sentiment]
                reviews.append(review)
            try:
                next_page = self.driver.find_element(By.XPATH,'.//*[@class="a-last"]')
                next_page.click()
                sleep(10)
            except:
                break
            
        df = pd.DataFrame(reviews, columns=['Name', 'Stars', 'Title', 'Date', 'Description', 'Sentiment'])
        print(df)
        df.to_csv('ass1.csv',index=False)

def start_scraping():
    url = url_entry.get()
    obj = Testing()
    obj.scrape_reviews_page(url)

if __name__ == "__main__":
    root = Tk()
    root.title("Amazon Review Scraper")
    root.geometry("500x500")

    label = Label(root, text="Enter Amazon Product URL:")
    label.pack(pady=10)

    url_entry = Entry(root, width=60)
    url_entry.pack(pady=5)

    submit_button = Button(root, text="Submit", command=start_scraping)
    submit_button.pack(pady=5)

    root.mainloop()
