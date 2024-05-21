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
class testing():
    url = 'https://www.amazon.in/Apple-iPhone-14-128GB-Midnight/dp/B0BDHX8Z63/ref=sr_1_1?crid=2GBG91LF250IZ&dib=eyJ2IjoiMSJ9.eFa-TvbcC_zjCq_5PD2KO7esruSMHK5ZeG6Ar_e-Gy6XZo4gdfr6NOw3hpFrfQby-BqsnOscO8IpueNWVDzLPQbT6e8S7YFvG4UNPYWIKjOfFGkR7pSuXo5cb6rnFB1YGBP1sgBIUphuUBm1FNB20k42ckXyZh1w0qjc0bNHmkKfMu7MB8qMBBsxDetVUX_EzajW2DJCRi47lWY5Z6cUvxTLx3VhWt59z0J_7TZCnm0.0nt9C--hN0U8HlWQwuXPrAOfbO4Dytm5-fRqvNfNWUY&dib_tag=se&keywords=iphone&qid=1709747161&sprefix=iphone%2Caps%2C347&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1'
    driver=webdriver.Chrome()

    def init(self):
        """init : use for maximize the window and implement implicity wait"""
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
    def handle_captcha(self):
        link=self.driver.find_element(By.XPATH,'//div[@class="a-row a-text-center"]//img').get_attribute('src')
        captcha=AmazonCaptcha.fromlink(link)
        captcha_val=AmazonCaptcha.solve(captcha)
        input_field=self.driver.find_element(By.ID,'captchacharacters').send_keys(captcha_val)
        button=self.driver.find_element(By.CLASS_NAME,"a-button-text")
        button.click()
        
    def scrape_reviews_page(self):
        self.driver.get(self.url)
        self.handle_captcha()
        sleep(10)
        analyzer = SentimentIntensityAnalyzer()
        istrue=True
        while(istrue):
            full_review=self.driver.find_element(By.XPATH,'.//*[@id="reviews-medley-footer"]/div[2]/a').click()
            istrue=False
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

                review = [name,stars,title,date,description, sentiment]
                reviews.append(review)
            try:
                next_page=self.driver.find_element(By.XPATH,'.//*[@class="a-last"]')
                next_page.click()
                sleep(10)
            except:
                break
            
        df=pd.DataFrame(reviews, columns=['Name', 'Stars', 'Title', 'Date', 'Description', 'Sentiment'])
        print(df)
        df.to_csv('review.csv',index=False)
obj=testing()
obj.scrape_reviews_page()