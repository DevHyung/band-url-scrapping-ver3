import time
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.alert import Alert
#실패
#https://band.us/band/73030454?extra_data=%7B%22inflow_method%22%3A%22section%22%2C%22section_no%22%3A19%7D
if __name__=="__main__":
    #===CONFIG
    driver = webdriver.Chrome('./chromedriver')
    driver.get('https://band.us/discover/search/로그인')
    driver.maximize_window()
    enter = input(">>> 밴드 로그인후에 엔터를 눌러주세요 : ")
    #try:
    while True:
        # Excel
        wb = Workbook()
        ws1 = wb.worksheets[0]
        header1 = ['이름', 'URL', 'member_count']
        ws1.column_dimensions['A'].width = 60
        ws1.column_dimensions['B'].width = 50
        ws1.column_dimensions['C'].width = 20
        ws1.append(header1)

        keyword = input(">>> 키워드를 입력하세요 :: ")
        min = int( input(">>> Min ~ MAX 멤버수중 Min값을 입력하세요(포함) :") )
        max = int(input(">>> {} ~ MAX 멤버수중 Min값을 입력하세요(포함) :".format(min)))
        print(">>> {} ~ {} 멤버 + 바로가입가능한 밴드만 추출을 시작합니다.".format(min,max))
        print("___"*20)
        baseUrl = 'https://band.us/'
        url = 'https://band.us/discover/search/' + keyword

        #=========
        driver.get(url)
        time.sleep(3)

        driver.find_element_by_xpath('//*[@id="header"]/div[2]/form/fieldset/input').clear()
        driver.find_element_by_xpath('//*[@id="header"]/div[2]/form/fieldset/input').send_keys(keyword+Keys.ENTER)
        time.sleep(2)
        try:
            cnt = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/section[2]/div/div/h1/span').text.strip()
        except:
            cnt = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/section/div/div/h1/span').text.strip()
        print(">>> 총 검색 갯수 : ",cnt)
        lisLength = 0
        while int(cnt) > lisLength:
            body = driver.find_element_by_css_selector('body')
            bs4 = BeautifulSoup(driver.page_source,'lxml')
            lis = bs4.find('ul',class_='cCoverList searchResult _bandListContainer').find_all('li')
            lisLength = len(lis)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
        print(">>> URL 추출완료 조건에 맞는 밴드 검색중 ...")
        realCnt = 0
        liIdx =  1
        for li in lis:
            print("\t>>> {}번째 검사중...".format(liIdx),end=' => ')
            liIdx +=1
            try:
                bandUrl = baseUrl + li.find('a')['href']
                name = li.find('strong',class_='name').find('span').get_text().strip()
                memberCnt = int ( li.find('strong',class_='totalNumber').get_text().strip().replace(',','') )
            except:
                print("")
                continue
            if min <= memberCnt <= max:
                try:
                    driver.get(bandUrl)
                except:
                    Alert(driver).accept()
                    time.sleep(0.2)
                    driver.get(bandUrl)
                time.sleep(1)
                idx = 1
                while True:
                    try:
                        driver.find_element_by_xpath('//*[@id="infoInner"]/div[2]/button').click()
                        break
                    except:
                        idx += 1
                        time.sleep(0.2)
                        if idx == 20:
                            print(">>> 밴드 가입하기 버튼 누르기 오류")
                            break
                time.sleep(1)
                idx = 1
                while idx < 5:
                    try:
                        driver.find_element_by_xpath(
                            '//*[@id="wrap"]/div[2]/div/section/div/div/div[1]/ul/li/label/span[3]/span/input').click()
                        break
                    except:
                        idx += 1
                        time.sleep(0.2)
                if idx < 5:
                    print("조건충족")
                    ws1.append([name, bandUrl, memberCnt])
                    realCnt += 1
                else:
                    print("X")
            else:
                print("인원수 미달")
        print(">>> 총 {}개 추출완료 파일저장중".format(realCnt))
        wb.save('./'+keyword + "{}~{}.xlsx".format(min,max))
        lastInput = input("종료하시려면 q 또는 Q를 눌러주세요:").strip()
        if lastInput.lower() == 'q':
            break
    # except:
    #     wb.save('./' + keyword + "{}~{}.xlsx".format(min, max))
    #     print(">>> 비정상적종료 자꾸 반복되면 관리자한테 연락부탁드립니다.")
    #     input(">>> 종료하시려면 아무키나 눌러주세요.")

    driver.quit()