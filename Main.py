import telegram as tele
from telegram.ext import Updater
from telegram.ext import CommandHandler as cmdHandler
import logging
from telegram.ext import MessageHandler, Filters
import urllib.request
from pathlib import Path
import csv
import os
import sqlite3


def start(update, context):
    print(update.message)
    logging.debug(update.message.text)
    # start_conn.execute(f'''INSERT INTO USER (FIRST_NAME, LAST_NAME, USER_NAME, CHAT_ID)
    #     VALUES ({str(update.effective_chat.first_name)}, {str(update.effective_chat.last_name)},
    #             {str(update.effective_chat.username)}, {str(update.effective_chat.id)}, NULL );''')
    try:
        start_conn = sqlite3.connect("user.db")
        start_conn.execute(f"INSERT INTO USER (FIRST_NAME, LAST_NAME, USER_NAME, CHAT_ID, STUDENT_NUMBER) "
                           f"VALUES ('{str(update.effective_chat.first_name)}', "
                           f"'{str(update.effective_chat.last_name)}', "
                           f"'{str(update.effective_chat.username)}', "
                           f"'{str(update.effective_chat.id)}', 'NULL' )")
        start_conn.commit()
        cursor_start = start_conn.execute("SELECT * FROM USER")
        global users_list
        users_list = cursor_start.fetchall()
        start_conn.close()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="به بات درس برنامه سازی پیشرفته خوش آمدید")
    except ValueError:
        print(ValueError)


def echoImage(update, context):
    print(update.message)
    if update.effective_chat.type == 'group' and update.effective_chat.title == 'ApBotEchoChat':
        sendMessageToAllUser(update, context, users_list, "IMAGE")
    else:
        file = bot.getFile(update.message.photo[1].file_id)
        passvnad = file.file_path.split('.')[len(file.file_path.split('.')) - 1]
        Path(FILE_PATH + '/' + str(update.effective_chat.first_name) +
             str(update.effective_chat.last_name)).mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(file.file_path, FILE_PATH + '/' + str(update.effective_chat.first_name) +
                                   str(update.effective_chat.last_name) + '/' + file.file_unique_id + '.' + passvnad)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="عکس ارسالی ذخیره شد",
                                 reply_markup=kb_markup)


def handleTextMessage(update, context):
    print(update)
    print(str(update.message.text == GET_CLASS_VIDEO))
    if update.message.text == BACK_TEXT:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="چه کاری انجام بدم؟",
                                 reply_markup=kb_markup)
    elif update.message.text == GET_MY_FILE_TEXT:
        user_id = getUserIdFromCharId(update.effective_chat.id)
        print("user id : " + str(user_id))
        file_list_message = ''
        keyboard_button_arrays = []
        for file in file_list:
            if file[3] == user_id:
                keyboard_button_arrays.append([tele.KeyboardButton(file[1])])
                file_list_message = file_list_message + file[1] + "\n"
        if len(keyboard_button_arrays) > 0:
            keyboard_button_arrays.append([BACK_TEXT])
            print(str(len(keyboard_button_arrays)))
            keyboard_button_markup = tele.ReplyKeyboardMarkup(keyboard_button_arrays,
                                                              resize_keyboard=True)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=file_list_message,
                                     reply_markup=keyboard_button_markup)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="چیزی تحویل نداده اید",
                                     reply_markup=kb_markup)
    elif isFileName(update.message.text, getUserIdFromCharId(update.effective_chat.id)):
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=getFileId(update.message.text,
                                                     getUserIdFromCharId(update.effective_chat.id)))
    elif update.message.text == GET_CLASS_VIDEO:
        print('inja')
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="جلسه مورد نظر را انتخاب کنید",
                                 reply_markup=keyboard_button_class_file)
    elif isClassFIleName(update.message.text):
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=getClassFileId(update.message.text),
                                  reply_markup=keyboard_button_class_file)
    elif update.effective_chat.type == 'group' and update.effective_chat.title == 'ApBotEchoChat':
        sendMessageToAllUser(update, context, users_list)
    else:
        with open('comment/comments.csv', mode='a', encoding="utf-8", newline='') as first_csv_file:
            inner_writer = csv.writer(first_csv_file)
            message_text = str(update.message.text)
            inner_writer.writerow([str(update.effective_chat.first_name),
                                   str(update.effective_chat.last_name),
                                   str(update.effective_chat.username),
                                   message_text])
        first_csv_file.close()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="پیام شما ذخیره شد با تشکر از شما",
                                 reply_markup=kb_markup)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text_caps)


def helpHandler(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="شما در بات درس برنامه سازی پیشرفته ثبت نام شده اید برای ارسال شماره دانشجویی و یا ویرایش آن از دستور \n /studentnum  شماره  دانشجویی \n استفاده کنید \n"
                                  " تمامی فایل های ارسالی شما در حافظه بات ذخیره می شود لیست فایل های ارسالی خود را می توانید با استفاده از گزینه های زیر دریافت کنید.",
                             reply_markup=kb_markup)


def DocumentCallBack(update, context):
    print(update.message)
    file_conn = sqlite3.connect("user.db")
    if update.effective_chat.type == 'group' and update.effective_chat.title == 'ApBotEchoChat':
        sendMessageToAllUser(update, context, users_list, type="DOC")
    elif update.effective_chat.type == 'group' and update.effective_chat.title == 'ApBotGroup':
        file_conn.execute(f"INSERT INTO CLASS_FILE (CHAT_ID, FILE_NAME, FILE_ID, CAPTION, FILE_SIZE) "
                          f"VALUES ('{str(update.effective_chat.id)}',"
                          f" '{str(update.message.document.file_name)}',"
                          f" '{str(update.message.document.file_id)}',"
                          f" '{str(update.message.caption)}',"
                          f" '{str(update.message.document.file_size)}');")
        file_conn.commit()
        global class_file_list
        class_file_list.clear()
        class_file_list_inner_courser = file_conn.execute("SELECT * FROM CLASS_FILE")
        class_file_list = class_file_list_inner_courser.fetchall()
        class_file_list_inner_courser.close()
        global keyboard_button_class_file
        keyboard_button_arrays.clear()
        for class_file in class_file_list:
            keyboard_button_arrays.append([tele.KeyboardButton(class_file[2])])
        if len(keyboard_button_arrays) > 0:
            keyboard_button_arrays.append([BACK_TEXT])
            keyboard_button_class_file = tele.ReplyKeyboardMarkup(keyboard_button_arrays,
                                                                  resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="فایل ارسالی ذخیره شد",
                                 reply_markup=kb_markup)
    else:
        Path(FILE_PATH + '/' + str(update.effective_chat.first_name) +
             str(update.effective_chat.last_name)).mkdir(parents=True, exist_ok=True)
        file = tele.PassportFile.get_file(bot.getFile(update.message.document.file_id)) \
            .download(FILE_PATH + '/' + str(update.effective_chat.first_name) +
                      str(update.effective_chat.last_name) + '/' + str(update.message.document.file_name))
        file_conn.execute(f"INSERT INTO FILE (FILE_NAME, FILE_ID, USER_ID) "
                          f"VALUES ('{str(update.message.document.file_name)}',"
                          f" '{str(update.message.document.file_id)}',"
                          f" (SELECT ID FROM USER WHERE CHAT_ID='{str(update.effective_chat.id)}'))")
        file_conn.commit()
        cursor_file = file_conn.execute("SELECT * FROM FILE")
        global file_list
        file_list = cursor_file.fetchall()
        print(file_list)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="فایل ارسالی ذخیره شد",
                                 reply_markup=kb_markup)
    file_conn.close()


def handleStudentNumberCallBack(update, context):
    if len(context.args) > 0:
        number = context.args[0]
        student_conn = sqlite3.connect("user.db")
        student_conn.execute(
            f"UPDATE USER SET STUDENT_NUMBER = '{number}' where CHAT_ID = '{update.effective_chat.id}'")
        student_conn.commit()
        cursor_start = student_conn.execute("SELECT * FROM USER")
        global users_list
        users_list = cursor_start.fetchall()
        student_conn.close()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="شماره دانشجویی شما ذخیره شد",
                                 reply_markup=kb_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="ورودی نا معتبر است",
                                 reply_markup=kb_markup)


def videoCalBack(update, context):
    print(update.message)
    if update.effective_chat.type == 'group' and update.effective_chat.title == 'ApBotEchoChat':
        sendMessageToAllUser(update, context, users_list, "VIDEO")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="این فرمت پشتیبانی نمی شود",
                                 reply_markup=kb_markup)


def sendMessageToAllUser(update, context, users_list, type='TEXT'):
    for user in users_list:
        if int(user[4]) > 0:
            if type == 'DOC':
                context.bot.send_document(chat_id=user[4], document=update.message.document.file_id,
                                          caption=update.message.caption, reply_markup=kb_markup)
            elif type == 'IMAGE':
                context.bot.send_photo(chat_id=user[4], photo=update.message.photo[1], caption=update.message.caption
                                       , reply_markup=kb_markup)
            elif type == 'VIDEO':
                context.bot.send_video(chat_id=user[4], video=update.message.video.file_id,
                                       caption=update.message.caption, reply_markup=kb_markup)
            else:
                context.bot.send_message(chat_id=user[4], text=update.message.text, reply_markup=kb_markup)


def getUserIdFromCharId(chat_id):
    for user in users_list:
        if user[4] == str(chat_id):
            print(user[4])
            return user[0]


def getFileId(text, user_id):
    print(file_list)
    for file in file_list:
        if file[3] == user_id:
            if text == file[1]:
                return file[2]


def isClassFIleName(text):
    for class_file in class_file_list:
        if class_file[2] == text:
            return True
    return False


def getClassFileId(text):
    for f in class_file_list:
        if text == f[2]:
            return f[3]


def isFileName(text, user_id):
    for file in file_list:
        if file[3] == user_id:
            if text == file[1]:
                return True
    return False


TOKEN = '1250087938:AAHzRycLJu1G2QUTE7O6a_bGfFDhFkswFsc'
FILE_PATH = "files"
GET_MY_FILE_TEXT = 'فایل های تحویلی من'
GET_CLASS_VIDEO = 'دریافت جلسات کلاس'
BACK_TEXT = "بازگشت"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='log.log')

start_handler = cmdHandler('start', start)
dispatcher.add_handler(start_handler)
caps_handler = cmdHandler('caps', caps)
dispatcher.add_handler(caps_handler)
help_handler = cmdHandler('help', helpHandler)
dispatcher.add_handler(help_handler)
student_number_handler = cmdHandler('studentnum', handleStudentNumberCallBack)
dispatcher.add_handler(student_number_handler)
echoImage_handler = MessageHandler(Filters.photo & (~Filters.command), echoImage)
dispatcher.add_handler(echoImage_handler)
otherFile_handler = MessageHandler(Filters.document, DocumentCallBack)
dispatcher.add_handler(otherFile_handler)
video_file_handler = MessageHandler(Filters.video, videoCalBack)
dispatcher.add_handler(video_file_handler)
echoText_handler = MessageHandler(Filters.text, handleTextMessage)
dispatcher.add_handler(echoText_handler)
updater.start_polling()

# CSV file created if not exist
if not os.path.isfile('comment/comments.csv'):
    print("Create CSV")
    Path("comment").mkdir(parents=True, exist_ok=True)
    with open('comment/comments.csv', mode='w', newline='') as csv_file:
        fieldnames = ['First_Name', 'Last_Name', 'User_Name', 'Message']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    csv_file.close()

bot = tele.Bot(token=TOKEN)
# kb = [[tele.KeyboardButton(GET_MY_FILE_TEXT), tele.KeyboardButton('تست')]]
kb = [[tele.KeyboardButton(GET_MY_FILE_TEXT), tele.KeyboardButton(GET_CLASS_VIDEO)]]
kb_markup = tele.ReplyKeyboardMarkup(kb, resize_keyboard=True)
# Create data base
conn = sqlite3.connect("user.db")
conn.execute('''CREATE TABLE IF NOT EXISTS  USER 
         (ID INTEGER PRIMARY KEY AUTOINCREMENT   NOT NULL,
         FIRST_NAME           TEXT,
         LAST_NAME            TEXT,
         USER_NAME            TEXT,
         CHAT_ID              TEXT unique , 
         STUDENT_NUMBER   TEXT NULLABLE );''')
conn.execute('''CREATE TABLE IF NOT EXISTS FILE 
            (ID INTEGER  PRIMARY KEY AUTOINCREMENT   NOT NULL,
            FILE_NAME       TEXT, 
            FILE_ID         TEXT,
            USER_ID         INTEGER NOT NULL, 
                FOREIGN KEY(USER_ID) REFERENCES USER(ID) 
                ON UPDATE CASCADE 
                ON DELETE CASCADE);''')
conn.execute('''CREATE TABLE IF NOT EXISTS CLASS_FILE 
            (ID INTEGER  PRIMARY KEY AUTOINCREMENT   NOT NULL,
            CHAT_ID         TEXT,
            FILE_NAME       TEXT, 
            FILE_ID         TEXT,
            CAPTION         TEXT,
            FILE_SIZE       TEXT
            );''')

cursor = conn.execute("SELECT * FROM USER")
users_list = cursor.fetchall()
cursor.close()
file_cursor = conn.execute("SELECT * FROM FILE")
file_list = file_cursor.fetchall()
file_cursor.close()
class_file_list_courser = conn.execute("SELECT * FROM CLASS_FILE")
class_file_list = class_file_list_courser.fetchall()
class_file_list_courser.close()
print(conn.execute(f"SELECT ID FROM USER WHERE CHAT_ID='244106511'").fetchall())
conn.close()

keyboard_button_arrays = []
if len(class_file_list) > 0:
    for file in class_file_list:
        keyboard_button_arrays.append([tele.KeyboardButton(file[2])])
    if len(keyboard_button_arrays) > 0:
        keyboard_button_arrays.append([BACK_TEXT])
        keyboard_button_class_file = tele.ReplyKeyboardMarkup(keyboard_button_arrays,
                                                              resize_keyboard=True)

