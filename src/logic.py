# logic.py
#

from controls import *
from commands import *

controls_list = {
    'muc'        : MUCControl,
}

commands_list = {
    '!film'     : FilmCommand,
    '!help'     : HelpCommand,
    '!memb'     : MembCommand,
    '!part'     : PartCommand,
    '!ping'     : PingCommand,
    '!roll'     : RollCommand
}

admin_commands_list = {
#    '!ban'      : BanCommand,
#    '!devoice'  : DevoiceCommand,
#    '!kick'     : KickCommand
}