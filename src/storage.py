# storage.py
#

import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
Base = declarative_base()

# Класс для прозрачной работы с БД
class Storage(object):
    def __init__(self):
        self.engine = create_engine('sqlite:///database.sqlite', echo=False)
        Session.configure(bind=self.engine)
        self.metadata = Base.metadata
        self.metadata.create_all(self.engine)

# Конференции
    def addMUC(self, jid, nick, public, auto):
        session = Session()
        muc = session.query(MUC).filter(MUC.jid == jid).first()
        if muc is None:
            muc = MUC(jid, nick, public, auto)
            session.add(muc)
            session.commit()
            session.close()
            return
        session.close()
        return muc
    def getMUC(self, muc_id):
        session = Session()
        muc = session.query(MUC).filter(MUC.id == muc_id).first()
        session.close()
        return muc
    def getMUConJID(self, muc_jid):
        session = Session()
        muc = session.query(MUC).filter(MUC.jid == muc_jid).first()
        session.close()
        return muc
    def getPublicMUC(self, public=True):
        session = Session()
        mucs = session.query(MUC).filter(MUC.public == public).all()
        session.close()
        return mucs
    def getAutoMUC(self, auto=True):
        session = Session()
        mucs = session.query(MUC).filter(MUC.auto == auto).all()
        session.close()
        return mucs
    def setPublicMUC(self, muc_id, public=True):
        session = Session()
        muc = session.query(MUC).filter(MUC.id == muc_id).first()
        muc.public = public
        session.add(muc)
        session.commit()
        session.close()

# Пользователи
    def checkJid(self, jid, admin=False):
        session = Session()
        jid = jid.lower()
        user = session.query(Jid).filter(Jid.jid == jid).first()
        if user is None:
            user = Jid(jid)
            session.add(user)
        user.admin = admin
        session.commit()
        session.close()
        return user
    def getJid(self, jid):
        session = Session()
        user = session.query(Jid).filter(Jid.jid == jid).first()
        session.close()
        return user
    def getJidFromID(self, uid):
        session = Session()
        user = session.query(Jid).filter(Jid.id == uid).first()
        session.close()
        return user
    def checkNick(self, nick):
        session = Session()
        user = session.query(Nick).filter(Nick.nick == nick).first()
        if user is None:
            user = Nick(nick)
            session.add(user)
        session.commit()
        session.close()
        return user

#Сообщения
    def addMessage(self, room, ijid, inick, message):
        session = Session()
        jid = session.query(Jid).filter(Jid.jid == ijid).first()
        if jid is None:
            jid = Jid(ijid)
            session.add(jid)
            session.commit()
        nick = session.query(Nick).filter(Nick.nick == inick).first()
        if jid is None:
            user = Nick(inick)
            session.add(jid)
        muc = session.query(MUC).filter(MUC.jid == room).first()
        if muc is not None:
            msg = Message(jid.id, muc.id, nick.id, message)
            session.add(msg)
            session.commit()
        session.close()

# Фильмы
    def currTime(self):
        session = Session()
        settings = session.query(Settings).one()
        return settings.date
    def currFilm(self):
        session = Session()
        settings = session.query(Settings).one()
        if settings is not None:
            film = session.query(Film).filter(Film.id == settings.film).first()
        session.close()
        return film
    def listFilms(self, all):
        session = Session()
        films = []
        for film in session.query(Film).order_by(Film.id):
            if film.roll or all:
                films.append('{0}. «{1}»'.format(film.id, film.title))
        session.close()
        return films
    def addFilm(self, title):
        session = Session()
        film = session.query(Film).filter(Film.title == title).first()
        if film is None:
            film = Film(title, 0, True)
            session.add(film)
            session.commit()
            session.close()
            return True
        else:
            return False
    def switchFilm(self, id, roll):
        session = Session()
        film = session.query(Film).filter(Film.id == id).first()
        if film is not None:
            film.roll = roll
            session.commit()
        return film.title
    def remFilm(self, id):
        session = Session()
        film = session.query(Film).filter(Film.id == id).first()
        if film is not None:
            title = film.title
            session.delete(film)
            session.commit()
            return title
        else:
            return False
#Класс описывающий участника
class Jid(Base):
    __tablename__ = 'jids'
    id = Column(Integer, primary_key=True)
    jid = Column(String)
    admin = Column(Boolean)
    alerts = Column(Boolean)
    def __init__(self, jid):
        self.jid = jid
        self.admin = False
        self.alerts = False
class Nick(Base):
    __tablename__ = 'nicks'
    id = Column(Integer, primary_key=True)
    nick = Column(String)
    def __init__(self, nick):
        self.nick = nick
# Список конференций
class MUC(Base):
    __tablename__ = 'mucs'
    id = Column(Integer, primary_key=True)
    jid = Column(String)
    nick = Column(String)
    public = Column(Boolean)
    auto = Column(Boolean)
    def __init__(self, jid, nick, public, auto):
        self.jid = jid
        self.nick = nick
        self.public = public
        self.auto = auto
# Класс описывающий запись в логе
class Message(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    jid = Column(Integer, ForeignKey('jids.id'))
    muc = Column(Integer, ForeignKey('mucs.id'))
    nick = Column(Integer, ForeignKey('nicks.id'))
    message = Column(String)
    def __init__(self, jid, muc, nick, message):
        self.date = datetime.datetime.now()
        self.jid = jid
        self.muc = muc
        self.nick = nick
        self.message = message
# Список фильмов
class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    count = Column(Integer)
    roll = Column(Boolean)
    def __init__(self, title, count, roll):
        self.title = title
        self.count = count
        self.roll = roll
# Настройки бота
class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    film = Column(Integer)
    def __init__(self, data):
        self.data = data
