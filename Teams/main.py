import json, time, pytz, pdb, random
from threading import Timer
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

driver: webdriver.Chrome = None
config = None
active_meeting = None
uuid_regex = r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b"
hangup_thread: Timer = None

#<send tg msg>
import telebot
API_KEY = '5873490198:AAEF0SjUqUyiLyc_LkSkY7DltGu0VEI652I'
tb = telebot.TeleBot(API_KEY, False)
def tg_msg(msg):
    tb.send_message(config['chat_id'], msg)
#</send tg msg>

def load_config():
    global config
    try:
        with open('Teams/config.json', 'r') as f:
            config = json.load(f)
    except:
        with open('config.json', 'r') as f:
            config = json.load(f)
load_config()

def wait_until_found(sel, timeout=5, method=By.CSS_SELECTOR):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((method, sel)))
        return element
    except exceptions.TimeoutException:
        print(f"Timeout waiting for element with sel: {sel}")
        return None

def junk_popups():
    #engagement-surface-dialog > div > div > div.ts-modal-dialog-footer > div > div:nth-child(1) > button
    #ts-btn ts-btn-fluent ts-btn-fluent-secondary
    pass
def switch_to_teams_tab():
    teams_button = wait_until_found("button.app-bar-link > ng-include > svg.icons-teams", 5)
    if teams_button is not None:
        teams_button.click()
def move_mouse():
    width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
    height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

    x = random.randint(0, width)
    y = random.randint(0, height)

    actions = ActionChains(driver)
    actions.move_by_offset(x, y)
    actions.perform()

def initialize(start_time):
    tz = pytz.timezone(config['timezone'])
    now = datetime.now(tz)
    run_at = datetime.fromisoformat(config['meetingtime']) if not start_time else start_time
    run_at = tz.localize(run_at)
    if run_at < now:
        tg_msg('Выбранное время уже прошло. Проверьте время начала и запустите бота заново')
        raise Exception ('Chosen time is out of bounds')

    start_delay = (run_at - now).total_seconds()
    print(f"DEBUG: Waiting until {run_at} ({int(start_delay)}s)")
    time.sleep(start_delay)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    #chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #driver.maximize_window()

    return driver
def join_meeting(start_time=None):
    global driver, config, completion_status
    driver = initialize(start_time)
    completion_status = 400
    i=0
    while completion_status != 200 and i<10:
        try:
            driver.get(config['link'])

            # click continue in the driver
            continue_in_browser = wait_until_found('[data-tid="joinOnWeb"]', 30)
            if continue_in_browser is None:
                print('DEBUG: Continue-in-browser button not found')
                time.sleep(1000)

            continue_in_browser.click()
            print('DEBUG: Continue-in-browser Button Clicked')

            # turn camera off
            video_btn = wait_until_found("button.ts-toggle-button[track-name='1047']", 30)
            time.sleep(7)
            video_is_on = video_btn.get_attribute('aria-pressed')
            if video_is_on == "true":
                print('DEBUG: Video Turned Off')
                video_btn.click()

            # turn mic off
            audio_btn = wait_until_found("button.ts-toggle-button[track-name='1048']", 5)
            audio_is_on = audio_btn.get_attribute('aria-pressed')
            if audio_is_on == "true":
                print('DEBUG: Audio Turned Off')
                audio_btn.click()

            # enter guest name
            guest_name_btn = wait_until_found("input[id=username]", 5)
            if guest_name_btn is not None:
                guest_name_btn.send_keys(config['guest_name'])
                time.sleep(1)
                print(f'DEBUG: entered guest name')

            # final join button
            join_now_btn = wait_until_found("button[data-tid='prejoin-join-button']", 30)
            if join_now_btn is None:
                print('DEBUG: Join now button not found')
                raise Exception

            #recheck that these things are dealt with and click join
            audio_is_on = audio_btn.get_attribute('aria-pressed')
            if audio_is_on == "true":
                audio_btn.click()
            video_is_on = video_btn.get_attribute('aria-pressed')
            if video_is_on == "true":
                video_btn.click()
            video_is_on = video_btn.get_attribute('aria-pressed')
            if video_is_on == "true":
                print(f"DEBUG: couldn't turn off the camera. exiting")
                raise Exception
            else:
                join_now_btn.click()
                print(f'DEBUG: Successfuly connected')
                tg_msg('Успешно присоединились к звонку. Отключение произойдет автоматически.')

            #TODO: if he wants to log in, we do so here
            #TODO: control paste the message on join

            total_members = 1
            while True:
                time.sleep(5)
                global members_count, members_element
                try:
                    found, i = False, 0
                    while (not found) and i<4:
                        try:
                            element = wait_until_found("#page-content-wrapper > div.flex-fill > div > calling-screen > div > div.ts-calling-screen.flex-fill.call-connected.PERSISTENT.GRID.passive-bar-available.has-meeting-info.closed-captions-hidden.trigger-overlap.show-roster.has-panel.immersive > meeting-panel-components > calling-roster > div > div.scroll-container.flex-fill > div > div.scrolling-pane > accordion > div > accordion-section:nth-child(1) > div > calling-roster-section > div > div.roster-list-title-group.has-roster-limit > button")
                            aria_label = element.get_attribute('aria-label')
                            members_count = int(aria_label.split(' ')[-1])
                            found = True
                        except:
                            members_element = wait_until_found("#roster-button")
                            driver.execute_script("arguments[0].click();", members_element)

                            element = wait_until_found("#page-content-wrapper > div.flex-fill > div > calling-screen > div > div.ts-calling-screen.flex-fill.call-connected.PERSISTENT.GRID.passive-bar-available.has-meeting-info.closed-captions-hidden.trigger-overlap.show-roster.has-panel.immersive > meeting-panel-components > calling-roster > div > div.scroll-container.flex-fill > div > div.scrolling-pane > accordion > div > accordion-section:nth-child(1) > div > calling-roster-section > div > div.roster-list-title-group.has-roster-limit > button")
                            aria_label = element.get_attribute('aria-label')
                            members_count = int(aria_label.split(' ')[-1])
                            found = True

                        time.sleep(0.15)
                    print(f"DEBUG: members_count: {members_count}, {time.time()}")

                    if (members_count/total_members) * 100 < int(config['leave_percentage']):
                        print('DEBUG: Exiting Meeting...')
                        close_participants = wait_until_found("svg.app-svg.icons-close", 5)
                        if close_participants is not None:
                            try:
                                close_participants.click()
                            except:
                                driver.execute_script("arguments[0].click();", close_participants)
                            print(f'DEBUG: closed participants')

                        hangup_btn = wait_until_found("#hangup-button")
                        driver.execute_script("arguments[0].click();", hangup_btn)
                        print('DEBUG: Exited')
                        tg_msg('Звонок завершен')
                        driver.quit()
                        completion_status = 200
                        break

                    if members_count and members_count > total_members:
                        total_members = members_count #*4 # debugging - will make it hang up immediately after first getting the value
                        print(f"DEBUG: new peak in users: {members_count}")
                except:
                    pass
        except:
            print(f"DEBUG: couldn't connect. Retrying.")
            i+= 1
    if not completion_status == 200:
        tg_msg('!!!Не смогли подключиться к звонку. Завершаем сессию.')

def log_in():
    global driver, config

    load_config()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.maximize_window()

    driver.get("https://teams.microsoft.com")
    try:
        if config['email'] != "" and config['password'] != "":
            print('Email and Password found in config.json!')

        login_email = wait_until_found("input[type='email']", 30)
        if login_email is not None:
            login_email.send_keys(config['email'])
            time.sleep(1)

        # find the element again to avoid StaleElementReferenceException
        login_email = wait_until_found("input[type='email']", 5)
        if login_email is not None:
            login_email.send_keys(Keys.ENTER)

        login_pwd = wait_until_found("input[type='password']", 5)
        if login_pwd is not None:
            login_pwd.send_keys(config['password'])
            time.sleep(1)

        # find the element again to avoid StaleElementReferenceException
        login_pwd = wait_until_found("input[type='password']", 5)
        if login_pwd is not None:
            login_pwd.send_keys(Keys.ENTER)
        
        # stay signed in
        keep_logged_in = wait_until_found("input[id='idBtn_Back']", 5)
        if keep_logged_in is not None:
            keep_logged_in.click()
        
        # use web app instead
        use_web_instead = wait_until_found("a.use-app-lnk", 5)
        if use_web_instead is not None:
            use_web_instead.click()
        # find the element again to avoid StaleElementReferenceException
        use_web_instead = wait_until_found("a.use-app-lnk", 5)
        if use_web_instead is not None:
            use_web_instead.click()
    except:
        pass

    check = wait_until_found("input[id='control-input']", 5)
    if check is None:
        tg_msg('Не удалось войти в аккаунт')
        driver.quit() # likely to give an error by itself, so can't have specific to my custom Exception checks
        raise Exception('Could not log in to Microsoft Teams')
    else:
        tg_msg('Бот успешно вошел в аккаунт')
        #driver.quit()
    
if __name__ == "__main__":
    start_time = datetime.now() + timedelta(seconds=6, hours=3)
    join_meeting(start_time=start_time)
