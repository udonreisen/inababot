# commands.py
#

import random
import time
import hashlib

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

# Команда для фильмов
class FilmCommand(Command):
    def __call__(self,  room, nick, argstring=None):
        if argstring is None or argstring.startswith('help'):
            self.say(room, self.help().format(nick))
        elif argstring.startswith('list'):
            listFilms = []
            for film in list(self.bot.storage.listFilms(True)):
                if film.roll:
                    listFilms.append('{0}. «{1}»'.format(film.id, film.title))
            if listFilms:
                reply = '{0}, список фильмов в рулетке: {1}'.format(nick, ', '.join(listFilms))
            else:
                reply = '{0}, фильмов в рулетке нет.'.format(nick)
            self.say(room, reply)
        elif argstring.startswith('full'):
            listFilms = []
            for film in list(self.bot.storage.listFilms(False)):
                listFilms.append('{0}. «{1}»'.format(film.id, film.title))
            if listFilms:
                reply = '{0}, весь список фильмов: {1}'.format(nick, ', '.join(listFilms))
            else:
                reply = '{0}, фильмов в списке нет.'.format(nick)
            self.say(room, reply)
        elif argstring.startswith('add '):
            if len(argstring) > 4:
                film = argstring.split(' ', 1)[1]
                self.bot.storage.addFilm(film)
                self.say(room, '{0}: Добавлено!'.format(nick))
            else:
                self.say(room, self.help().format(nick))
        elif argstring.startswith('o'):
            if argstring.startswith('on '):
                onRollete = True
                if len(argstring) > 3:
                    filmID = argstring.split(' ', 1)[1]
            elif argstring.startswith('off '):
                onRollete = False
                if len(argstring) > 4:
                    filmID = argstring.split(' ', 1)[1]
            else:
                self.say(room, self.help().format(nick))
                return
            if filmID.isdigit():
                film = self.bot.storage.switchFilm(filmID, onRollete)
                if film:
                    if onRollete:
                        reply = '{0}, фильм «{1}» участвует в рулетке!'.format(nick, film)
                    else:
                        reply = '{0}, фильм «{1}» не участвует в рулетке!'.format(nick, film)
                else:
                    reply = '{0}, неправильный ID!'.format(nick)
                self.say(room, reply)
            else:
                self.say(room, self.help().format(nick))
        elif argstring.startswith('rm '):
            if len(argstring) > 3:
                filmID = argstring.split(' ', 1)[1]
                if filmID.isdigit():
                    film = self.bot.storage.remFilm(filmID)
                    if film:
                        self.say(room, '{0}: «{1}» удалён из базы.'.format(nick, film))
                    else:
                        self.say(room, '{0}: неправильный ID!'.format(nick))
        elif argstring == 'clear':
            if self.bot.storage.clearFilm():
                self.say(room, '{0}: База очищенна.'.format(nick))
            else:
                self.say(room, '{0}: Ошибка!'.format(nick))
        else:
            self.say(room, self.help().format(nick))

    def help(self):
        return '''{0}: Использование:
!film help — данная справка;
!film list — список фильмов участвующих в рулетке;
!film full — полный список фильмов;
!film add Название Фильма — добавить фильм;
!film on ID — добавить фильм с ID в рулетку;
!film off ID — убрать фильм с ID из рулетки;
!film rm ID — удалить фильм с ID из базы;
!film clear — очистить базу.'''

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
!film — работа с базой фильмов, подробности !film help
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
        if self.bot.xmpp.plugin['xep_0199'].send_ping(jid):
            self.say(room, '{0}: pong!'.format(nick))
        else:
            self.say(room, '{0}: No more pongs for you...'.format(nick))

# Команда выбора фильма
class RollCommand(Command):
    def __call__(self, room, nick, argstring=None):
        films = list(self.bot.storage.listFilms(True))
        if films:
            film = self.randList(films)
            title = self.bot.storage.switchFilm(film.id, False)
            reply = '{0}, выбранный фильм: {1}. «{2}»'.format(nick, film.id, title)
        else:
            reply = '{0}, ничего не выбранно!'.format(nick)
        self.say(room, reply)