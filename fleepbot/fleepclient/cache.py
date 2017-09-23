# -*- coding: cp1257 -*-
"""Python Library for Fleep HTTP API.
"""

import json
import logging
import re
import time
from bisect import bisect_left, bisect_right
from lxml import etree

def find_xml_refs(xml):
    rlist = []

    if isinstance(xml, unicode):
        xml = xml.encode('utf8')

    root = etree.fromstring(xml)
    for ref in root.getiterator('file'):
        k = ref.get('key')
        if k:
            rlist.append(k)
    return rlist

from .api import FleepApi

FILE_KEY = "%s-%s"

#
# --- Message ------------------------------------------------------------------------------
#

class Message(object):
    """Message object used in conversation messages collection
    """
    # enumerate fields here for pylint
    message = None
    account_id = None
    mk_message_type = None
    posted_time = None
    flow_message_nr = None
    revision_message_nr = None
    pin_weight = None
    ref_message_nr = None
    edit_account_id = None
    edited_time = None
    lock_account_id = None
    inbox_nr = None
    message_nr = None
    tags = None
    subject = None

    SIMPLE_FIELDS = (
        'message', 'account_id', 'mk_message_type', 'posted_time',
        'flow_message_nr', 'revision_message_nr', 'pin_weight',
        'ref_message_nr', 'edit_account_id', 'edited_time',
        'html_email_data',
        'lock_account_id', 'inbox_nr', 'subject')

    ALL_FIELDS = ('message_nr', 'tags') + SIMPLE_FIELDS

    LOCAL_FIELDS = ('is_hidden', 'is_editing', 'is_pinned', 'is_unpinned', 'is_task')

    #__slots__ = ALL_FIELDS + LOCAL_FIELDS

    def __init__(self, message):
        """Initialize message from dict received from server
        """
        self.message_nr = message['message_nr']
        self.tags = message.get('tags',[])
        for k in self.SIMPLE_FIELDS:
            setattr(self, k, message.get(k))
        self.is_hidden = False
        self.is_editing = False
        self.is_pinned = 'pin' in self.tags
        self.is_unpinned = 'unpin' in self.tags
        self.is_task = 'is_task' in self.tags

    def as_dict(self):
        res = {}
        for k in self.ALL_FIELDS:
            res[k] = getattr(self, k)
        return res

    def apply_stream_rec(self, message):
        for k in self.SIMPLE_FIELDS:
            setattr(self, k, message.get(k, getattr(self, k)))
        self.tags = message.get('tags', self.tags)
        self.is_pinned = 'pin' in self.tags
        self.is_unpinned = 'unpin' in self.tags
        if 'unlock' in self.tags:
            self.lock_account_id = None

    def get_refs(self):
        """Get list of urls taht can be sent to edit as attatchments
        """
        return find_xml_refs(self.message)

    def show(self, contacts, teams, files, read_msg_nr = None, is_pinboard = False):
        """Put together message to e displayed
        """
        if self.is_hidden:
            return None
        message_nr = self.message_nr
        display_name = contacts.get_name(self.account_id)
        message = self.message
        # if normal text message
        if self.mk_message_type in ('text','email'):
            if message == '':
                message = '*** message deleted ***'
            else:
                refs = find_xml_refs(message)
                message = re.sub(r'\<.*?\>', '', message)
                for ref in refs:
                    file_key = ref
                    r_file = files[file_key]
                    if r_file.get('is_deleted'):
                        message += '\nFile deleted'
                    else:
                        message += '\nFile: ' + r_file['file_name']
                if 'is_task' in self.tags:
                    if 'is_done' in self.tags:
                        message = '[v] ' + message
                    else:
                        message = '[ ] ' + message
                if self.subject:
                    message = message + ' (Subject: ' + self.subject + ')'
        elif self.mk_message_type == 'create':
            data = json.loads(self.message)
            if data['members']:
                names = contacts.get_names(data['members'])
                message = "*** created conversation with %s as members ***" % ', '.join(names)
            else:
                message = "*** created conversation ***"
        elif self.mk_message_type == 'add':
            data = json.loads(self.message)
            names = contacts.get_names(data['members'])
            message = "*** added %s to the conversation ***" % ', '.join(names)
        elif self.mk_message_type == 'signin':
            message = "*** became Fleep user!***"
        elif self.mk_message_type == 'disclose':
            data = json.loads(self.message)
            names = contacts.get_names(data['members'])
            message = "*** disclosed history to %s ***" % ', '.join(names)
        elif self.mk_message_type == 'file':
            data = json.loads(self.message)
            if data.get('is_deleted'):
                message = '*** file deleted ***'
            else :
                message = "*** uploaded file " + data['file_name'] + " ***"
        elif self.mk_message_type == 'hook':
            data = json.loads(self.message)
            hook_name = data['hook_name']
            hook_key = data['hook_key']
            message = "*** added hook %s ***" % hook_name
        elif self.mk_message_type == 'leave':
            message = "*** left the conversation ***"
        elif self.mk_message_type == 'kick':
            data = json.loads(self.message)
            if data['members']:
                names = contacts.get_names(data['members'])
                message = "*** removed %s from conversation ***" % ', '.join(names)
        elif self.mk_message_type == 'topic':
            data = json.loads(self.message)
            topic = data['topic']
            message = "*** changed topic to " + topic + " ***"
        elif self.mk_message_type == 'unhook':
            data = json.loads(self.message)
            hook_name = data['hook_name']
            hook_key = data['hook_key']
            message = "*** removed hook %s ***" % hook_name
        elif self.mk_message_type == 'delfile':
            data = json.loads(self.message)
            message = "*** deleted %s ***" % data['file_names']
        elif self.mk_message_type == 'add_team':
            data = json.loads(self.message)
            names = teams.get_names(data['teams'])
            message = "*** added %s to the conversation ***" % ', '.join(names)
        elif self.mk_message_type == 'kick_team':
            data = json.loads(self.message)
            names = teams.get_names(data['teams'])
            message = "*** removed %s from the conversation ***" % ', '.join(names)
        elif self.mk_message_type == 'autojoin':
            data = json.loads(self.message)
            message = "***" + re.sub(r'\+ \{.*?\}', '', data['sysmsg_text'][:-1]) + " ***"
        elif self.mk_message_type in ('share','unshare','show','unshow','url_previews','no_url_previews'):
            data = json.loads(self.message)
            message = "***" + re.sub(r'\{.*?\}', '', data['sysmsg_text'][:-1]) + " ***"


        is_edited = '*' if self.edit_account_id and self.mk_message_type in ('text') else ' '
        is_edited = '/' if self.lock_account_id else is_edited
        is_pinned = '|' if self.is_pinned or self.is_unpinned else ' '
        is_pinned = '#' if self.lock_account_id and self.is_pinned else is_pinned
        is_unread = ' '
        if read_msg_nr is not None and not is_pinboard:
            is_unread = '+' if self.inbox_nr > 0 else '-'
            is_unread =  ' ' if self.message_nr <= read_msg_nr else is_unread
        return "{:>4} {:<20} {}{}{} {}".format(message_nr, display_name, is_unread, is_edited, is_pinned, message)

#
# --- Conversation ------------------------------------------------------------------------
#

class Conversation(object):
    """Conversation object used inside client cache. Encapsulates conveniently conversation
       service calls and makes sure that conversation stays in consistent state at all times.
    """
    def __init__(self, cache, conversation_id):
        """Creates new conversation object and if conversation_id is provided
           does also initial sync from database
        """
        self.api = cache.api            #: used to call FleepApi methods
        self.contacts = cache.contacts  #: we need to access contacts also
        self.teamlist = cache.teams     #: account teams
        self.owner_id = cache.account['account_id']
        self.conversation_id = conversation_id
        self.join_message_nr = None     #: bigint - message on which user joined the conversation
        #: first time (in case there are several appearances)
        self.read_message_nr = None     #: bigint - Current truth about read horizon. Normally it only
        #: increased but sometimes user may mark some messages unread.
        self.last_message_nr = None     #: bigint - last message nr in the conversation or last message
        #: that is shown in case of leaving conversation
        self.can_post = False           #: boolean - true if profile is still in conevrsation
        #: and can post to this conversation
        self.bw_message_nr = None       #: bigint- number to be submitted to sync messages when
        #: moving backward in message flow. Returned when moving backward
        self.fw_message_nr = None       #: bigint - number to be submitted to sync messages call when
        #: moving forward in message flow. Returned when moving forward
        self.poke_message_nr = None     #: bigint - used for syncing
        self.pin_horizon = None         #: bigint - set if there is more stuff on pinboard than was sent
        self.file_horizon = None        #: bigint - set if there are more files to sync
        self.topic = None               #: text - topic. Returned when changed
        self.account_id = None          #: text - conversation owner. Returned when changed.
        self.last_message_time = None   #: when last message was sent to this conversation
        self.hide_message_nr = None     #: message nr where conversation was hidden
        self.my_message_nr = None       #: last mention number
        self.messages = {}              #: messages by message nr
        self.members = []               #: list of memberInfo records
        self.leavers = []               #: list of leaver id's
        self.pinboard = {}              #: Pinboard dictionary
        self.activity = {}              #: Member activity records for ones who send them
        self.show_horizon = None        #: used by cache object to keep track what we have shown
        self.mk_alert_level = None      #: does user want to receive notifications from this chat
        self.unread_count = None        #: number of unread alerting messages in conversation
        self.inbox_message_nr = None    #: inbox message nr for conversation list
        self.hooks = {}                 #: list of hooks
        self.teams = []                 #: list of teams in conversation
        self.labels = []                #: labels user has given to this conversation
        self.files = {}                 #: files attached to the conversation messages
        self.autojoin_url = None        #: url for joining conversation

    @staticmethod
    def create(cache, topic, emails = None, message = None, attachments = None):
        """Create new conversation object with given topic and participants
        """
        c = cache.api.conversation_create(topic, emails, message, attachments)
        r = Conversation(cache, c['header']['conversation_id'])
        r._update(c)
        return r

    def reset(self):
        """Reset conversation contents. Used when receiving new init from server
        """
        self.messages = {}              #: messages by message nr
        self.pinboard = {}              #: Pinboard dictionary
        self.activity = {}              #: Member activity records for ones who send them

    def get_ref_urls(self, message_nr):
        """Get list of urls that can be sent to edit as attatchments
        """
        r_message = self.messages[message_nr]
        refs = r_message.get_refs()
        return [self.files[ref_key]['file_url'] for ref_key in refs]

    def update_lock(self, message):
        """Apply message received from event stream
        """
        mnr = message['message_nr']
        if mnr in self.messages:
            self.messages[mnr].apply_stream_rec(message)
            m = self.messages[mnr]
            if 'lock_account_id' not in message:
                m.lock_account_id = None

    def update_message(self, message):
        """Apply message received from event stream
        """
        mnr = message['message_nr']
        if mnr in self.messages:
            self.messages[mnr].apply_stream_rec(message)
        else:
            self.messages[mnr] = Message(message)
        m = self.messages[mnr]

        msg_nr = m.flow_message_nr if m.flow_message_nr else m.message_nr
        # if we got next sequential message to our current batch from conversation
        if msg_nr == self.fw_message_nr + 1:
            self.fw_message_nr += 1

        if m.is_unpinned:
            if m.ref_message_nr in self.pinboard:
                del self.pinboard[m.ref_message_nr]
        elif m.is_pinned:
            self.pinboard[m.message_nr] = m.pin_weight
        if 'lock_account_id' not in message:
            m.lock_account_id = None

        if m.mk_message_type and m.mk_message_type not in (
                'sysmsg','disclose','hook','unhook','text','email','create',
                'add','leave','topic','kick','file','signin','alerts','delfile',
                'add_team','kick_team','hangout','share','unshare','autojoin',
                'separator','show','unshow','no_url_previews','url_previews','bounce','replace'):
            logging.warning('Unhandled message type: %s', m.mk_message_type)

    def update_file(self, file_rec):
        """Update File information
        """
        file_key = file_rec['attachment_id']
        self.files[file_key] = file_rec

    def _update_header(self, c):
        """Apply updates received updates
        """
        self.join_message_nr = c.get('join_message_nr', self.join_message_nr)
        self.read_message_nr = c.get('read_message_nr', self.read_message_nr)
        self.last_message_nr = c.get('last_message_nr', self.last_message_nr)
        self.can_post = c.get('can_post', self.can_post)
        self.bw_message_nr = c.get('bw_message_nr', self.bw_message_nr)
        self.fw_message_nr = c.get('fw_message_nr', self.fw_message_nr)
        self.pin_horizon = c.get('pin_horizon', self.pin_horizon)
        self.file_horizon = c.get('file_horizon', self.file_horizon)
        self.hide_message_nr = c.get('hide_message_nr', self.hide_message_nr)
        self.my_message_nr = c.get('my_message_nr', self.my_message_nr)
        self.topic = c.get('topic', self.topic)
        self.account_id = c.get('account_id', self.account_id)
        self.members = c.get('members', self.members)
        self.leavers = c.get('leavers', self.leavers)
        self.teams = c.get('teams', self.teams)
        self.last_message_time = c.get('last_message_time', self.last_message_time)
        self.mk_alert_level = c.get('mk_alert_level', self.mk_alert_level)
        self.unread_count = c.get('unread_count', self.unread_count)
        self.inbox_message_nr = c.get('inbox_message_nr', self.inbox_message_nr)
        self.labels = c.get('labels', self.labels)
        self.autojoin_url = c.get('autojoin_url', self.autojoin_url)

        # we can start showing the conevrsation
        if self.show_horizon is None:
            self.show_horizon = self.read_message_nr

    def update_activity(self, rec):
        member_id = rec['account_id']
        r_activity = self.activity.get(member_id)
        if r_activity:
            r_activity.update(rec)
        else:
            self.activity[member_id] = rec
            r_activity = self.activity.get(member_id)
        if r_activity.get('message_nr'):
            enr = r_activity['message_nr']
            if enr in self.messages:
                msg = self.messages[enr]
                msg.is_editing = r_activity['is_writing']
        self.poke_message_nr = rec.get('poke_message_nr')

    def is_writing(self, member_id, message_nr = None):
        r_activity = self.activity.get(member_id)
        if r_activity:
            is_pen = r_activity.get('is_writing', False)
            if message_nr and is_pen:
                return r_activity.get('message_nr',0) == message_nr
            return is_pen
        return False

    def is_locked(self, member_id, message_nr):
        r_msg = self.messages[message_nr]
        return r_msg.lock_account_id is not None

    def is_read(self, member_id, message_nr):
        r_activity = self.activity.get(member_id)
        if r_activity:
            return r_activity.get('read_message_nr', 0) >= message_nr
        return False

    def update(self, rec):
        if rec['mk_rec_type'] == 'message':
            self.update_message(rec)
        elif rec['mk_rec_type'] == 'lock':
            self.update_lock(rec)
        elif rec['mk_rec_type'] == 'conv':
            self._update_header(rec)
            if self.fw_message_nr is None:
                self._sync()
            if 'fw_message_nr' in rec and 'bw_message_nr' in rec:
                self.reset()
        elif rec['mk_rec_type'] == 'contact':
            self.contacts.upsert(rec)
        elif rec['mk_rec_type'] == 'activity':
            self.update_activity(rec)
        elif rec['mk_rec_type'] == 'poke':
            self.poke_message_nr = rec.get('message_nr')
        elif rec['mk_rec_type'] == 'hook':
            self.hooks[rec.get('hook_key')] = rec
        elif rec['mk_rec_type'] == 'team':
            self.teamlist.upsert(rec)
        elif rec['mk_rec_type'] == 'file':
            self.update_file(rec)
        elif rec['mk_rec_type'] in ['preview','label','replace']:
            pass # FIXME?
        else:
            logging.warning('Unhandled record type %s', rec['mk_rec_type'])

    def _update(self, res):
        """Update conversation object from dict received from one of the conversation api calls
        """
        if 'header' in res and res['header']:
            self.update(res['header'])

        for rec in res['stream']:
            self.update(rec)

    def _sync(self, res = None):
        """If initial sync has not been done does this
        """
        # if initial sync has not been done for this conversation do it first
        if self.fw_message_nr is None:
            self._update(
                self.api.conversation_sync(
                    self.conversation_id))
        # if conversation service did not return anything or only initial sync was asked
        if res and self.api.code == 200:
            if res.get('files'):
                return res['files']
            if res.get('sysmsg'):
                return res['sysmsg']
            self._update(res)
            return res.get('result_message_nr', None)
        return None

    def add_members(self, emails):
        """Add members to the conversation
        """
        return self._sync(
            self.api.conversation_add_members(
                self.conversation_id, emails, self.fw_message_nr))

    def create_hook(self, hook_name, mk_hook_type = 'plain'):
        """Create hook for conversation
        """
        result = self.api.conversation_create_hook(
            self.conversation_id, hook_name, mk_hook_type, self.fw_message_nr)
        self._sync(result)
        hook_info = result['hook_info']
        return hook_info['hook_url']

    def show_hooks(self):
        res = self.api.conversation_show_hooks(self.conversation_id)
        sysmsg = "Active?  Owner                Description\n"
        for r_hook in res['hooks']:
            contact = self.contacts.get_name(r_hook['account_id'])
            sysmsg += '{:<7}  {:<20} {:<20}\n'.format(
                r_hook['is_active'], contact, r_hook['hook_name'])
            if r_hook.get('hook_url'):
                sysmsg += '  {}\n'.format("URL would be here")
        return sysmsg


    def drop_hook(self, hook_key):
        """Remove hook from conversation
        """
        return self._sync(
            self.api.conversation_drop_hook(
                self.conversation_id, hook_key, self.fw_message_nr))

    def delete(self):
        """Delete conversation from list
        """
        return self._sync(
            self.api.conversation_delete(
                self.conversation_id, self.last_message_nr))

    def disclose_all(self, emails, message_nr):
        """Disclose conversation history
        """
        return self._sync(
            self.api.conversation_disclose_all(
                self.conversation_id, emails, message_nr, self.fw_message_nr))

    def hide(self):
        """Hide conversation from view
            last_message_nr is here by design to ensure that we are hiding
            all the cureent messages
        """
        return self._sync(
            self.api.conversation_hide(
                self.conversation_id, self.last_message_nr))

    def unhide(self):
        """Bring conversation out from hiding
        """
        return self._sync(
            self.api.conversation_unhide(
                self.conversation_id, self.fw_message_nr))

    def store(self, read_message_nr = None, labels = None, topic = None,
              mk_alert_level = None, snooze_interval = None, add_emails = None,
              remove_emails = None, disclose_emails = None, hide_message_nr = None,
              is_deleted = None, is_autojoin = None, is_disclose = None,
              is_url_preview_disabled = None,
              add_ids = None, disclose_ids = None, remove_ids = None):
        return self._sync(
            self.api.conversation_store(
                conversation_id = self.conversation_id,
                read_message_nr = read_message_nr,
                labels = labels,
                topic = topic,
                mk_alert_level = mk_alert_level,
                snooze_interval = snooze_interval,
                add_emails = add_emails,
                remove_emails = remove_emails,
                disclose_emails = disclose_emails,
                add_ids = add_ids,
                disclose_ids = disclose_ids,
                remove_ids = remove_ids,
                hide_message_nr = hide_message_nr,
                is_deleted = is_deleted,
                is_autojoin = is_autojoin,
                is_disclose = is_disclose,
                is_url_preview_disabled = is_url_preview_disabled,
                from_message_nr = self.fw_message_nr))

    def leave(self):
        """Leave from the conversation
        """
        return self._sync(
            self.api.conversation_leave(
                self.conversation_id, self.fw_message_nr))

    def mark_read(self, message_nr = None):
        """Set read horizon as requested by client..
        """
        if message_nr:
            mark = message_nr
        else:
            mark = self.last_message_nr
        self._sync(
            self.api.message_mark_read(
                self.conversation_id, mark, self.fw_message_nr))

    def mark_all_read(self):
        """Set read horizon as requested by client..
        """
        self._sync(
            self.api.conversation_mark_read(self.conversation_id))

    def mark_unread(self, message_nr):
        """Mark conversation unread starting from given message
        """
        self._sync(
            self.api.message_mark_unread(
                self.conversation_id, message_nr, self.fw_message_nr))

    def message_send(self, message, attachments = None, client_req_id = None):
        """Send message to flow.
        """
        return self._sync(
            self.api.message_send(
                self.conversation_id, message,  self.fw_message_nr, attachments, client_req_id))

    def message_copy(self, message_nr, to_conv_id):
        """Copy message to another conversation
        """
        return self._sync(
            self.api.message_copy(
                self.conversation_id, message_nr, to_conv_id, self.fw_message_nr))

    def message_snooze(self, message_nr, snooze_interval = None):
        """Turn off alerts for given interval
        """
        return self._sync(
            self.api.message_snooze(
                self.conversation_id, message_nr, snooze_interval, self.fw_message_nr))


    def message_edit(self, message, message_nr, attachments = None):
        """Send revision of message
        """
        return self._sync(
            self.api.message_edit(
                self.conversation_id, message, message_nr, attachments, self.fw_message_nr))

    def message_delete(self, message_nr, attachment_id = None):
        """Mark message as deleted
        """
        return self._sync(
            self.api.message_delete(
                self.conversation_id, message_nr, attachment_id, self.fw_message_nr))

    def message_pin(self, message_nr, pin_weight = None):
        """Pin the message.
        """
        return self._sync(
            self.api.message_pin(
                self.conversation_id, message_nr, pin_weight, self.fw_message_nr))

    def message_repin(self, pin_message_nr, pin_weight = None):
        """Change pinned message position on pinboard
        """
        return self._sync(
            self.api.message_repin(
                self.conversation_id, pin_message_nr, pin_weight, self.fw_message_nr))

    def message_unpin(self, pin_message_nr):
        """Unpin given message from pinboard
        """
        return self._sync(
            self.api.message_unpin(
                self.conversation_id, pin_message_nr, self.fw_message_nr))

    def message_store(self, message_nr = None, message = None,
                      attachments = None, tags = None, pin_weight = None,
                      assignee_ids = None, subject = None, is_retry = None):
        """Store changes to message
        """
        return self._sync(
            self.api.message_store(conversation_id = self.conversation_id,
                                   message_nr = message_nr,
                                   message = message,
                                   attachments = attachments,
                                   tags = tags,
                                   pin_weight = pin_weight,
                                   assignee_ids = assignee_ids,
                                   subject = subject,
                                   from_message_nr = self.fw_message_nr,
                                   is_retry = is_retry))

    def poke(self, message_nr, is_bg_poke = False):
        """Send poke event
        """
        return self._sync(
            self.api.conversation_poke(
                self.conversation_id, message_nr, is_bg_poke, self.fw_message_nr))

    def remove_members(self, emails):
        """Add members to the conversation
        """
        return self._sync(
            self.api.conversation_remove_members(
                self.conversation_id, emails, self.fw_message_nr))

    def add_team(self, team_id):
        """Add team tracking to the conversation
        """
        return self._sync(
            self.api.conversation_add_team(
                self.conversation_id, team_id, self.fw_message_nr))

    def remove_team(self, team_id):
        """Remove team tracking from the conversation
        """
        return self._sync(
            self.api.conversation_remove_team(
                self.conversation_id, team_id, self.fw_message_nr))

    def add_label(self, label):
        labels = self.labels
        labels.append(label)
        return self._sync(
            self.api.conversation_update_labels(
                self.conversation_id, labels))

    def change_label(self, label, new_label = None):
        if label == new_label:
            return
        labels = self.labels
        is_changed = False
        for i, cur_label in enumerate(labels):
            if cur_label == label:
                is_changed = True
                if new_label is None:
                    labels.pop(i)
                    break
                else:
                    labels[i] = new_label
                    break
        if is_changed:
            return self._sync(
                self.api.conversation_update_labels(
                    self.conversation_id, labels))

    def show_labels(self):
        labels = ' | '.join([label for label in self.labels])
        return labels

    def assign_task(self, message_nr, assignee_ids = None):
        return self._sync(
            self.api.task_assign(
                self.conversation_id, message_nr, assignee_ids, self.fw_message_nr))

    def archive_task(self, message_nr):
        return self._sync(
            self.api.task_archive(
                self.conversation_id, message_nr, self.fw_message_nr))

    def activate_task(self, message_nr):
        return self._sync(
            self.api.task_activate(
                self.conversation_id, message_nr, self.fw_message_nr))

    def sort_task(self, message_nr, below_task_weight = None, is_my_tasklist = None):
        return self._sync(
            self.api.task_sort(
                self.conversation_id, message_nr, below_task_weight, is_my_tasklist, self.fw_message_nr))

    def create_task(self, message, attachments = None, assignee_ids = None):
        return self._sync(
            self.api.task_create(
                self.conversation_id, message, self.fw_message_nr, attachments, assignee_ids))

    def make_task(self, message_nr):
        return self._sync(
            self.api.task_make(
                self.conversation_id, message_nr, self.fw_message_nr))

    def task_done(self, message_nr):
        return self._sync(
            self.api.task_done(
                self.conversation_id, message_nr, self.fw_message_nr))

    def task_todo(self, message_nr):
        return self._sync(
            self.api.task_todo(
                self.conversation_id, message_nr, self.fw_message_nr))

    def task_list(self, sync_horizon = None, is_archive = None):
        return self._sync(
            self.api.task_list(
                self.conversation_id, sync_horizon, is_archive))

    def set_alerts_off(self):
        """Turn off alerting"""
        return self._sync(
            self.api.conversation_set_alerts(
                self.conversation_id, 'never', self.fw_message_nr))

    def set_alerts_on(self):
        """Turn on alerting"""
        return self._sync(
            self.api.conversation_set_alerts(
                self.conversation_id, 'default', self.fw_message_nr))

    def set_topic(self, topic):
        """Change conversation topic"""
        return self._sync(
            self.api.conversation_set_topic(
                self.conversation_id, topic, self.fw_message_nr))

    def set_active(self):
        """Switch on activity sending for conversation"""
        return self._sync(
            self.api.conversation_show_activity(
                self.conversation_id, None, None, self.fw_message_nr))

    def show_pen(self, message_nr = None):
        """Show user writing activity"""
        return self._sync(
            self.api.conversation_show_activity(
                self.conversation_id, message_nr, True, self.fw_message_nr))

    def hide_pen(self, message_nr = None):
        """Show user writing activity"""
        return self._sync(
            self.api.conversation_show_activity(
                self.conversation_id, message_nr, False, self.fw_message_nr))

    def search(self, keywords, search_types=None):
        """Search for keyword
        """
        res = self.api.search(keywords, self.conversation_id, search_types = search_types)
        matches = res.get('matches')
        lines = "Search results for '" + keywords + "':"
        for match in matches:
            lines += "\n" + str(match.get('inbox_nr')) + " " + re.sub(r'\<.*?\>', '', match.get('marked_text'))
        return lines

    def sync(self):
        """Do initial sync if it has not been done yet
        """
        self._sync() # ensure we have initial sync

    def sync_next(self):
        """Fetch next batch of messages
        """
        self._sync() # ensure we have initial sync
        self._sync(
            self.api.conversation_sync(
                self.conversation_id, self.fw_message_nr, 'forward'))

    def sync_prev(self):
        """Fetch previous batch of messages
        """
        self._sync() # ensure we have initial sync
        self._sync(
            self.api.conversation_sync(
                self.conversation_id, self.bw_message_nr, 'backward'))

    def sync_files(self):
        self._sync() # ensure we have initial sync
        self._sync(
            self.api.conversation_sync_files(
                self.conversation_id, self.file_horizon))

    def sync_pins(self):
        self._sync() # ensure we have initial sync
        self._sync(
            self.api.conversation_sync_pins(
                self.conversation_id, self.pin_horizon))

    def sync_to_last(self):
        """Sync to the last message in conversation
        """
        self.sync_next()
        self._sync() # ensure we have initial sync
        while self.fw_message_nr < self.last_message_nr:
            self.sync_next()
        while self.pin_horizon:
            self.sync_pins()
        while self.file_horizon:
            self.sync_files()

    def rename_file(self, file_id, file_name):
        """Upload files
        """
        self._sync()
        return self._sync(
            self.api.file_rename(
                self.conversation_id, file_id, file_name, self.fw_message_nr))

    def sync_to_first(self):
        """Sync to the first message in conversation
        """
        while self.join_message_nr < self.bw_message_nr:
            self.sync_prev()

    def get_prev_message(self, message_nr):
        """Get previous messages account_id
        """
        if message_nr - 1 in self.messages:
            return self.messages[message_nr - 1]
        else:
            nrs = self.messages.keys()
            nrs.sort()
            message_pos = bisect_left(nrs, message_nr)
            if message_pos == len(nrs) or nrs[message_pos] >= message_nr:
                message_pos -= 1
            if message_pos >= 0:
                return self.messages[nrs[message_pos]]
        return None

    def get_next_message(self, message_nr):
        """Get next message
        """
        if message_nr + 1 in self.messages:
            return self.messages[message_nr + 1]
        elif message_nr < self.last_message_nr:
            nrs = self.messages.keys()
            nrs.sort()
            message_pos = bisect_right(nrs, message_nr)
            if message_pos < len(nrs) and nrs[message_pos] <= message_nr:
                message_pos += 1
            if message_pos >= 0 and message_pos < len(nrs):
                return self.messages[nrs[message_pos]]
        return None

    def show_header(self):
        """Return conversation header string
        """
        self._sync() # ensure we have initial sync
        alerts_off = '  Alerts: OFF' if self.mk_alert_level == 'never' else ''
        has_mention = '@' if self.my_message_nr > self.read_message_nr else ''
        return "{:<20}  {:<20}  Unread:{:>2}{}  Read#:{:>3}  Last#:{:>3}  Inbox#:{:>3}  {}".format(
            self.topic,
            self.contacts.get_owner(),
            has_mention,
            self.unread_count,
            self.read_message_nr,
            self.last_message_nr,
            self.inbox_message_nr,
            alerts_off)

    def get_lines(self, nrs, is_pinboard = False):
        '''Get message lines
        '''
        lines = []
        for nr in nrs:
            lines.append(
                self.messages[nr].show(
                    self.contacts, self.teamlist, self.files, self.read_message_nr, is_pinboard))
        return lines

    def show_all(self):
        self._sync() # ensure we have initial sync
        nrs = self.messages.keys()
        nrs.sort()
        flow = ''
        lines = self.get_lines(nrs)
        flow = '\n'.join([l for l in lines if l])
        return flow

    def show_tasklist(self, show_archive = False):
        self._sync()
        nrs = self.messages.keys()
        nrs.sort()
        lines = []
        if show_archive:
            for nr in nrs:
                if ('is_task', 'is_archived') in self.messages[nr].tags:
                    lines.append(
                        self.messages[nr].show(
                            self.contacts, self.teamlist, self.files, self.read_message_nr))
        else:
            for nr in nrs:
                if 'is_task' in self.messages[nr].tags and 'is_archived' not in self.messages[nr].tags:
                    lines.append(
                        self.messages[nr].show(
                            self.contacts, self.teamlist, self.files, self.read_message_nr))
        header = 'Tasks (%s):\n' % len(lines)
        tasks = header + '\n'.join([l for l in lines if l])
        return tasks

    def show_flow(self, show_count = False):
        """Show next part of message flow
        """
        self._sync() # ensure we have initial sync
        nrs = self.messages.keys()
        nrs.sort()
        flow = ''
        if self.show_horizon < self.last_message_nr:
            i = bisect_left(nrs, self.show_horizon + 1)
            tail = nrs[i:]
            if len(tail) == 0:
                tail = nrs[i-1:]
            lines = self.get_lines(tail)
            self.show_horizon = tail.pop()
            count_header = 'Messages (%s):\n' % len(lines) if show_count else ''
            flow = count_header + '\n'.join([l for l in lines if l])
        else:
            if show_count:
                flow = 'No unread messages'
        return flow

    def show_members(self, show_active = False):
        """Show conversation members.
        """
        self._sync() # ensure we have initial sync
        if not self.members:
            return 'No active members.'
        lines = [self.contacts.show_activity(mid, self.activity.get(mid), show_active) for mid in self.members]
        lines.sort()
        return 'Members (%s):\n%s' % (len(self.members), '\n'.join([l for l in lines if l]))

    def show_pinboard(self):
        """Show ordered pinboard
        """
        self._sync() # ensure we have initial sync
        if not self.pinboard:
            return 'Pinned: 0'
        nrs = sorted(self.pinboard, key=self.pinboard.get)
        lines = self.get_lines(nrs, True)
        return 'Pinboard (%s):\n%s' % (len(nrs), '\n'.join([l for l in lines if l]))

    def show(self, show_flow = True, show_members = True, show_pinboard = True, from_first = False, show_active = False):
        """Display current state and messages received since last
           call in log
        """
        if from_first:
            self.sync_to_first()
            self.sync_to_last()
            self.show_horizon = 0
        header = self.show_header()
        flow = "\n" + self.show_flow(show_count = True) if show_flow else ''
        members = '\n' + self.show_members(show_active) if show_members else ''
        pinboard = '\n' + self.show_pinboard() if show_pinboard else ''
        return "%s%s%s%s" % (header, members, pinboard, flow)

    def is_unread(self):
        """ Returns 1 if conversation has unread messages otherwise 0
        """
        return 1 if self.unread_count > 0 else 0

# --- ContactList ------------------------------------------------------------------------
#

class ContactList(object):
    """Manages accounts contactlist
    """
    def __init__(self, api, account_id):
        self.api = api
        self.contacts = {}                      #: contacts by account_id
        self.emails = {}                        #: contacts by email
        self.fully_synced = False               #: set to true only after full sync
        self.account_id = account_id

    def upsert(self, a):
        """Insert or update contact
        """
        self.emails[a['email']] = self.contacts[a['account_id']] = a

    def describe(self, email, contact_name, phone_nr = None):
        a = self.emails[email]
        contact_id = a['account_id']
        self.api.contact_describe(contact_id, contact_name, phone_nr)
        self.sync_list([contact_id])

    def hide(self, emails):
        contacts = []
        for email in emails:
            contact = self.emails.get(email)
            if contact:
                contacts.append(contact['account_id'])
        changed = self.api.contact_hide(contacts).get('contacts')
        self.sync_list(changed)

    def sync_email(self, email):
        '''Sync contact into contactlist by email
        '''
        a = self.emails[email]
        self.sync_one(a['account_id'])

    def sync_fadr(self, fleep_address):
        """
        """
        for r_contact in self.contacts.values():
            if r_contact.get('fleep_address') == fleep_address:
                return r_contact['account_id']
        return None

    def sync_one(self, account_id):
        """Sync just one contact
        """
        a = self.api.contact_sync(account_id)
        self.upsert(a)

    def sync_list(self, accounts):
        """Sync contacts from given list of uuid's
        """
        res = self.api.contact_sync_list(accounts)
        for a in res['contacts']:
            self.emails[a['email']] = self.contacts[a['account_id']] = a

    def sync_all(self):
        """Send all uuid's you have to server and let server return you all you are missing
            also sets's internal event horizon so we know we are in full sync now
        """
        res = self.api.contact_sync_all(self.contacts.keys())
        for a in res['contacts']:
            self.emails[a['email']] = self.contacts[a['account_id']] = a
        self.fully_synced = True

    def get_account_id(self, email):
        a = self.emails[email]
        return a['account_id']

    def get_name(self, account_id):
        """Get contact from cache and if not found from server.
        """
        if account_id not in self.contacts:
            self.sync_one(account_id)
        a = self.contacts[account_id]
        return a.get('display_name') or a['email']

    def get_email(self, account_id):
        if account_id not in self.contacts:
            self.sync_one(account_id)
        a = self.contacts[account_id]
        return a['email']

    def get_status(self, account_id):
        if account_id not in self.contacts:
            self.sync_one(account_id)
        a = self.contacts[account_id]
        return a['mk_account_status']

    def get_names(self, accounts):
        """Useful for system messages
        """
        return sorted([self.get_name(v) for v in accounts])

    def find(self, namepart):
        """Does local find for exact email match, if no match then one roundtrip to server
           to sync all the contacts
        """
        if namepart in self.emails:
            return [self.emails[namepart]]
        else:
            if not self.fully_synced:
                self.sync_all()

    def show_activity(self, member_id, r_activity = None, show_active = False):
        ''' Show conversation member and his activity
        '''
        r_contact = self.contacts[member_id]
        l = list()
        l.append(self.get_name(member_id))
        # l.append(self.get_status(member_id))
        if r_activity and r_activity.get('read_message_nr'):
            l.append("Read: %s" % r_activity['read_message_nr'])
        if r_activity and r_activity.get('message_nr') and r_activity.get('is_writing'):
            l.append("Editing: %s" % r_activity['message_nr'])
        elif r_activity and r_activity.get('is_writing'):
            l.append('Writing')
        if 'activity_time' in r_contact and show_active:
            if time.time() - r_contact['activity_time'] < 300:
                l.append('Active')
        return ' '.join(l)

    def show(self):
        """Display contents of contact cache in log.
        """
        contacts = sorted(self.contacts.values(), key=lambda x: x['email'])
        contacts_show = [contact for contact in contacts if contact['is_hidden_for_add'] != True]
        contactlist = "Contacts:\n"
        for contact in contacts_show:
            if contact.get('mk_account_status') == 'closed':
                continue
            #print contact
            has_avatar = ""
            if contact.get('avatar_urls') is not None and contact.get('avatar_urls') != '{}':
                has_avatar = "Has avatar"

            display_name = contact.get('display_name') if contact.get('display_name') != contact.get('email') else ''
            contactlist += "%s %s %s %s %s\n" % (
                contact.get('email'),
                contact.get('mk_account_status'),
                display_name,
                contact.get('phone_nr'),
                has_avatar)
        return contactlist

    def get_owner(self):
        """Owners name
        """
        return self.get_name(self.account_id)


# --- TeamList ------------------------------------------------------------------------
#

class TeamList(object):
    """Teams this account is part of
    """
    def __init__(self, api):
        self.api = api
        self.teams = {}                         #: teams by team_id

    def upsert(self, a):
        """Insert or update contact
        """
        self.teams[a['team_id']] = a

    def create_team(self, team_name, members = None, conversations = None):
        """Create team with given memebrs and or conversations
        """
        return self.api.team_create(team_name, members, conversations)

    def add_members(self, team_id, emails):
        """Add members to team
        """
        return self.api.team_configure(team_id, added_emails = emails)

    def remove_members(self, team_id, emails):
        return self.api.team_configure(team_id, removed_emails = emails)

    def remove_team(self, team_id):
        """Remove team
        """
        return self.api.team_remove(team_id)

    def get_name(self, team_id):
        """Get team name from cache
        """
        r_team = self.teams[team_id]
        return r_team.get('team_name')

    def get_names(self, teams):
        """Useful for system messages
        """
        return sorted([self.get_name(team_id) for team_id in teams])

    def show(self):
        """Display contents of team cache
        """
        teams = sorted(self.teams.values(), key=lambda x: x['team_name'])
        return '\n'.join(
            ["%s" % (r_team['team_name'],) for r_team in teams])

    def get_members(self, team_id):
        r_team = self.teams[team_id]
        return r_team['members']

    def get_convs(self, team_id):
        r_team = self.teams[team_id]
        return r_team['conversations']


#
# --- FleepCache ------------------------------------------------------------------------
#

class FleepCache(object):
    """Client memory cache model
    """
    def __init__(self, url, email = None, password = None, token = None, ticket = None):
        # create session and log in
        self.api = FleepApi(url)                #: for any request except long poll
        self.account = None                     #: owners account details
        if token:
            self.api.set_token(token = token, ticket = ticket)
            self.account = self.api.account_sync()
        else:
            self.account = self.api.account_login(email, password)
        # another one for long poll
        self.lp = None                          #: only for long poll
        # cache collections and state
        self.contacts = ContactList(self.api, self.account['account_id'])
        self.teams = TeamList(self.api)
        self.conversations = {}                 #: conversations by conversation_id
        self.flags = []
        self.event_horizon = 0                  #: how far we have synced events
        self.aliases = []                       #: list of aliases attachd to this account
        self.fleep_address = None

        # do initial sync:
        while True:
            self.poll(False, ['skip_hidden'])
            if self.event_horizon > 0:
                break
            if not self.conversations:
                break

    def clear(self):
        ''' Hide all exisiting conversations for given user
        '''
        count = 0
        for r_conv in self.conversations.values():
            if not r_conv.hide_message_nr >= r_conv.last_message_nr:
                if r_conv.can_post and r_conv.topic:
                    r_conv.set_topic('')
                r_conv.hide()
                count += 1
        return count

    def conversation_list(self):
        """ Returns sorted list of visible conversations
        """
        conversations = sorted(self.conversations.values(), key=lambda x: x.last_message_time, reverse=True)
        conversations.sort(key=lambda x: x.is_unread(), reverse=True)
        conversations = [conv for conv in conversations if not conv.hide_message_nr >= conv.last_message_nr]
        return conversations

    def show_convlist(self, topics = None):
        convlist = ""
        for conv in self.conversation_list():
            if topics and conv.topic not in topics:
                continue
            convlist += conv.show_header() + "\n"
        return convlist

    def team_list(self):
        """ Team list for current user
        """
        retval = self.api.account_sync_teams()
        self._process_stream(retval['stream'])

    def team_create(self, team_name, members = None, conversations = None):
        """Create team
        """
        retval = self.teams.create_team(team_name, members, conversations)
        self._process_stream(retval['stream'])
        for rec in retval['stream']:
            if rec['mk_rec_type'] == 'team':
                return rec['team_id']

    def team_remove(self, team_id):
        retval = self.teams.remove_team(team_id)
        self._process_stream(retval['stream'])

    def team_add_members(self, team_id, emails):
        retval = self.teams.add_members(team_id, emails)
        self._process_stream(retval['stream'])

    def team_remove_members(self, team_id, emails):
        retval = self.teams.remove_members(team_id, emails)
        self._process_stream(retval['stream'])

    def team_show_members(self, team_id):
        team = self.teams.get_name(team_id)
        members = self.teams.get_members(team_id)
        names = self.contacts.get_names(members)
        return team + '\n' + '\n'.join(
            ["%s" % name for name in names])

    def team_show_convs(self, team_id):
        team = self.teams.get_name(team_id)
        convs = self.teams.get_convs(team_id)
        return team + '\n' + '\n'.join(
            ["%s" % self.conversations[conv].topic for conv in convs])

    def conversation_find(self, topic):
        """Return list of conversations with given topic.
        """
        return [v for v in self.conversations.values() if v.topic == topic]

    def conversation_create(self, topic, emails, message = None, attachments = None):
        """Create conversation
        """
        c = Conversation.create(self, topic, emails, message, attachments)
        self.conversations[c.conversation_id] = c
        return c

    def conversation_get(self, conversation_id, is_activity_needed = False):
        """Tries to locate conversation by id and if not found creates it.
        """
        # see if conversation already exists or create it
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(self, conversation_id)
        r_conv = self.conversations[conversation_id]
        if is_activity_needed:
            r_conv.set_active()
        return r_conv

    def conversation_open(self, topic, emails, message = None, attachments = None):
        """Tries to locate conversation by topic and if not found creates it.
        """
        # see if conversation already exists or create it
        conv_list = self.conversation_find(topic)
        for conv in conv_list:
            conv.set_topic('')
            conv.hide()
        r_conv = self.conversation_create(topic, emails, message, attachments)
        r_conv.set_active()
        return r_conv

    def upload_file(self, files):
        return self.api.file_upload(files)['files']

    def upload_file_url(self, file_name):
        files = {'files' : open(file_name, 'rb')}
        r_file = self.upload_file(files)[0]
        return r_file['upload_url']

    def upload_file_id(self, file_name):
        files = {'files' : open(file_name, 'rb')}
        r_file = self.upload_file(files)[0]
        return r_file['file_id']

    def _process_stream(self, stream):
        """Process incoming records
        """
        del_ids = []
        for rec in stream:
            if not rec.get('mk_rec_type'):
                logging.warning('Broken record %s', rec)
                continue

            if rec['mk_rec_type'] in ('conv','message','activity','poke','hook','file','lock'):
                c = self.conversation_get(rec['conversation_id'])
                if rec['mk_rec_type'] == 'conv' and rec.get('is_deleted'):
                    self.conversations.pop(rec['conversation_id'])
                    del_ids.append(rec['conversation_id'])
                elif rec['conversation_id'] not in del_ids:
                    c.update(rec)
            elif rec['mk_rec_type'] == 'request':
                self.api.requests.add(rec['client_req_id'])
            elif rec['mk_rec_type'] == 'contact':
                self.contacts.upsert(rec)
            elif rec['mk_rec_type'] == 'team':
                if rec['is_deleted'] and rec['team_id'] in self.teams.teams.keys():
                    del self.teams.teams[rec['team_id']]
                else:
                    self.teams.upsert(rec)
            elif rec['mk_rec_type'] in ['preview','label','replace']:
                pass
            else:
                logging.warning('Unhandled record type %s', rec['mk_rec_type'])

    def poll(self, wait = True, poll_flags = None):
        """Sync internal structures so that they are up to date with server
           Get next batch of unprocessed events and process them
           Returns True if we have caught up with server
        """
        if self.lp is None:
            self.lp = FleepApi(self.api.base_url)
            self.lp.set_token(token = self.api.get_token(), ticket = self.api.get_ticket())
        res = self.lp.account_poll(self.event_horizon, wait, poll_flags)
        self._process_stream(res['stream'])
        # if we received any events
        if self.event_horizon != res['event_horizon']:
            self.event_horizon = res['event_horizon']
            return True
        return False

    def poll_poke(self, source_conv, message_nr = -1, is_bg_poke = False):
        if source_conv.conversation_id in self.conversations:
            conv = self.conversation_get(source_conv.conversation_id)
            conv.poke(-1, is_bg_poke)
        else:
            return
        for seconds in range(30):
            if conv.poke_message_nr == -1:
                conv.poke_message_nr = None
                break
            self.poll(False)
            time.sleep(1)
        else:
            raise Exception("poll_poke: conversation sync failed")

    def poll_until(self, source_conv, last_message_nr = None):
        """Poll until conversation in current cache with same id as source_conv
           gets synced to given last_message_nr or source_conv last_message_nr
           If sync is not reached in 10 seconds assert is thrown
        """
        if last_message_nr is None:
            last_message_nr = source_conv.last_message_nr
        for seconds in range(10):
            if source_conv.conversation_id in self.conversations:
                conv = self.conversation_get(source_conv.conversation_id)
                #print 'Sleep: ', seconds, 'Last: ',last_message_nr, 'Fw: ', conv.fw_message_nr
                if last_message_nr <= conv.fw_message_nr:
                    break
            self.poll(False)
            time.sleep(1)
        else:
            raise Exception("poll_until: conversation sync failed")

    def poll_request(self, clinet_request_id):
        """Poll until request travels through event sender
        """
        for seconds in range(10):
            # check if it has flipped alread
            if clinet_request_id in self.api.requests:
                break
            self.poll(False)
            time.sleep(1)
        else:
            raise Exception("poll_pen: conversation sync failed")

    def poll_activity(self, source_conv, activity,  message_nr = None):
        """Poll until pen events travels through servers.
        """
        conv = self.conversation_get(source_conv.conversation_id)
        member_id = source_conv.owner_id
        for seconds in range(10):
            if (activity == 'is_writing' and conv.is_writing(member_id)
                or  activity == 'is_editing' and conv.is_writing(member_id, message_nr)
                or  activity == 'is_idle' and not conv.is_writing(member_id)
                or  activity == 'is_locked' and conv.is_locked(member_id, message_nr)
                or  activity == 'is_unlocked' and not conv.is_locked(member_id, message_nr)
                or  activity == 'is_read' and conv.is_read(member_id, message_nr)
                ):  break
            self.poll(False)
            time.sleep(1)
        else:
            raise Exception("poll_activity: conversation sync failed")

    def set_flag(self,flag,bool_value = True):
        res = self.api.account_set_flag(flag, bool_value)
        self.flags = res['client_flags']

    def sync_alias(self):
        retval = self.api.alias_sync()
        self.aliases = []
        for r_contact in retval['stream']:
            if r_contact['account_id'] != self.account['account_id']:
                self.aliases.append(r_contact)
        for rec in retval['stream']:
            self.contacts.upsert(rec)
        return retval

    def get_aliases(self):
        """Return formatted list of aliases attached to this account
        """
        alias_list = "Aliases:\n"
        self.sync_alias()
        if len(self.aliases) == 0:
            alias_list += "None\n"
        else:
            for alias in self.aliases:
                status = 'alias' if alias['mk_account_status'] == 'alias' else 'pending'
                alias_list += "%s %s\n" % (status, self.contacts.get_name(alias['account_id']))
        return alias_list

    def alias_remove_all(self):
        self.sync_alias()
        for alias in self.aliases:
            email = self.contacts.contacts[alias['account_id']]['email']
            self.api.alias_remove(email)

    def fleep_address_add(self, fleep_address):
        res = self.api.fleep_address_add(fleep_address)
        self.fleep_address = res.get('fleep_address')

class FleepListen(object):
    """Client memory cache model
    """
    def __init__(self, url, email = None, password = None, token = None, ticket = None):
        # create session and log in
        self.api = FleepApi(url)               #: for any request except long poll
        self.account = None
        if token:
            self.api.set_token(token = token, ticket = ticket)
            self.account = self.api.account_sync()
        else:
            self.account = self.api.account_login(email, password)
        # another one for long poll
        self.lp = None                          #: only for long poll
        self.event_horizon = 0                  #: how far we have synced events
        self.fresh_conv_count = 0               #: number of unread conversations
        self.messages = []                      #: list of messages returned from last trip

    def listen(self, wait = True):
        """Just listen for conv count and messages coming from server
        """
        if self.lp is None:
            self.lp = FleepApi(self.api.base_url)
            self.lp.set_token(token = self.api.get_token(), ticket = self.api.get_ticket())
        res = self.lp.account_listen(self.event_horizon, wait)
        # if we received any events
        if self.event_horizon != res['event_horizon']:
            self.event_horizon = res['event_horizon']
        if 'conv_count' in res:
            self.fresh_conv_count = res['conv_count']
        self.messages = res.get('messages') or []

    def listen_until(self, conv_count):
        """Poll until fresh conv count gets given value
        """
        seconds = 10
        while seconds:
            if conv_count == self.fresh_conv_count:
                break
            self.listen(False)
            seconds -= 1
            time.sleep(1)
        assert seconds > 0, "listen failed"