# commands.py
#

import random
import time
from xml.etree import cElementTree

angry = False

class Command(object):
    def __init__(self, bot):
        self.bot = bot
        random.seed()
    def __call__(self):
        raise(ValueError, 'This is an abstract method!')

    def say(self, room, text):
        self.bot.xmpp.sendMessage(room, text, mtype='groupchat')

    def getNicksInRoom(self, room):
        return list(self.bot.xmpp.plugin['xep_0045'].getRoster(room))

    def randList(self, rlist):
        return rlist[random.randrange(len(rlist))]

    def percent(self, text):
        text_hash = hashlib.md5()
        text_hash.update(text.encode())
        text_hash = text_hash.hexdigest()[:2]
        result = 0
        for i in range(len(text_hash)):
            if text_hash[i] == 'a':
                num = 10
            elif text_hash[i] == 'b':
                num = 11
            elif text_hash[i] == 'c':
                num = 12
            elif text_hash[i] == 'd':
                num = 13
            elif text_hash[i] == 'e':
                num = 14
            elif text_hash[i] == 'f':
                num = 15
            else:
                num = int(text_hash[i])
            result += num * pow(10, len(text_hash) - i - 1)
        return result % 101

# Возвращает достоверность информации
class InfaCommand(Command):
    def __call__(self, room, nick, argstring=None):
        if argstring is None:
            result = random.randrange(101)
            self.say(room, '{0}: Инфа {1}%'.format(nick, result))
        else:
            result = self.percent(argstring)
            self.say(room, '{0}: {1}, инфа {2}%'.format(nick, argstring, result))

# Выводит список доступных команд
class HelpCommand(Command):
    def __call__(self, room, nick, argstring=None):
        reply = '''{0}: Справка.
!help — данная справка
!memb — делает участника постояным
!part — подсвечивает всех участников в конференци
!ping — pong!
!roll — рулетка с фильмами'''.format(nick)
        self.say(room, reply)

class MembCommand(Command):
    def __call__(self, room, nick, argstring=None):
        if self.bot.users[room][nick]['affiliation'] not in ['owner','admin','member']:
            self.bot.xmpp.plugin['xep_0045'].set_affiliation(room, nick=nick)
            reply = 'Добро пожаловать в нашу секту, {0} :3'.format(nick)
        else:
            reply = '{0}, ты же и так с нами!'.format(nick)
        time.sleep(2)
        self.say(room, reply)

# Хайлайтит всех участников конференции
class PartCommand(Command):
    def __call__(self, room, nick, argstring=None):
        users = sorted(list(self.getNicksInRoom(room)))
        users.remove(self.bot.myNicks[room])
        users.remove(nick)
        reply = '{0}\nВсем проснуться, сейчас {1} говорить будет!'.format(', '.join(users), nick)
        self.say(room, reply)

# Простая команда для проверки
class PingCommand(Command):
    def __call__(self, room, nick, argstring=None):
        jid = self.bot.users[room][nick]['jid']
        delay = self.bot.xmpp.plugin['xep_0199'].send_ping(jid)
        self.say (room, '{0}: pong! Задержка {1} с.'.format(nick, str(delay)[0:5]))

