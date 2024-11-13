
from selenium.webdriver.common.by import By          # - 정보 획득
import pandas as pd 
import time
from datetime import datetime, timedelta

def marketinsight(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#contents > article > div > div.cont-free > div.article-head > div.date-info > span:nth-child(1) > span').text
    news_date = pd.to_datetime(news_date)
    return news_date

def lawtimes(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#__next > div:nth-child(2) > div.css-8atqhb.e1s9yunr0 > div > div > div.css-1rop7pp.ehx2lg80 > div.css-vcchsy.e179ozeo0 > div.css-1vaapo.e179ozeo5 > div:nth-child(3)').text
    news_date = pd.to_datetime(news_date)
    return news_date

def dailynk(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#post-297217 > div.td-post-header > header > div > span > time').text.split(' ')[:2]
    news_date = pd.to_datetime(' '.join(news_date))
    return news_date

def kgnews(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div.respon_wrap.active > div > div.contents.column-wrap > div.con_left > div > div.line_wrap.no_bb > div > div:nth-child(1) > div > div.arv_001_01 > div.art_top > ul.art_info > li:nth-child(2)').text.replace('등록 ','')
    news_date = pd.to_datetime(news_date)
    return news_date

def dailymedi(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#viewHead > div.view_head > div.info > span:nth-child(1)').text
    news_date = pd.to_datetime(news_date)
    return news_date

def kyeongin(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='div > span.news-date > span.news-date').text.replace('입력 ','')
    news_date = pd.to_datetime(news_date)
    return news_date

def newstomato(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#main-top > div.rn_container.mt50px.mb30px > div.rn_sti_case > div.rn_sdate').text.split(' ')[:2]
    news_date = pd.to_datetime(' '.join(news_date))
    return news_date

def esquirekorea(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='span.time').text
    news_date = pd.to_datetime(news_date)
    return news_date

def medipana(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.inr-c > div.flex_article > div.lft_article > div.bbs_view > div.tit > p > span.r').text
    news_date = pd.to_datetime(news_date)
    return news_date

def newsprime(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div > div > div > div.section_h12 > div > div.c011_arv > div.viewsubject > div > div > div').text.split('|')[-1]
    news_date = pd.to_datetime(news_date)
    return news_date

def nocut(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#pnlViewTop > div.h_info > ul > li:nth-child(2)').text
    news_date = pd.to_datetime(news_date)
    return news_date

def newspim(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#send-time').text
    news_date = pd.to_datetime(news_date, format='%Y년%m월%d일 %H:%M')
    return news_date

def kotra(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#pdfArea > dl > dt > div.txtInfo > ul > li.date').text
    news_date = pd.to_datetime(news_date)
    return news_date

def mtn(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#__next > main > div > section > div > div > div > article > header > div.css-1b8sprk > time').text
    news_date = pd.to_datetime(news_date)
    return news_date

def skyedaily(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#n_view2 > div > div.articlearea > div.articletitle > div > font').text.replace('입력 ','')
    news_date = pd.to_datetime(news_date)
    return news_date

def donga(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > main > div > div.main-content.col-lg-8 > div.article > article > header > div.row.py-2 > div.col-sm-4.text-right > time').text
    news_date = pd.to_datetime(news_date)
    return news_date

def dnews(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div > div.view_contents.innerNews > div.newsCont > div.dateFont > em').text.replace('기사입력 ','')
    news_date = pd.to_datetime(news_date)
    return news_date

def topdaily(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='span.published_at').text
    news_date = pd.to_datetime(news_date)
    return news_date

def kukinews(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='div.publishDate').text.replace('기사승인 ','')
    news_date = pd.to_datetime(news_date)
    return news_date

def economist(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#present_issue_day').text.split()[2:4]
    news_date = pd.to_datetime(' '.join(news_date))
    return news_date

def asiatime(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div:nth-child(8) > div:nth-child(7) > div > div > div.article_title_area > p > span:nth-child(2)').text.split()[1:2]
    news_date = pd.to_datetime(' '.join(news_date))
    return news_date

def metroseoul(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div.container > div.article-title > div > span:nth-child(2)').text.replace('ㅣ','')
    news_date = pd.to_datetime(news_date)
    return news_date

def ddaily(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div > div.article_head > div.util_box > div.byline > span.date').text.split(' ')[1:]
    news_date = pd.to_datetime(' '.join(news_date))
    return news_date

def itworld(browser):
    time.sleep(1)
    try:
        news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div:nth-child(11) > div > div.col-12.ps-lg-0.pe-lg-0 > div > div.section-content.col-12.col-lg.pe-lg-5 > div.mx-3.mx-lg-0.my-4.border-bottom > div > small.font-color-5.font-lato').text
    except:
        try:
            news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div:nth-child(12) > div > div.col-12.ps-lg-0.pe-lg-0 > div > div.section-content.col-12.col-lg.pe-lg-5 > div.mx-3.mx-lg-0.my-4.border-bottom > div > small.font-color-5.font-lato').text
        except:    
            news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div.mt-5.bg-bottom > div > div > div:nth-child(1) > div.d-flex.align-items-center.justify-content-between.mt-3 > div.d-flex.align-items-center > small.text-tlb-primary-3.font-lato.d-flex.align-items-center').text
    news_date = pd.to_datetime(news_date)
    return news_date

def news1(browser):
    time.sleep(1)
    try:
        plus_btn = browser.find_element(by=By.CSS_SELECTOR,value='#updated > button > svg')
        plus_btn.click()
    except: 
        pass
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#published').text.split(' ')[0]
    news_date = pd.to_datetime(news_date)
    return news_date

def datanews(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='span.datetime').text
    news_date = pd.to_datetime(news_date)
    return news_date

def ciokorea(browser):    
    time.sleep(1)
    try:
        news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div:nth-child(11) > div > div.col-lg-12.col-xl-9 > div > div.row > div.col-12 > div.d-flex.justify-content-between.align-items-center.mt-5.py-2.border-bottom.border-3.mb-4 > div:nth-child(1) > small.font-color-primary-2.font-lato.d-flex.align-items-center.font-lato').text
    except:
        try:
            news_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div:nth-child(12) > div > div.col-lg-12.col-xl-9 > div > div.row > div:nth-child(2) > div.d-flex.justify-content-between.align-items-center.mt-5.py-2.border-bottom.border-3.mb-4 > div:nth-child(1) > small.font-color-primary-2.font-lato.d-flex.align-items-center.font-lato').text
        except:
            news_date = browser.find_elment(by=By.CSS_SELECTOR,value='body > div:nth-child(11) > div > div.col-lg-12.col-xl-9 > div > div.row > div.col-12 > div.d-flex.justify-content-between.align-items-center.mt-5.py-2.border-bottom.border-3.mb-4 > div:nth-child(1) > small.font-color-primary-2.font-lato.d-flex.align-items-center.font-lato').text
    if '일 전' in news_date:
        date_int = int(news_date.replace('일 전',''))
        now = datetime.now()
        news_date = (now - timedelta(days=date_int)).date()
    news_date = pd.to_datetime(news_date)
    return news_date

def nate(browser):
    
    time.sleep(1)
    news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#contents > div.responsive_wrap > section.rwd_left > div > header > div.medium > div>em')[0]
    news_date = news_date.find_element(by=By.CSS_SELECTOR,value='span').text
    news_date = pd.to_datetime(news_date)
    return news_date

def digital_times(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='div.article_info > span:nth-child(1)').text.replace('입력: ','')
    news_date = pd.to_datetime(news_date)
    return news_date    

def hani(browser):
    time.sleep(1)
    try:
        news_date = browser.find_element(by=By.CSS_SELECTOR,value='#renewal2023 > div.ArticleDetailView_articleDetail__IT2fh > ul > li:nth-child(1) > span').text
    except:
        news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#__next > div > div > div.ArticleBgHeader_headerWrapper__NLj75 > section > div.ArticleBgHeader_articleDetail__pvl2b > div.ArticleBgHeader_bottomWrapper__p34ah > ul > li> span')[-1].text
    news_date = pd.to_datetime(news_date)
    return news_date   

def munhwa(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div > section.section_split.mb64 > div > div.section_split_item.view_contents > div > div.view_info_01 > ul > li:nth-child(2)').text.replace('입력 ','')
    news_date = pd.to_datetime(news_date)
    return news_date   

def naver(browser):
    time.sleep(1)
    news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div')[0]
    news_date = news_date.find_element(by=By.CSS_SELECTOR,value='span').text
    news_date = pd.to_datetime(news_date.split(' ')[0])
    return news_date

def busan(browser):
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div:nth-child(2) > div.section > div.article_view > div.article_head > div.byline').text
    news_date = pd.to_datetime(' '.join(news_date.split(' ')[-2:]))
    return news_date

def kookje(browser):
    
    time.sleep(1)
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#news_topArea > div.news_reporterDate.left > ul > li:nth-child(2) > span').text
    news_date = pd.to_datetime(' '.join(news_date.split(' ')[-2:]))
    return news_date

def chosun(browser):
    time.sleep(1)
    try:
        news_title = browser.find_element(by=By.CSS_SELECTOR,value='#v-left-scroll-in > div.article_head > div.article_info > span:nth-child(1)').text
    except:
        try:
            news_title = browser.find_element(by=By.CSS_SELECTOR,value='h1.heading').text
        except:
            news_title = browser.find_element(by=By.CSS_SELECTOR,value='#fusion-app > div.article > div:nth-child(2) > div > div > div > h1').text
    try:
        news_content = browser.find_element(by=By.CSS_SELECTOR,value='#fusion-app > div.article > div:nth-child(2) > div > section > article > section').text
    except:
        news_content = browser.find_element(by=By.CSS_SELECTOR,value='#article-view-content-div').text
    try: 
        plus_btn = browser.find_element(by=By.CSS_SELECTOR,value='span.upDate > svg')
        plus_btn.click()
        time.sleep(1)
    except:
        pass
    try: 
        news_date = browser.find_element(by=By.CSS_SELECTOR,value='span.inputDate').text.split()[1]
    except:
        news_date= browser.find_element(by=By.CSS_SELECTOR,value='#article-view > div > header > div > ul > li:nth-child(2)').text.replace('입력 ','')
    news_date = pd.to_datetime(news_date)
    news_dict = {'news_title':news_title,
                                    'news_content':news_content,
                                    'news_date': news_date}
    return news_dict
    
def kbs(browser):
    time.sleep(1)
    news_title = browser.find_element(by=By.CSS_SELECTOR,value='h4.headline-title').text
    news_content = browser.find_element(by=By.CSS_SELECTOR,value='div > #cont_newstext').text
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='div.dates > em.input-date').text.split()[1]
    news_date = pd.to_datetime(news_date)
    news_dict = {'news_title':news_title,
                                    'news_content':news_content,
                                    'news_date': news_date}
    return news_dict

def boannews(browser):
    time.sleep(1)
    news_title = browser.find_element(by=By.CSS_SELECTOR,value='#news_title02 > h1').text
    news_content = browser.find_element(by=By.CSS_SELECTOR,value='div#news_content').text
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#news_util01').text.replace('입력 : ','')
    news_date = pd.to_datetime(news_date)
    news_dict = {'news_title':news_title,
                                    'news_content':news_content,
                                    'news_date': news_date}
    return news_dict

def sbs_biz(browser):
    time.sleep(1)
    news_title = browser.find_element(by=By.CSS_SELECTOR,value='#cnbc-front-articleHeader-self > div > div > h3').text
    news_content = browser.find_element(by=By.CSS_SELECTOR,value='#cnbc-front-articleContent-area-font').text    
    news_date = browser.find_element(by=By.CSS_SELECTOR,value='#cnbc-front-articleHeader-self > div > div > div.ah_info > span.ahi_date').text.replace('입력 ','')
    news_date = pd.to_datetime(news_date)
    news_dict = {'news_title':news_title,
                                    'news_content':news_content,
                                    'news_date': news_date}
    return news_dict

def fetch_news_date(news_link, browser):
    # 뉴스 날짜를 사이트에서 가져오는 함수
    handlers = {
        'n.news.naver': naver,
        'www.busan': busan,
        'www.hani': hani,
        'www.dt': digital_times,
        'www.kookje': kookje,
        'www.munhwa': munhwa,
        'm.news.nate': nate,
        'ddaily.co.kr':ddaily,
        'itworld.co.kr':itworld,
        'news1.kr':news1,
        'datanews.co.kr':datanews,
        'ciokorea':ciokorea,
        'dnews.co.kr':dnews,
        'topdaily.kr': topdaily, 
        'kukinews.com': kukinews, 
        'economist.co.kr': economist,  
        'asiatime.co.kr': asiatime, 
        'metroseoul.co.kr': metroseoul,
        'it.donga' : donga,
        'skyedaily' : skyedaily,
        'news.mtn' : mtn,
        'dream.kotra' : kotra,
        'newspim' : newspim,
        'nocutnews' : nocut,
        'newsprime' : newsprime,
        'medipana.com' : medipana,
        'marketinsight': marketinsight, 
        'dailynk': dailynk, 
        'kgnews': kgnews, 
        'dailymedi': dailymedi, 
        'kyeongin': kyeongin, 
        'newstomato': newstomato, 
        'esquirekorea': esquirekorea,
        'lawtimes' : lawtimes,
        'chosun.com': chosun,
        'biz.sbs': sbs_biz,
        'news.kbs': kbs,
        'boannews.com': boannews

    }
    for key, handler in handlers.items():
        if key in news_link:
            return handler(browser)
    return None
# answer = itworld(browser)
# print(answer)
