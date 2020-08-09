# Khatm al-Quran bot
a telegram bot to manage khatm al-quran

## How to Run

you need Python 3.7.0 and above to run the script.

Use commands below to install vital libraries :

```bash
$ pip install python-telegram-bot --upgrade
```

In the script, change the [line 228](https://github.com/hatam008/khatm-al-quran-bot/blob/f58b367976402988b608877d4d805f6c173055a8/bot.py#L228) with your token gotten 
from [@BotFather](https://telegram.me/botfather) (described [here](https://core.telegram.org/bots#6-botfather))

You also should add admins id to [line 12](https://github.com/hatam008/khatm-al-quran-bot/blob/f58b367976402988b608877d4d805f6c173055a8/bot.py#L12) in the list. Ids can be found in [UserInfoBot](https://t.me/userinfobot).

Now run the script :)

## Guide for Admins
To add a new 'khatm' an admin should send this command to bot :
```
/add_khatm <a name for khatm>
```
To remove a 'khatm' an admin should send this command to bot :
```
/delete_khatm <name of the khatm>
```
Admins can also see all khatms and how many pages on each is read by command :
```
/show_all
```
