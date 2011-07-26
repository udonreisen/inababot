# logic.py
#

from controls import *
from commands import *

controls_list = {
    'muc'        : MUCControl,
}

commands_list = {'!infa': InfaCommand,
                 '!help': HelpCommand,
                 '!memb': MembCommand,
                 '!part': PartCommand,
                 '!ping': PingCommand,
}

admin_commands_list = {
#    '!ban'      : BanCommand,
#    '!devoice'  : DevoiceCommand,
#    '!kick'     : KickCommand
}