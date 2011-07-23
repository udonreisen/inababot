# controls.py
#

class Control(object):
    def __init__(self, bot):
        self.bot = bot
    def __call__(self):
        raise(ValueError, 'This is an abstract method!')
    def say(self, jid, text):
        self.bot.xmpp.sendMessage(jid, text, mtype='chat')


# Команда подключения бота к конференции
class MUCControl(Control):
    def __call__(self, user, argstring=None):
        if user.admin:
            if argstring is None or argstring.startswith('help'):
                self.say(user.jid, self.help())
            elif argstring.startswith('add '):
                args = argstring.split(' ', 2)
                print (args)
                muc = self.bot.storage.addMUC(args[1], args[2], True, True)
                if muc:
                    self.say(user.jid,
                        'Такая конференция уже есть. '
                        'ID: %s, JID: %s, Ник бота: %s. '
                        'Для измения — set, для — удаления rm.'
                        % (muc.id, muc.jid, muc.nick))
                else:
                    self.say(user.jid, 'Конференция успешно добавлена.')
            elif argstring.startswith('join '):
                args = argstring.split(' ', 1)
                if args[1].isdigit():
                    muc = self.bot.storage.getMUC(int(args[1]))
                    if muc is not None:
                        self.bot.joinMUC(muc.jid, muc.nick)
                else:
                    muc = args[1].split(' ', 1)
                    self.bot.joinMUC(muc[0], muc[1])
            elif argstring.startswith('set '):
                args = argstring.split(' ', 2)
                if args[1].isdigit():
                    muc = self.bot.storage.getMUC(int(args[1]))
                    if muc is not None:
                        if args[2] == 'private':
                            self.bot.storage.setPublicMUC(muc.id, public=False)
    def help(self):
        return '''Управление подключением к конференциям.

Доступны только администраторам:
muc add room@conference.jabber.srv Ник — добавить конференцию
muc join ID — подключится к конференции'''
