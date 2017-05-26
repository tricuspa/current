# -*- coding: UTF-8 -*-
import time
from commands.command import MuxPlayerCommand
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import ansi, utils, create, search, evtable


class CmdWho(MuxPlayerCommand):
    """
    Shows who is currently online.
    Usage:
      who    - basic view
      where  - includes location
      what   - includes doing
      ws     - includes species
      wa     - same as 'where'
    """
    key = 'who'
    aliases = ['ws', 'where', 'wa', 'what', 'wot']
    locks = 'cmd:all()'

    def func(self):
        """Get all connected players by polling session."""
        you = self.player
        session_list = SESSIONS.get_sessions()
        cmd = self.cmdstring
        show_session_data = you.check_permstring('Immortals') and not you.attributes.has('_quell')
        player_count = (SESSIONS.player_count())
        table = evtable.EvTable(border='none', pad_width=0, border_width=0, maxwidth=79)
        if cmd == 'wa' or cmd == 'where':
            table.add_header('|wCharacter', '|wOn for', '|wIdle', '|wLocation')
            table.reformat_column(0, width=40, align='l')
            table.reformat_column(1, width=8, align='l')
            table.reformat_column(2, width=7, pad_right=1, align='r')
            table.reformat_column(3, width=25, align='l')
            for session in session_list:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                character = session.get_puppet()
                here = character.location if character else None
                location = here.get_display_name(you) if character and here else '|222Nothingness|n'
                table.add_row(character.get_display_name(you) if character else '- Unknown -',
                              utils.time_format(delta_conn, 0), utils.time_format(delta_cmd, 1), location)
        elif cmd == 'ws':
            my_character = self.caller.get_puppet(self.session)
            if not (my_character and my_character.location):
                self.msg("You can't see anyone here.")
                return
            table.add_header('|wCharacter', '|wOn for', '|wIdle')
            table.reformat_column(0, width=45, align='l')
            table.reformat_column(1, width=8, align='l')
            table.reformat_column(2, width=7, pad_right=1, align='r')
            for session in session_list:
                character = session.get_puppet()
                if not session.logged_in or not character or character.location != my_character.location:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                character = session.get_puppet()
                species = '-masked-' if my_character.location.tags.get('rp', category='flags') and character.db.\
                    unmasked_sdesc else character.attributes.get('species', default='*ghost*')
                table.add_row((character.get_display_name(you) if character else '*ghost*') + ', ' + species,
                              utils.time_format(delta_conn, 0), utils.time_format(delta_cmd, 1))
        elif cmd == 'what' or cmd == 'wot':
            table.add_header('|wCharacter  - Doing', '|wIdle')
            table.reformat_column(0, width=72, align='l')
            table.reformat_column(1, width=7, align='r')
            for session in session_list:
                if not session.logged_in or not session.get_puppet():
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                character = session.get_puppet()
                doing = character.get_display_name(you, pose=True)
                table.add_row(doing, utils.time_format(delta_cmd, 1))
        else:  # Default to displaying who
            if show_session_data:  # privileged info shown to Immortals and higher only when not quelled
                table.add_header('|wCharacter', '|wPlayer', '|wQuell', '|wCmds', '|wProtocol', '|wAddress')
                table.reformat_column(0, align='l')
                table.reformat_column(1, align='r')
                table.reformat_column(2, width=7, align='r')
                table.reformat_column(3, width=6, pad_right=1, align='r')
                table.reformat_column(4, width=11, align='l')
                table.reformat_column(5, width=16, align='r')
                session_list = sorted(session_list, key=lambda o: o.player.key)
                for session in session_list:
                    if not session.logged_in:
                        continue
                    player = session.get_player()
                    puppet = session.get_puppet()
                    table.add_row(puppet.get_display_name(you) if puppet else 'None',
                                  player.get_display_name(you),
                                  '|gYes|n' if player.attributes.get('_quell') else '|rNo|n',
                                  session.cmd_total, session.protocol_key,
                                  isinstance(session.address, tuple) and session.address[0] or session.address)
            else:  # unprivileged info shown to everyone, including Immortals and higher when quelled
                table.add_header('|wCharacter', '|wOn for', '|wIdle')
                table.reformat_column(0, width=40, align='l')
                table.reformat_column(1, width=8, align='l')
                table.reformat_column(2, width=7, align='r')
                for session in session_list:
                    if not session.logged_in:
                        continue
                    delta_cmd = time.time() - session.cmd_last_visible
                    delta_conn = time.time() - session.conn_time
                    character = session.get_puppet()
                    table.add_row(character.get_display_name(you) if character else '- Unknown -',
                                  utils.time_format(delta_conn, 0), utils.time_format(delta_cmd, 1))
        is_one = player_count == 1
        string = '%s' % 'A' if is_one else str(player_count)
        string += ' single ' if is_one else ' unique '
        plural = ' is' if is_one else 's are'
        string += 'account%s logged in.' % plural
        self.msg(table)
        self.msg(string)
