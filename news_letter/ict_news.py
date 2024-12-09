from function_list.news_scraping_func import fetch_news_date
from function_list.basic_options import mongo_setting,selenium_setting,init_browser
from selenium.webdriver.common.by import By
from newspaper import Article
import time
from selenium.webdriver.common.keys import Keys

def process_links(link_elements, collection, browser,news_topic,crawling_count):
    results = collection.find({},{'_id':0,'news_link':1})
    link_list = [i['news_link'] for i in results]
    original_window = browser.current_window_handle

    for link_element in link_elements:
        
        link = link_element.get_attribute('href')
        time.sleep(1)  # 대기 시간
        if link not in link_list:
            try:
                if 'https://zdnet.co.kr/error/' in link or 'cuts.top' in link  or 'dailysecu' in link or 'datanet' in link or 'search.naver' in link or 'kmib.co.kr' in link or 'cctvnews' in link:
                    pass  # 해당 링크는 무시            
                else:
                    article = Article(link, language='ko')
                    article.download()
                    article.parse()
                    title, date, content = article.title, article.publish_date, article.text
                    if title is None or content is None or 'news.naver' in link or 'newsis.com' in link :
                        link_element.click()
                        browser.switch_to.window(browser.window_handles[-1])
                        try:
                            news_dict = fetch_news_date(link, browser)
                            news_dict['news_topic']=news_topic
                            news_dict['news_link']=link
                        except:
                            pass
                        browser.close()
                        browser.switch_to.window(browser.window_handles[-1])

                    elif date is None:
                        link_element.click()
                        browser.switch_to.window(browser.window_handles[-1])
                        try:
                            date = fetch_news_date(link, browser)
                        except:
                            pass
                        browser.close()
                        browser.switch_to.window(browser.window_handles[-1])
                        news_dict = {
                            'news_title': title,
                            'news_content': content,
                            'news_date': date,
                            'news_link': link,
                            'news_topic':news_topic,
                            'news_reference':'ict_news'
                        }
                    collection.insert_one(news_dict)
                    crawling_count+=1
            except:
                pass
        for handle in browser.window_handles:
            if handle != original_window:
                browser.switch_to.window(handle)
                browser.close()
        browser.switch_to.window(original_window)
    return crawling_count
 
def ict_news():
    crawling_count = 0
    collection = mongo_setting('news_scraping','news_list')
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)
    pass
    browser.get("https://ictnewsclipping.stibee.com/")    
    first_content = browser.find_element(by=By.CSS_SELECTOR,value='#__next > div > div > div:nth-child(1) > a')
    first_content.click()
    time.sleep(1)
    for j in range(5):
        time.sleep(1)
        content_list_first = browser.find_elements(by=By.CSS_SELECTOR,value='div.stb-left-cell > div.stb-text-box > table > tbody > tr > td')
        content_title = browser.find_element(by=By.CSS_SELECTOR,value='#__next > div:nth-child(1) > div > div > div.fOAJCs').text
        if '[ICT 뉴스' in content_title:
            for i in content_list_first:
                try:
                    news_topic = i.find_element(by=By.CSS_SELECTOR,value='div > span').text
                except:
                    news_topic = i.find_element(by=By.CSS_SELECTOR,value='h2 > span').text
                contents_list = i.find_elements(by=By.CSS_SELECTOR,value='a')
                crawling_count = process_links(contents_list, collection, browser,news_topic,crawling_count)
        else:
            j = j - 1
        body = browser.find_element(by=By.TAG_NAME,value='body')
        body.send_keys(Keys.END)
        time.sleep(1)
        try:
            alarm_btn = browser.find_element(by=By.CSS_SELECTOR,value='button.no-subscription')
            alarm_btn.click()
        except:
            pass
        time.sleep(2)
        before_btn = browser.find_element(by=By.CSS_SELECTOR,value='div.prev')
        before_btn.click()
    browser.quit()
    print('ict news crawling finish')
    print('crawling count : ',crawling_count)

# 크롤링 함수 실행
# ict_news()