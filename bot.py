from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Updater, Filters, PicklePersistence
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction
from functools import wraps
import logging
import threading
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

LIST_OF_ADMINS = [] # id of admins should be added to this list

# sychronize decorator
def synchronized(wrapped):
    lock = threading.Lock()
    @wraps(wrapped)
    def _wrap(*args, **kwargs):
        with lock:
            return wrapped(*args, **kwargs)
    return _wrap

# decorator to restrict some commands that they can be accessible only for admins
def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            context.bot.send_message(chat_id=update.effective_chat.id, text = "Access Denied :(")
            return
        return func(update, context, *args, **kwargs)
    return wrapped

# This function will be used as a decorator for calback functions
def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

# typing... action in bot
send_typing = send_action(ChatAction.TYPING)

#Conversation stages
COUNT, CHOOSE = range(2)

#Admin stages
_ADMIN_, _ADD_, _REMOVE_ = range(3)

#create keyboard from itrable strings
def create_keyboard(names): return [[name] for name in names]

@send_typing
def start(update,context):
    bot_data_key = context.bot_data
    if 'khatms' in bot_data_key:
        if len(context.bot_data['khatms']) != 0 :
            keyboard = create_keyboard(context.bot_data['khatms'].keys())
            reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
            reply_text = "سلام ، به ربات ختم قرآن کریم خوش آمدید. \n از میان ختم های موجود یکی را انتخاب کنید."
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup=reply_markup)
            return CHOOSE
    reply_text = "سلام ، به ربات ختم قرآن کریم خوش آمدید. \n متاسفانه ختمی موجود نیست."
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
    return ConversationHandler.END

@send_typing
def choose(update,context):
    text = update.message.text
    if text in context.bot_data['khatms'].keys():
        context.user_data['choice'] = text
        reply_markup = ReplyKeyboardMarkup([["بازگشت"]],resize_keyboard=True)
        reply_text = "تعداد صفخات مورد نظر را وارد کنید : "
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup= reply_markup)
        return COUNT
    else:
        reply_text = "چنین ختمی وجود ندارد. از گزینه های پایین یکی را انتخاب کنید : "
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
        return CHOOSE

# function to show numbers that should be read
@send_typing
def choose_count(update,context):
    name = context.user_data['choice']
    count = int(update.message.text)
    if count == 0:
        reply_text = "التماس دعا :)"
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text,reply_markup= ReplyKeyboardRemove())
        return ConversationHandler.END
    else :
        khatms = context.bot_data['khatms']
        pages = get_pages(name,count,khatms)
        if pages[1] == -1:
            keyboard = create_keyboard(context.bot_data['khatms'].keys())
            reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
            reply_text = f"ختم مورد نظر از دسترس خارج شده است"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text,reply_markup=reply_markup)
            return CHOOSE
        elif pages[1] == 605:
            keyboard = create_keyboard(context.bot_data['khatms'].keys())
            reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
            reply_text = f"ختم مورد نظر به پایان رسیده است"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text,reply_markup=reply_markup)
            return CHOOSE
        else:
            reply_text = f"شما باید از صفحه {pages[0]} تا صفحه {pages[1]} را مطالعه کنید؛ \nالتماس دعا."
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text,reply_markup= ReplyKeyboardRemove())
            return ConversationHandler.END

# synchronized function that calculate number of ages should be read
@synchronized
def get_pages(name,count,khatms):
    if name in khatms.keys():
        current = khatms[name]
        if current == 604 :
            return (604,605)
        elif current + count > 604:
            khatms.update({name:604})
            return (current + 1,604)
        else:
            khatms.update({name:current + count})
            return (current + 1,current + count)
    else:
        return (-1,-1)

# exit command handler
@send_typing
def exit(update,context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    reply_text = "التماس دعا"
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup= ReplyKeyboardRemove())
    return ConversationHandler.END

# back function in COUNT stage
@send_typing
def back(update,context):
    bot_data_key = context.bot_data
    if 'khatms' in bot_data_key:
        keyboard = create_keyboard(context.bot_data['khatms'].keys())
        reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
        reply_text = "از میان ختم های موجود یکی را انتخاب کنید."
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup=reply_markup)
        return CHOOSE
    else:
        reply_text = "متاسفانه ختمی موجود نیست."
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
        return ConversationHandler.END

# unknown khatm name in CHOOSE stage
@send_typing
def unknown_khatm(update,context):
    reply_text = "داده نامعتبر! از میان ختم های زیر یکی را انتخاب کنید : "
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
    return CHOOSE

# unknown type of input for COUNT stage
@send_typing
def unknown_count(update,context):
    reply_text = "داده نامعتبر! عددی بین 1 تا 604 انتخاب کنید : "
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
    return COUNT

# function that admin can add khatm
@send_typing
@restricted
def add_khatm(update, context):
    name = update.message.text
    if name == "Back" :
        return admin_back(update,context)

    bot_data = context.bot_data
    if 'khatms' in bot_data.keys():
        khatm_data = bot_data['khatms']
        if name in khatm_data.keys():
            reply_text = "This khatm already exists!\nTry another time ..."
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
            return _ADD_
        else:
            khatm_data.update({name :0})
            reply_text = "Successfuly added!"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
            return admin_back(update,context)
    else:
        bot_data['khatms'] = {name: 0}
        reply_text = "Successfuly added!"
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
        return admin_back(update,context)

# function that admin delete a khatm
@send_typing
@restricted
def delete_khatm(update,context):
    name = update.message.text
    if name == "Back" :
        return admin_back(update,context)
    bot_data = context.bot_data
    if 'khatms' in bot_data.keys():
        khatm_data = bot_data['khatms']
        if name in khatm_data.keys():
            khatm_data.pop(name)
            reply_text = "Successfuly removed!"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
            return admin_back(update,context)
        else:
            reply_text = "No khatm exist with this name\nSelect One Option Below"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
            return _REMOVE_
    else:
        reply_text = "No khatm exist with this name\nSelect One Option Below"
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
        return _REMOVE_

def create_khatms_list(khatm_data):
    reply = ""
    for name,page in khatm_data.items():
        reply += f"{name} read til page {page}\n"
    reply += "\n\n"
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    reply += dt_string
    return reply

# function to show all khatms to admins
def show_all_khatms(update,context):
    bot_data = context.bot_data
    if 'khatms' in bot_data.keys():
        khatm_data = bot_data['khatms']
        reply_text = create_khatms_list(khatm_data)
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
    else:
        reply_text = "No khatm added yet"
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)

@send_typing
@restricted
def admin(update, context):
    reply_text = "Welcome Admin :)\nSelect one option below or /exit"
    reply_keyboard = [["Add","Remove"],["Show all Khatms\' info"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text,reply_markup= reply_markup)
    return _ADMIN_

@send_typing
@restricted
def admin_choose(update, context):
    text = update.message.text
    if text == "Add":
        admin_add_message(update,context)
        return _ADD_
    elif text == "Remove":
        return admin_remove_message(update, context)
    elif text == "Show all Khatms\' info":
        show_all_khatms(update,context)
        return _ADMIN_

def admin_add_message(update,context):
    reply_text = "Enter a name for the new khatm :"
    reply_keyboard = [["Back"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text,reply_markup= reply_markup)

def admin_remove_message(update, context):
    return admin_khatm_keyboard(update, context, _REMOVE_)
    
def admin_khatm_keyboard(update, context, mode):
    bot_data_key = context.bot_data
    if 'khatms' in bot_data_key:
        if len(context.bot_data['khatms']) != 0 :
            keyboard = create_keyboard(context.bot_data['khatms'].keys())
            keyboard.append(["Back"])
            reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
            reply_text = "Select a khatm below :"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup= reply_markup)
            return mode
        else :
            reply_text = "No khatm added yet"
            context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
            return admin_back(update, context)
    else:
        reply_text = "No khatm added yet"
        context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
        return admin_back(update, context)

def admin_back(update,context):
    reply_text = "Select one option below or /exit :"
    reply_keyboard = [["Add","Remove"],["Show all Khatms\' info"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup= reply_markup)
    return _ADMIN_

@send_typing
@restricted
def admin_exit(update, context):
    reply_text = "See ya soon :)"
    context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text, reply_markup= ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    token = "yor token" # Your bot token should be placed here
    persistent = PicklePersistence("db") # it automaticly will generate a db that contains bot data
    updater = Updater(token= token,use_context= True,persistence=persistent)
    dispacher = updater.dispatcher

    conversation = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            CHOOSE : [MessageHandler(Filters.text & ~Filters.command,choose),MessageHandler(~Filters.command,unknown_khatm)],
            COUNT : [MessageHandler(Filters.regex('^([0-5]?[0-9]?[0-9]|60[0-4])$'),choose_count),MessageHandler(Filters.regex('^بازگشت$'),back),CommandHandler('back',back),MessageHandler(Filters.all,unknown_count)]
        },
        fallbacks= [CommandHandler('exit',exit),MessageHandler(Filters.regex('^خروج$'),exit)]
    )
    dispacher.add_handler(conversation)

    adminConversation = ConversationHandler(
        entry_points=[CommandHandler('admin',admin)],
        states={
            _ADMIN_: [MessageHandler(Filters.regex('^Add|Remove|Show all Khatms\' info$'),admin_choose)],
            _ADD_: [MessageHandler(Filters.text,add_khatm)],
            _REMOVE_: [MessageHandler(Filters.text,delete_khatm)]
        },
        fallbacks=[CommandHandler('exit',admin_exit)]
    )
    dispacher.add_handler(adminConversation)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()