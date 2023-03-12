from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.by import By


def extract_review(place_id, driver):

    time.sleep(1)
    while True:
        try:
            if driver.find_element(By.CSS_SELECTOR, '#mArticle > div.cont_evaluation > div.evaluation_review > a').text == '후기 더보기':
                driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, '#mArticle > div.cont_evaluation > div.evaluation_review > a'))
            else:
                break
        except:
            break
        time.sleep(1)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        review_lists = soup.find('ul', {'class':'list_evaluation'}).find_all('li')
    except:
        return ''
    
    p_name = []
    u_name = []
    u_rating = []
    u_comment = []
    
    for review_list in review_lists:
        try:
            user_id = review_list.find('a', {'class':'link_user'}).text
        except:
            user_id = ''
            continue
        
        try:
            value = review_list.find('div', {'class':'star_info'}).find('div').find('span').find('span')['style']
            value = value.replace('width:', '')
            value = value.replace('%;', '')
            user_rating = int(value)/20
        except:
            user_rating = ''
            continue
        
        try:
            user_comment = review_list.find('p', {'class':'txt_comment'}).find('span').text
        except:
            user_comment = ''
            continue
        p_name.append(place_id)
        u_name.append(user_id)
        u_rating.append(user_rating)
        u_comment.append(user_comment)
        
        print('place_id:', place_id)
        print('user_id:', user_id)
        print('score:', user_rating)
        print('comment:', user_comment)
    
    review_df = pd.DataFrame({
        'place_id':p_name,
        'user_id':u_name,
        'score':u_rating,
        'comment':u_comment
    },)

    review_df.to_csv(f'./review/{place_id}.csv', index=False, encoding='utf-8-sig')

def crawling(url, seachWord, pageLimit):
    chromedriver_dir = r'./chromedriver.exe'
    driver = webdriver.Chrome(chromedriver_dir)
    driver.get(url)
    time.sleep(1)

    inputbox = driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]')
    driver.execute_script("arguments[0].click();", inputbox)
    inputbox.send_keys(seachWord)
    inputbox.send_keys(Keys.ENTER)
    time.sleep(1)

    print(driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/div[1]/ol/li[2]/a').text)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/div[1]/ol/li[2]/a'))

    title = []
    address = []
    url_lst = []
    rate = []
    tags = []
    page_num = 1
    while page_num != pageLimit:
        time.sleep(1)
        ul = driver.find_element(By.XPATH, '//*[@id="info.search.place.list"]')
        driver.execute_script("arguments[0].click();", ul)
        time.sleep(1)
        lis = ul.find_elements(By.TAG_NAME, 'li')
        print(len(lis))
        idx = page_num % 5

        for li in lis:
            print(li)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", li.find_element(By.CSS_SELECTOR, 'div.info_item > div.contact.clickArea > a.moreview'))
            driver.switch_to.window(window_name=driver.window_handles[-1])
            print(driver.current_url)
            time.sleep(2)
            p_id = driver.find_element(By.XPATH, '//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/h2').text
            title.append(p_id)
            address.append(driver.find_element(By.XPATH, '//*[@id="mArticle"]/div[1]/div[2]/div[1]/div/span[1]').text)
            rate.append(driver.find_element(By.XPATH, '//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/a[1]/span[1]').text)
            tags.append(driver.find_element(By.XPATH, '//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/span[1]').text)
            url_lst.append(driver.current_url)
            extract_review(place_id=p_id, driver=driver)
            driver.switch_to.window(window_name=driver.window_handles[-1])
            
            
            driver.close()
            driver.switch_to.window(window_name=driver.window_handles[0])
            # driver.execute_script("arguments[0].click();", li.find_element(By.XPATH, ' #info\.search\.place\.list > li.PlaceItem.clickArea.PlaceItem-ACTIVE > div.rating.clickArea > span.score > a'))
            
        if idx == 0:
            driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="info.search.page.next"]'))
        else:
            driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="info.search.page.no' + str(idx + 1) +'"]'))
            
        page_num += 1

    driver.quit()
    
    df = pd.DataFrame({'title': title, 'rate': rate, 'tags': tags, 'address': address, 'url': url_lst})
    df.to_csv('ulsan_titelist.csv', index = False, encoding='utf-8-sig')
    
def main():
    url = 'https://map.kakao.com/'
    searchWord = '울산 음식점' # 검색어 설정
    pageLimit = 21 # 크롤링할 페이지 수
    crawling(url, searchWord, pageLimit)
    
if __name__ == "__main__":
    main()