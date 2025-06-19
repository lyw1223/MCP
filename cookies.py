import json
import os
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import psutil
load_dotenv()

KSS_ID = os.getenv("KSS_ID")
KSS_PW = os.getenv("KSS_PW")
KSS_SERVER = os.getenv("KSS_SERVER")

def main():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, headless=True)
    
    '''KSS 로그인 후 쿠키 가져오기'''        
    if KSS_SERVER == '2':
        channel = 'DEV'
        url = 'https://kssdev.surplusglobal.com/KSS/login.do'
        check_url = 'https://kssdev.surplusglobal.com/KSS/mainConts.do'
        server = 'https://kssdev.surplusglobal.com/KSS'
    elif KSS_SERVER == '1':
        channel = 'Main'
        url = 'https://zpdldptmdptm.surplusglobal.com/KSS/login.do'
        check_url = 'https://zpdldptmdptm.surplusglobal.com/KSS/mainConts.do'
        server = 'https://zpdldptmdptm.surplusglobal.com/KSS'
    else:
        raise Exception('KSS_SERVER 값이 올바르지 않습니다. 1 또는 2를 입력해주세요.')

    driver.get(url)
    time.sleep(2)
    driver.find_element(By.ID, 'userId').send_keys(str(KSS_ID))
    driver.find_element(By.ID, 'password').send_keys(str(KSS_PW))
    driver.execute_script('fn_checkToken()')   
    count = 0
    while True:
        try:               
            if driver.current_url == check_url:
                print(f'{KSS_ID} 로그인 성공')
                print(f'{channel} 서버 쿠키 저장성공')
                cookies = driver.get_cookies()
                cookies = {cookie['name']: cookie['value'] for cookie in cookies}
                with open('cookies.json', 'w') as f:
                    json.dump(cookies, f)

                '크롬드라이버 강제종료'
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'chrome' in proc.info['name'].lower():
                            cmdline = ' '.join(proc.info['cmdline']).lower()
                            if 'remote-debugging-port' in cmdline or 'undetected_chromedriver' in cmdline:
                                proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass                
                break
        except:
            time.sleep(1)
            count += 1
            if count > 10:
                raise Exception(f'count 초과로 로그인 실패: 로그인대기시간 {count}초')
            continue

if __name__ == "__main__":
    main()