import json, time, pytz
from threading import Timer
from datetime import datetime

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

browser: webdriver.Chrome = None
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
        with open('Zoom/config.json', 'r') as f:
            config = json.load(f)
    except:
        with open('config.json', 'r') as f:
            config = json.load(f)

def wait_until_found(sel, timeout):
    try:
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
        WebDriverWait(browser, timeout).until(element_present)

        return browser.find_element_by_css_selector(sel)
    except exceptions.TimeoutException:
        print("Timeout waiting for element.")
        return None



def join_meeting():
    global browser, config
    load_config()

    """tz = pytz.timezone(config['timezone'])
    now = datetime.now(tz)
    run_at = datetime.fromisoformat(config['meetingtime'])
    run_at = tz.localize(run_at)
    if run_at < now:
        tg_msg('Выбранное время уже прошло. Проверьте время начала и запустите бота заново')
        raise Exception ('Chosen time is out of bounds')

    start_delay = (run_at - now).total_seconds()
    print(f"DEBUG: Waiting until {run_at} ({int(start_delay)}s)")
    time.sleep(start_delay)"""

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    #chrome_options.add_argument('--headless')
    browser.maximize_window()
    
    browser.get(config['link'])

    # click continue in the browser
    continue_in_browser = wait_until_found("div.text", 30)
    if continue_in_browser is None:
        print('DEBUG: Continue-in-browser button not found')
        #return

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
        #guest_name_btn.click()
        guest_name_btn.send_keys(config['guest_name'])
        time.sleep(1)
        print(f'DEBUG: entered guest name')

    # final join button
    join_now_btn = wait_until_found("button[data-tid='prejoin-join-button']", 30)
    if join_now_btn is None:
        print('DEBUG: Join now button not found')
        return
    join_now_btn.click()
#TODO: if he wants to log in, we do so here
    print(f'DEBUG: Successfuly connected')
    tg_msg('Успешно присоединились к звонку. Отключение произойдет автоматически.')
#TODO: control paste the message on join
    total_members = 1
    while True:
        time.sleep(10)
        members_count = None
        try:
            try:
                members_element = wait_until_found("span.toggle-number", 5)
                members_count = int(members_element.text.strip('() '))
            except:
                move_mouse()
                browser.execute_script("document.getElementById('roster-button').click()")
                members_element = wait_until_found("span.toggle-number", 5)
                members_count = int(members_element.text.strip('() '))

            if (members_count/total_members) * 100 < int(config['leave_percentage']):
                # hangup button
                print('DEBUG: Exiting Meeting...')
                close_participants = wait_until_found("svg.app-svg.icons-close", 5)
                ##page-content-wrapper > div.flex-fill > div > calling-screen > div > div.ts-calling-screen.flex-fill.call-connected.PERSISTENT.GRID.passive-bar-available.has-meeting-info.closed-captions-hidden.show-roster.has-panel.trigger-overlap.pip-expanded.show-myself-preview.immersive > meeting-panel-components > calling-roster > div > right-pane-header > div > div > button
                if close_participants != None:
                    close_participants.click()
                    print(f'DEBUG: closed participants')
                print(f'DEBUG: moving mouse')
                while True:
                    try:
                        move_mouse()
                        time.sleep(0.5)
                        hangup_btn = wait_until_found("button[id='hangup-button']", 5)
                        hangup_btn.click()
                        print('DEBUG: Exited')
                        tg_msg('Звонок завершен')
                        browser.quit()
                        break
                    except:
                        pass
                break

            if members_count and members_count > total_members:
                total_members = members_count
        except:
            pass
    
if __name__ == "__main__":
    join_meeting()
