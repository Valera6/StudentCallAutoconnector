import time, os, json, subprocess, sys
from datetime import datetime
from pprint import pprint

import telebot
from telebot import types

bot = telebot.TeleBot('5873490198:AAEF0SjUqUyiLyc_LkSkY7DltGu0VEI652I')
platforms = ['Microsoft Teams', 'Zoom', 'Google Meets', 'Discord']

support_chat_id = 499185038
len_details = 2 #Number of elements in general.json

#---------------------------------------------------------- 
# initial definition
def current_function(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text='Не понимаю, что вы имеете ввиду')

class Platform():
    # I want here a function of:
    # date-setting
    # link-sending
    def __init__(self, chat_id):
        self.platform = self.__class__.__name__
        self.chat_id = chat_id

        self.timezone = 'Europe/Moscow'
        self.leave_percentage = 51
        self.guest_name = None
        self.join_message = None

        self.time = None
        self.link = None

        self.mail = None
        self.password = None

    #<general-data>
    def general_data(self):
        bot.send_message(chat_id=self.chat_id,
                         text='По умолчанию ваша временная зона: Europe/Mosccow. Вы можете изменить ее, используя /general')

        bot.send_message(chat_id=self.chat_id,
                         text='Введите имя, под которым вы хотите подключаться к звонкам в роли гостя')
        global current_function
        current_function = self.set_guest_name
    def set_guest_name(self, msg):
        self.guest_name = msg.text
        bot.send_message(chat_id=self.chat_id,
                         text='Сбор общих данных закончен')
        with open(f'Users/{str(self.chat_id)}/general.json', 'w') as f:
            json.dump({"timezone": self.timezone, "guest_name": self.guest_name}, f, indent=4, separators=(",", ": "))

        bot.send_message(chati_id=self.chat_id,
                         text='Продолжая ползоваться ботом, вы принимаете условия пользовательского соглашения https://docs.google.com/document/d/1595oRSSZiy9RQ4pOTazH5-h-YtDtuBErfbykxeN3BWA/edit?usp=sharing')

        handle_command_adminwindow(msg)
    #</general-data>

    #<initiation>
    def start(self):
        bot.send_message(chat_id=self.chat_id,
            text=f'В какое время вы хотите подключиться к звонку? ({self.timezone}, пример: "13-04 18:31")')
        global current_function
        current_function = self.set_time
    def set_time(self, msg):
        try:
            time = datetime.now()
            new = datetime.strptime(msg.text, '%d-%m %H:%M')
            self.time = new.replace(year=time.year)

            bot.send_message(chat_id=msg.chat.id,
                     text="Отправьте ссылку на звонок")
            global current_function
            current_function = self.receive_link
        except:
            bot.send_message(chat_id=self.chat_id,
                                text='Ошибка в выставлении даты. Проверьте, что ваше сообщение выглядит так: "dd-mm HH:MM" пример: 18-11 09:31')
    def receive_link(self, msg):
        self.link = msg.text.strip()

        with open(f'Users/{str(self.chat_id)}/general.json', 'r') as f:
            details = json.load(f)
        self.timezone = details['timezone']
        self.guest_name = details['guest_name']

        with open(f'{self.platform}/config.json', 'r') as f:
            config = json.load(f)
        config['meetingtime'] = self.time.isoformat()
        config['link'] = self.link
        config['chat_id'] = self.chat_id
        config['timezone'] = self.timezone
        config['guest_name'] = self.guest_name
        config['leave_percentage'] = self.leave_percentage
        with open(f'{self.platform}/config.json', 'w') as f:
            json.dump(config, f, indent=4, separators=(",", ": "))

        bot.send_message(chat_id=msg.chat.id,
                     text=f"Звонок пройдет в {self.time} {self.timezone}")

        p = subprocess.run(['python', f'{self.platform}/main.py'])
    #</initiation>

class Meets(Platform):
    pass
  
class Teams(Platform):
#TODO: implement this for when requested. # also maybe move into the parent Platform class
    #<login details>
    def log_in(self):
        try:
            with open(f'Users/{str(self.chat_id)}/Teams.json', 'r') as f:
                details = json.load(f)
            self.mail = details['mail']
            self.password = details['password']
            
            with open(f'{self.platform}/config.json', 'r') as f:
                config = json.load(f)
            config['email'] = self.mail
            config['password'] = self.password
            config['chat_id'] = self.chat_id
            with open(f'{self.platform}/config.json', 'w') as f:
                json.dump(config, f, indent=4, separators=(",", ": "))
            bot.send_message(chat_id=self.chat_id,
                             text='Проверяем акуальность данных. Ожидайте, пока мы заходим в аккаунт')
            from Teams.main import log_in
            log_in()
    
            bot.send_message(chat_id=self.chat_id,
                text=f'В какое время вы хотите подключиться к звонку? ({self.timezone}, пример: "04-08 18:31")')
            global current_function
            current_function = self.set_time
        except:
            print('DEBUG: requesting login data')
            bot.send_message(chat_id=self.chat_id,
                                 text='Вам нужно ввести ваши актуальные детали для входа в аккаунт')
            self.login_details()
    def login_details(self):
        bot.send_message(chat_id=self.chat_id,
                         text='введите ваш имейл адрес от аккаунта без пробелов и лишних символов')
        global current_function
        current_function = self.get_mail
    def get_mail(self, msg):
        self.mail = msg.text
        bot.send_message(chat_id=self.chat_id,
                         text='введите ваш пароль от аккаунта без пробелов и лишних символов')
        global current_function
        current_function = self.get_password
    def get_password(self, msg):
        self.password = msg.text

        with open(f'Users/{str(self.chat_id)}/Teams.json', 'w') as f:
            json.dump({"mail": self.mail, "password": self.password}, f, indent=4, separators=(",", ": "))

        self.start()
    #</login details>

class Zoom(Platform):
    # for now could do without login in
    pass
class Discord(Platform):
    pass
# -----------------------------------------------------------

def makeKeyboard():
    markup = types.InlineKeyboardMarkup()

    for platform in platforms:
        markup.add(types.InlineKeyboardButton(text=platform,
                                              callback_data=platform)) 

    return markup

@bot.message_handler(commands=['help'])
def commands_list(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text='/general для изменения базовых параметров, включая временную зону, сообщение при подключении, имя при анонимном подключении\
                     \n/ask чтобы задать вопрос поддержке\
                     \n/roadmap чтобы увидеть наш планы по развитию функционала')
@bot.message_handler(commands=['ask'])
def ask_question_prompt(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text='Введите ваш вопрос следующим сообщением. Наш сотрудник свяжется с вами в рабочее время')
    global current_function
    current_function = ask_question
def ask_question(msg):
    bot.send_message(chat_id=support_chat_id,
                     text=f'question from {msg.chat.id}: {msg.text}\n\n(Для ответа отправь сообщение формы [<client_id> your_text])')
    print(f'DEBUG: asked a question')
    bot.send_message(chat_id=msg.chat.id,
                     text='Мы зарегистрировали ваш вопрос')
@bot.message_handler(commands=['general'])
def general_command(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text='not implemented yet')

@bot.message_handler(commands=['roadmap'])
def send_roadmap(msg):
    bot.send_message(chat_id=msg.chat.id,
                     text='this is roadmap')
#TODO: this
@bot.message_handler(commands=['start'])
def handle_command_adminwindow(msg):
    print(f'DEBUG: {msg.chat.id} connected')
    global chat_id
    chat_id = msg.chat.id

    if not os.path.exists(f"Users/{str(chat_id)}/general.json"):
        os.mkdir(f"Users/{str(chat_id)}")
        Platform(chat_id).general_data()
    else:
        with open(f"Users/{str(chat_id)}/general.json") as f:
            details = json.load(f)
        if len(details)<len_details:
            Platform(chat_id).general_data()
        else:
            bot.send_message(chat_id=msg.chat.id,
                             text="Где будет проходить звонок?",
                             reply_markup=makeKeyboard(),
                             parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    choice = call.data
    print(f'DEBUG: User requested {choice}')
    bot.send_message(chat_id=chat_id,
                     text = f'Вы выбрали {choice}')
    #TODO: call one of the functions for a dialog tree for a each platform
    if choice == 'Discord':
        platform = Discord(chat_id)
    if choice == 'Google Meets':
        platform = Meets(chat_id)
    if choice == 'Microsoft Teams':
        platform = Teams(chat_id)
    if choice == 'Zoom':
        platform = Zoom(chat_id)

    platform.start()

@bot.message_handler(content_types=["text"])
def handle_text(msg):
    if msg.text.split()[0][0] == '<':
        print(f'DEBUG: response from support')

        user_id = int(msg.text.split()[0].strip('<>'))
        response = ' '.join(msg.text.split()[1:])
        bot.send_message(chat_id=user_id,
                         text=response)

    #current_function is doing different things, depending on which platform the user chose and what step he is on
    current_function(msg)

if __name__ == '__main__':
    print('Bot started...')
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(e)
            time.sleep(10)
