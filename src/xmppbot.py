# xmppbot.py
#

import time
import random
from threading import Thread

import sleekxmpp
from xml.etree import cElementTree

from storage import Storage
import logic

# Класс бота
class XmppBot:
    def __init__(self, jid, password, owner):
        self.xmpp = sleekxmpp.ClientXMPP(jid, password)
        self.xmpp.registerPlugin('xep_0030')
        self.xmpp.registerPlugin('xep_0045')
        self.xmpp.registerPlugin('xep_0199', {'keepalive': True,
                                              'frequency': 120,
                                              'timeout'  : 30})
        self.xmpp.add_event_handler('session_start', self.handleXMPPConnected)
        self.xmpp.add_event_handler('message', self.handleIncomingMessage)
        self.xmpp.add_event_handler('groupchat_message', self.handleIncomingGroupMessage)
        self.xmpp.add_event_handler('groupchat_presence', self.handleIncomingGroupPresence)
        self.storage = Storage()
        self.myNicks = {}
        self.users = {}
        self.online = False
        self.watch = 0
        self.moderators = {}
        self.commands = logic.commands_list
        self.controls = logic.controls_list
        self.urls = []

    # Запуск бота
    def run(self):
        self.xmpp.connect()
        self.xmpp.process(threaded=False)

    # Обработчик события подключения к серверу
    def handleXMPPConnected(self, event):
        self.xmpp.sendPresence(ppriority=99, pshow='chat')
        for muc in self.storage.getAutoMUC():
            self.myNicks[muc.jid] = muc.nick
            self.joinMUC(muc.jid, muc.nick)
            self.users[muc.jid] = {}
            self.moderators[muc.jid] = []
        if not self.online:
            self.online = True
            self.hello()

    # Обработка статусных сообщений
    def handleIncomingGroupPresence(self, presence):
        room = presence['muc']['room']
        nick = presence['muc']['nick']
        affiliation = presence['muc']['affiliation']
        role = presence['muc']['role']
        jid = presence['muc']['jid'].bare
        type = presence['muc']['type']
        roster= self.xmpp.plugin['xep_0045'].getRoster(room)
        self.storage.checkNick(nick)
        if jid != '' and role == 'visitor':
            bannedStrings = ['_','(',')','0','1','2','3','4','5','6','7','8','9']
            isBot = 0
            for string in bannedStrings:
                isBot += nick.count(string)
                isBot += jid.count(string)
            if isBot > 1:
                self.kick(room, nick, 'Да ты же, сука, бот!')
                return
            if affiliation in ['owner', 'admin']:
                self.storage.checkJid(jid, True)
            elif affiliation == 'member':
                self.storage.checkJid(jid)
            elif role == 'visitor':
                avoice= Thread(target=self.autoVoice, args=(room, nick))
                avoice.start()
            if role == 'moderator' and not nick in self.moderators:
                self.moderators[room].append(nick)
        if not type == 'unavailable':
            self.users[room][nick] = {'jid': jid, 'affiliation': affiliation}
        else:
            del self.users[room][nick]
        for mod in self.moderators[room]:
            if mod not in roster: self.moderators[room].remove(mod)

    # Обработка сообщений в чатах
    def handleIncomingGroupMessage(self, message):
        room = message['mucroom']
        nick = message['mucnick']
        text = message['body']
        print('{0}/{1}: {2}'.format(room, nick, text))
        if nick:
            jid = self.users[room][nick]['jid']
            self.storage.addMessage(room, jid, nick, text)
            if nick != self.myNicks[room]:
                reply = logic.textHandle(nick, self.myNicks[room], text)
                if reply: self.sayInMUC(room, reply)
        if text.startswith('!'):
            if text in logic.commands_list:
                comm = Thread(target=logic.commands_list[text](self), args=(room, nick))
            elif text.count(' ') > 0:
                command = text.split(' ', 1)[0]
                argstring = text.split(' ', 1)[1]
                if command in logic.commands_list:
                    comm = Thread(target=logic.commands_list[command](self), args=(room, nick, argstring))
                else:
                    comm = Thread(target=logic.commands_list['!help'](self), args=(room, nick))
            else:
                comm = Thread(target=logic.commands_list['!help'](self), args=(room, nick))
            comm.start()

    # Обработка сообщений
    def handleIncomingMessage(self, message):
        jid = message['from'].bare
        text = message['body']
        user = self.storage.getJid(jid)
        if user is not None:
            if text.startswith(tuple(logic.controls_list)):
                if text.count(' ') > 0:
                    command = text.split(' ', 1)
                    logic.controls_list[command[0]](self)(user, command[1])
                elif text in logic.controls_list:
                    logic.controls_list[text](self)(user)

    # Подключение к конференции
    def joinMUC(self, room, nick):
        self.xmpp.plugin['xep_0045'].joinMUC(room, nick,  pshow='chat')

    # Отправляет сообщение в конференцию
    def sayInMUC(self, room, text):
        self.xmpp.sendMessage(room, text, mtype='groupchat')

    # Приветствие
    def hello(self):
        time.sleep(5)
        members = ['бетманы', 'няшки', 'омичи']
        asks = ['всё няшитесь', 'всё ругаетесь', 'всё спите','всё упарываетесь']
        for room in self.xmpp.plugin['xep_0045'].get_joined_rooms():
            text = 'Ну что вы, {0}, {1}?'.format(random.choice(members), random.choice(asks))
            self.sayInMUC(room, text)

    # Даёт голос гостям
    def autoVoice(self, room, nick):
        query = cElementTree.Element('{http://jabber.org/protocol/muc#admin}query')
        item = cElementTree.Element('item', {'role':'participant', 'nick':nick})
        query.append(item)
        iq = self.xmpp.makeIqSet(query)
        iq['to'] = room
        time.sleep(15)
        if iq.send():
            reply = 'Привет, {0}. Если хочешь стать постоянным участником, то отправь команду !memb в чат. Команда !help покажет остальные команды.'.format(nick)
            self.sayInMUC(room, reply)

    # Автокик
    def kick(self, room, nick, kickreason=None):
        query = cElementTree.Element('{http://jabber.org/protocol/muc#admin}query')
        item = cElementTree.Element('item', {'role':'none', 'nick':nick})
        if kickreason is not None:
            reason = cElementTree.Element('reason')
            reason.text = kickreason
            item.append(reason)
        query.append(item)
        iq = self.xmpp.makeIqSet(query)
        iq['to'] = room
        result = iq.send()
