# -*- coding: utf-8 -*-
from commands.command import MuxAccountCommand
from evennia.utils import utils
import time


class CmdQuit(MuxAccountCommand):
    """
    Gracefully disconnect your current session and send optional
    quit reason message to your other sessions, if any.
    Usage:
      quit [reason]
    Switches:
    /all      disconnect from all sessions.
    /boot     disconnect all other sessions. (Same as @bootme)
    /home     go home, first. (same as qhome)
    """
    key = 'quit'
    aliases = ['bye', 'disconnect', 'qhome', '@bootme']
    locks = 'cmd:all()'
    arg_regex = r'^/|\s|$'
    options = ('all', 'home', 'boot')

    def func(self):
        """hook function"""
        account = self.account
        bye = '|RDisconnecting|n'
        exit_msg = 'Hope to see you again, soon!' \
                   '|/A survey is available at https://goo.gl/forms/yCyLpF6JsAhhUgGz2 for your thoughts'
        cmd = self.cmdstring
        opt = self.switches
        char = self.character
        here = char.location
        sess = self.session
        if 'qhome' in cmd or 'home' in opt and char and here:  # Go home before quitting.
            char.execute_cmd('home')
        reason = self.args.strip() + '(Quitting)'
        if reason:
            bye += " ( |w%s|n ) " % reason
        boot = ('bootme' in cmd) or 'boot' in opt
        if 'all' in opt or boot:
            for session in account.sessions.all():
                if boot:
                    if session is sess:
                        continue  # Exclude booting current session
                    else:  # and boot the rest.
                        session.msg(exit_msg + reason + '/BOOT', session=sesssion)
                        account.disconnect_session_from_account(session, reason + '/BOOT')
                else:  # Disconnect them all!
                    session.msg(exit_msg, session=session)
                    account.disconnect_session_from_account(session, reason + '/ALL')
            if boot:
                sess.msg(bye + 'all other sessions. |gThis session remains connected.|n')
        else:
            session_count = len(account.sessions.all())
            online = utils.time_format(time.time() - sess.conn_time, 1)
            if session_count == 2:
                msg = bye
                others = [x for x in self.account.sessions.get() if x is not sess]
                sess.msg(msg + 'after ' + online + ' online.', session=sess)
                sess.msg(msg + 'your other session. |gThis session remains connected.|n', session=others)
            elif session_count > 2:
                msg = bye + "%i sessions are still connected."
                sess.msg(msg % (session_count - 1))
            else:
                # If quitting the last available session, give connect time.
                msg = bye + 'after ' + online + ' online. '
                sess.msg(msg, session=sess)
            sess.msg(exit_msg, session=sess)
            account.disconnect_session_from_account(sess, reason)
