# logic.py
#

import re

from controls import *
from commands import *

controls_list = {
    'muc'        : MUCControl,
}

commands_list = {'!film' : FilmCommand,
                 '!infa' : InfaCommand,
                 '!help' : HelpCommand,
                 '!memb' : MembCommand,
                 '!part' : PartCommand,
                 '!ping' : PingCommand,
                 '!roll' : RollCommand,
                 '!start': StartCommand,
                 '!stop' : StopCommand
}

controls_pm_list = {
    'say'        : SayControl,
}

admin_commands_list = {
#    '!ban'      : BanCommand,
#    '!devoice'  : DevoiceCommand,
#    '!kick'     : KickCommand
}

def textHandle(nick, my_nick, text):
    return
