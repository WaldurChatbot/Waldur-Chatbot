"""Python Library for Fleep HTTP API.
"""

from .base import FleepApiBase

#
# --- FleepApi ------------------------------------------------------------------------
#

class FleepApi(FleepApiBase):
    """Python Library for Fleep.
    Fleep api is designed as http service calls that use JSON encoding to transfer data.
    All services are implemented as HTTP POST calls. This allows for simple scripting.
    Mapping to PUT, DELETE, GET might look ok in some cases but would increase confusion
    for usage and for cases where there is no good match.
    """

    ##
    ## client
    ##

    def client_check(self):
        """Check if client version is good enought and if client is logged in
        """
        return self._webapi_call('api/client/check')

    def client_upgrade(self):
        """Push upgrade event to client if needed
        """
        return self._webapi_call('api/client/upgrade')

    ##
    ## account
    ##

    def account_configure(self, display_name = None, old_password = None, password = None,
                          is_automute_enabled=False, # unused?
                          email_interval = None, phone_nr = None, is_full_privacy = None, primary_email = None):
        """Changes account settings
        """
        return self._webapi_call('api/account/configure',
                                 display_name = display_name,
                                 old_password = old_password,
                                 password = password,
                                 email_interval = email_interval,
                                 phone_nr = phone_nr,
                                 is_full_privacy = is_full_privacy,
                                 primary_email = primary_email)

    def account_configure_apn(self, apn_token, token_ids):
        """Changes account settings
        """
        return self._webapi_call('api/account/configure_apn',
                                 apn_token = apn_token, token_ids = token_ids)

    def account_configure_android(self, google_id, token_ids):
        """Changes account settings
        """
        return self._webapi_call('/api/account/configure_android',
                                 registration_id = google_id, token_ids = token_ids)

    def account_confirm(self, notification_id):
        """Confirm receiving an email from fleep
        """
        info = self._webapi_call('api/account/confirm',
                                 notification_id = notification_id)
        if info and info.get('ticket'):
            self.set_token(ticket = info['ticket'])
        return info

    def account_dialog(self, contact_id):
        """Opens dialog with given contact
        """
        return self._webapi_call('api/account/dialog',
                                 contact_id = contact_id)

    def account_login(self, email, password, remember_me = False):
        """Handle user login business logic.  If login is successful,
        it sets session token and returns account info.
        """
        info = self._webapi_call('api/account/login',
                                 email = email,
                                 password = password)
        if info and info.get('ticket'):
            self.set_token(ticket = info['ticket'])
        return info

    def account_logout(self):
        """Terminate current session
        """
        return self._webapi_call('api/account/logout')

    def account_poll(self, event_horizon, wait = True, poll_flags = None):
        """Handles long poll server side by storing connection information
        into connection table by the token.
        """
        return self._webapi_call('api/account/poll',
                                 event_horizon = event_horizon,
                                 wait = wait,
                                 poll_flags = poll_flags)

    def account_listen(self, event_horizon, wait = True):
        """Handles long poll server side by storing connection information
        into connection table by the token.
        """
        return self._webapi_call('api/account/listen',
                                 event_horizon = event_horizon,
                                 wait = wait)

    def account_register(self, email, password, display_name = None):
        """Register a new account
        """
        return self._webapi_call('api/account/register',
                                 password = password,
                                 email = email,
                                 display_name = display_name)

    def account_reset_password(self, email):
        """Request password reset"""
        return self._webapi_call('api/account/reset_password',
                                 email = email)

    def account_confirm_password(self, notification_id, password):
        """Confirm new password"""
        return self._webapi_call('api/account/confirm_password',
                                 notification_id = notification_id,
                                 password = password)

    def account_set_flag(self, client_flag, bool_value = True):
        """Set client flag"""
        return self._webapi_call('api/account/set_flag',
                                 client_flag = client_flag, bool_value = bool_value)

    def account_sync(self):
        """Returns all user contacts and conversations. Use it to initialize client
           if there is no local client side cache
        """
        return self._webapi_call('api/account/sync')

    def account_sync_teams(self):
        """Sync teams"""
        return self._webapi_call('api/account/sync_teams')

    def fleep_address_add(self, fleep_address):
        return self._webapi_call('api/fleep_address/add',
                                 fleep_address = fleep_address)


    ##
    ## alias
    ##

    def alias_add(self, emails):
        """Add alias to existing account so it can be
        """
        return self._webapi_call('api/alias/add',
                                 emails = emails)

    def alias_confirm(self, notification_id):
        """Confirm alias email
        """
        return self._webapi_call('api/alias/confirm',
                                 notification_id = notification_id)

    def alias_remove(self, emails):
        """Remove alias from account
        """
        return self._webapi_call('api/alias/remove',
                                 emails = emails)

    def alias_sync(self):
        """Get list of aliases for given account
        """
        return self._webapi_call('api/alias/sync')

    ##
    ## contact
    ##

    def contact_describe(self, contact_id, contact_name, phone_nr):
        """Set contact name
        """
        return self._webapi_call('api/contact/describe'
                                 , contact_id = contact_id, contact_name = contact_name, phone_nr = phone_nr)

    def contact_import(self, contact_list):
        return self._webapi_call('api/contact/import'
                                 , contact_list = contact_list)

    def contact_hide(self, contacts):
        return self._webapi_call('api/contact/hide', contacts = contacts)

    def contact_sync(self, contact_id):
        """Return contact data for given uuid. Used to keep local cache in sync
        """
        return self._webapi_call('api/contact/sync', contact_id = contact_id)

    def contact_sync_list(self, contacts):
        """Return contact data for given list of uuid's. Used to keep local cache in sync
        """
        return self._webapi_call('api/contact/sync/list', contacts = contacts)

    def contact_sync_all(self, ignore):
        """Get all accounts contacts. for speedup give list of uuid's already in cache
           it will not need to return these again
        """
        return self._webapi_call('api/contact/sync/all', ignore = ignore)

    ##
    ## conversation
    ##

    def conversation_add_members(self, conversation_id, emails, from_message_nr = None):
        """Add members to the conversation
        """
        return self._webapi_call('api/conversation/add_members', conversation_id,
                                 emails = emails,
                                 from_message_nr = from_message_nr)

    def conversation_add_team(self, conversation_id, team_id, from_message_nr = None):
        """Add members to the conversation
        """
        return self._webapi_call('api/conversation/add_team', conversation_id,
                                 team_id = team_id,
                                 from_message_nr = from_message_nr)

    def conversation_autojoin(self, conv_url_key):
        return self._webapi_call('api/conversation/autojoin',
                                 conv_url_key = conv_url_key)

    def conversation_check_permissions(self, conversation_id):
        """Check if user can participated in this conversation
        """
        return self._webapi_call('api/conversation/check_permissions', conversation_id)

    def conversation_create(self, topic = None, emails = None, message = None, attachments = None):
        """Create new conversation with given topic and members
        """
        return self._webapi_call('api/conversation/create',
                                 topic = topic,
                                 emails = emails,
                                 message = message,
                                 attachments = attachments)

    def conversation_create_hook(self, conversation_id, hook_name, mk_hook_type, from_message_nr):
        """Create hook for given conversation
        """
        return self._webapi_call('api/conversation/create_hook', conversation_id,
                                 hook_name = hook_name,
                                 mk_hook_type = mk_hook_type,
                                 from_message_nr = from_message_nr)

    def conversation_configure_hook(self, conversation_id, hook_key, hook_name, from_message_nr):
        """Change hook
        """
        return self._webapi_call('api/conversation/configure_hook', conversation_id,
                                 hook_key = hook_key,
                                 hook_name = hook_name,
                                 from_message_nr = from_message_nr)

    def conversation_drop_hook(self, conversation_id, hook_key, from_message_nr):
        """Remove hook from conversation.
        """
        return self._webapi_call('api/conversation/drop_hook', conversation_id,
                                 hook_key = hook_key,
                                 from_message_nr = from_message_nr)

    def conversation_delete(self, conversation_id, from_message_nr = None):
        """Delete conversation flow content
        """
        return self._webapi_call('api/conversation/delete', conversation_id,
                                 from_message_nr = from_message_nr)

    def conversation_disclose_all(self, conversation_id, emails, message_nr, from_message_nr = None):
        """Disclose conversation history
        """
        return self._webapi_call('api/conversation/disclose_all', conversation_id,
                                 emails = emails,
                                 message_nr = message_nr,
                                 from_message_nr = from_message_nr)

    def conversation_hide(self, conversation_id, from_message_nr = None):
        """Hide conversation from view
        """
        return self._webapi_call('api/conversation/hide', conversation_id,
                                 from_message_nr = from_message_nr)

    def conversation_unhide(self, conversation_id, from_message_nr = None):
        """Bring conversation out from hiding
        """
        return self._webapi_call('api/conversation/unhide', conversation_id,
                                 from_message_nr = from_message_nr)

    def conversation_import(self, conversation_id, hook_id, messages):
        return self._webapi_call('api/conversation/import', conversation_id,
                                 hook_id = hook_id,
                                 messages = messages)

    def conversation_leave(self, conversation_id, from_message_nr = None):
        """Leave from the conversation
        """
        return self._webapi_call('api/conversation/leave', conversation_id,
                                 from_message_nr = from_message_nr)

    def conversation_mark_read(self, conversation_id):
        """Set read horizon as requested by client..
        """
        return self._webapi_call('api/conversation/mark_read', conversation_id)

    def conversation_poke(self, conversation_id, message_nr, is_bg_poke = False, from_message_nr = None):
        """Send poke event
        """
        return self._webapi_call('api/conversation/poke',
                                 conversation_id,
                                 message_nr = message_nr,
                                 is_bg_poke = is_bg_poke,
                                 from_message_nr = from_message_nr)

    def conversation_remove_members(self, conversation_id, emails, from_message_nr = None):
        """Remove members from the conversation
        """
        return self._webapi_call('api/conversation/remove_members', conversation_id,
                                 emails = emails,
                                 from_message_nr = from_message_nr)

    def conversation_remove_team(self, conversation_id, team_id, from_message_nr = None):
        """Add members to the conversation
        """
        return self._webapi_call('api/conversation/remove_team', conversation_id,
                                 team_id = team_id,
                                 from_message_nr = from_message_nr)

    def conversation_set_alerts(self, conversation_id, mk_alert_level, from_message_nr = None):
        """Change conversation topic"""
        return self._webapi_call('api/conversation/set_alerts', conversation_id,
                                 mk_alert_level = mk_alert_level,
                                 from_message_nr = from_message_nr)

    def conversation_set_topic(self, conversation_id, topic, from_message_nr = None):
        """Change conversation topic"""
        return self._webapi_call('api/conversation/set_topic', conversation_id,
                                 topic = topic,
                                 from_message_nr = from_message_nr)

    def conversation_show_activity(self, conversation_id, message_nr, is_writing, from_message_nr = None):
        """Show user writing activity"""
        return self._webapi_call('api/conversation/show_activity', conversation_id,
                                 message_nr = message_nr,
                                 is_writing = is_writing,
                                 from_message_nr = from_message_nr)

    def conversation_show_hooks(self, conversation_id):
        return self._webapi_call('api/conversation/show_hooks',
                                 conversation_id, from_message_nr = None)

    def conversation_store(self, conversation_id, read_message_nr = None,
                           labels = None, topic = None, mk_alert_level = None,
                           snooze_interval = None, add_emails = None, remove_emails = None,
                           disclose_emails = None, hide_message_nr = None, is_deleted = None,
                           is_autojoin = None, is_disclose = None,
                           is_url_preview_disabled = None, from_message_nr = None,
                           add_ids = None, disclose_ids = None, remove_ids = None):
        return self._webapi_call('api/conversation/store', conversation_id,
                                 read_message_nr = read_message_nr,
                                 labels = labels,
                                 topic = topic,
                                 mk_alert_level = mk_alert_level,
                                 snooze_interval = snooze_interval,
                                 add_emails = add_emails,
                                 remove_emails = remove_emails,
                                 disclose_emails = disclose_emails,
                                 hide_message_nr = hide_message_nr,
                                 is_deleted = is_deleted,
                                 is_autojoin = is_autojoin,
                                 is_disclose = is_disclose,
                                 is_url_preview_disabled = is_url_preview_disabled,
                                 from_message_nr = from_message_nr,
                                 add_ids = add_ids,
                                 disclose_ids = disclose_ids,
                                 remove_ids = remove_ids)

    def conversation_update_labels(self, conversation_id, labels):
        """Change conversation labels.
        """
        return self._webapi_call('api/conversation/update_labels',
                                 conversation_id, labels = labels)

    def conversation_sync(self, conversation_id, from_message_nr = None, mk_direction = 'forward'):
        """Sync state for single conversation.
        """
        return self._webapi_call('api/conversation/sync', conversation_id,
                                 from_message_nr = from_message_nr,
                                 mk_direction = mk_direction)

    def conversation_sync_pins(self, conversation_id, from_message_nr = None):
        """Sync next batch of pins
        """
        return self._webapi_call('api/conversation/sync_pins', conversation_id,
                                 from_message_nr = from_message_nr)

    def conversation_sync_files(self, conversation_id, from_message_nr = None):
        """Sync next batch of files
        """
        return self._webapi_call('api/conversation/sync_files', conversation_id,
                                 from_message_nr = from_message_nr)

    ##
    ## file
    ##

    def avatar_upload(self, files):
        """Upload avatar.
        """
        return self._file_call('api/avatar/upload', files = files)

    def avatar_delete(self):
        """Delete avatar.
        """
        return self._webapi_call('api/avatar/delete')

    def avatar_download(self, profile_id, file_id, filename):
        print(profile_id)
        print(file_id)
        print(filename)
        url = 'api/avatar/' + profile_id + '/' + file_id + '/' + filename
        return self._webapi_call(url)

    def file_upload(self, files):
        """Upload file.
        """
        return self._file_call('api/file/upload/', files = files)

    def file_rename(self, conversation_id, file_id, file_name, from_message_nr = None):
        """Rename file.
        """
        return self._webapi_call('api/file/rename', conversation_id,
                                 file_id = file_id,
                                 file_name = file_name,
                                 from_message_nr = from_message_nr)

    ##
    ## message
    ##

    def message_copy(self, conversation_id, message_nr, to_conv_id, from_message_nr = None):
        return self._webapi_call('api/message/copy', conversation_id,
                                 message_nr = message_nr,
                                 to_conv_id = to_conv_id,
                                 from_message_nr = from_message_nr)

    def message_delete(self, conversation_id, message_nr, attachment_id = None, from_message_nr = None):
        """Mark message as delete in flow
        """
        return self._webapi_call('api/message/delete', conversation_id,
                                 message_nr = message_nr,
                                 attachment_id = attachment_id,
                                 from_message_nr = from_message_nr)

    def message_edit(self, conversation_id, message, message_nr, attachments, from_message_nr = None):
        """Send revision of previous message to the flow
        """
        return self._webapi_call('api/message/edit', conversation_id,
                                 message = message,
                                 message_nr = message_nr,
                                 attachments = attachments,
                                 from_message_nr = from_message_nr)

    def message_mark_read(self, conversation_id, message_nr, from_message_nr = None):
        """Set read horizon as requested by client..
        """
        return self._webapi_call('api/message/mark_read', conversation_id,
                                 message_nr = message_nr,
                                 from_message_nr = from_message_nr)

    def message_mark_unread(self, conversation_id, message_nr, from_message_nr = None):
        """Set read horizon as requested by client..
        """
        return self._webapi_call('api/message/mark_unread', conversation_id,
                                 message_nr = message_nr,
                                 from_message_nr = from_message_nr)

    def message_pin(self, conversation_id, message_nr, pin_weight = None, from_message_nr = None):
        """Pin the message.
        """
        return self._webapi_call('api/message/pin', conversation_id,
                                 message_nr = message_nr,
                                 pin_weight = pin_weight,
                                 from_message_nr = from_message_nr)

    def message_repin(self, conversation_id, pin_message_nr, pin_weight = None, from_message_nr = None):
        """Reorder pins on pinboard
        """
        return self._webapi_call('api/message/repin', conversation_id,
                                 pin_message_nr = pin_message_nr,
                                 pin_weight = pin_weight,
                                 from_message_nr = from_message_nr)

    def message_send(self, conversation_id, message, from_message_nr = None, attachments = None, client_req_id = None):
        """Send message to flow.
        """
        return self._webapi_call('api/message/send', conversation_id,
                                 message = message,
                                 from_message_nr = from_message_nr,
                                 attachments = attachments,
                                 client_req_id = client_req_id)

    def message_snooze(self, conversation_id, message_nr, snooze_interval = None, from_message_nr = None):
        """Turn off alerts for given interval
        """
        return self._webapi_call('api/message/snooze', conversation_id,
                                 message_nr = message_nr,
                                 snooze_interval = snooze_interval)

    def message_store(self, conversation_id, message_nr = None, message = None,
                      attachments = None, tags = None, pin_weight = None,
                      assignee_ids = None, subject = None, from_message_nr = None, is_retry = None):
        """Store changes to message
        """
        return self._webapi_call('api/message/store', conversation_id,
                                 message_nr = message_nr,
                                 message = message,
                                 attachments = attachments,
                                 tags = tags,
                                 pin_weight = pin_weight,
                                 assignee_ids = assignee_ids,
                                 subject = subject,
                                 from_message_nr = from_message_nr,
                                 is_retry = is_retry)

    def message_unpin(self, conversation_id, pin_message_nr, from_message_nr = None):
        """Unpin the message.
        """
        return self._webapi_call('api/message/unpin', conversation_id,
                                 pin_message_nr = pin_message_nr,
                                 from_message_nr = from_message_nr)


    ##
    ## team
    ##


    def team_create(self, team_name, emails = None, conversations = None):
        """Create team
        """
        return self._webapi_call('api/team/create',
                                 team_name = team_name,
                                 emails = emails,
                                 conversations = conversations)

    def team_configure(self, team_id, team_name = None,
                       added_emails = None, removed_emails = None,
                       added_conversations = None, removed_conversations = None):
        """Change team
        """
        return self._webapi_call('api/team/configure', team_id,
                                 team_name = team_name,
                                 added_emails = added_emails,
                                 removed_emails = removed_emails,
                                 added_conversations = added_conversations,
                                 removed_conversations = removed_conversations)

    def team_remove(self, team_id):
        """Remove team.
        """
        return self._webapi_call('api/team/remove', team_id)

    ##
    ## payment
    ##

    def payment_conf(self):
        return self._webapi_call('api/payment/conf')

    def payment_subscribe(self, payment_token_id, card_encrypted_number,
                          card_encrypted_cvv, card_holder_name, card_expiration_month,
                          card_expiration_year, card_description, organisation_country_code,
                          organisation_member_emails, organisation_vat_number = None,
                          organisation_discount_code = None, organisation_name = None,
                          organisation_address = None, organisation_city = None,
                          organisation_region = None, organisation_postal_code = None,
                          organisation_phone_number = None, organisation_email = None):
        return self._webapi_call('api/payment/subscribe',
                                 payment_token_id = payment_token_id,
                                 card_encrypted_number = card_encrypted_number,
                                 card_encrypted_cvv = card_encrypted_cvv,
                                 card_holder_name = card_holder_name,
                                 card_expiration_month = card_expiration_month,
                                 card_expiration_year = card_expiration_year,
                                 card_description = card_description,
                                 organisation_country_code = organisation_country_code,
                                 organisation_member_emails = organisation_member_emails,
                                 organisation_vat_number = organisation_vat_number,
                                 organisation_discount_code = organisation_discount_code,
                                 organisation_name = organisation_name,
                                 organisation_address = organisation_address,
                                 organisation_city = organisation_city,
                                 organisation_region = organisation_region,
                                 organisation_postal_code = organisation_postal_code,
                                 organisation_phone_number = organisation_phone_number,
                                 organisation_email = organisation_email)

    ##
    ## search
    ##

    def search(self, keywords, conversation_id=None, need_suggestions = False, is_extended_search=False, search_types=None):
        return self._webapi_call('api/search',
                                 is_extended_search = is_extended_search,
                                 keywords = keywords,
                                 conversation_id = conversation_id,
                                 need_suggestions = need_suggestions,
                                 search_types = search_types)

    def search_reset(self):
        return self._webapi_call('api/search/reset')

    ##
    ## tasks
    ##

    def task_list(self, conversation_id, sync_horizon = None, is_archive = None):
        self._webapi_call('api/task/list', conversation_id,
                          sync_horizon = sync_horizon,
                          is_archive = is_archive)

    def task_create(self, conversation_id, message, from_message_nr = None,
                    attachments = None, assignee_ids = None):
        self._webapi_call('api/task/create', conversation_id,
                          message = message,
                          from_message_nr = from_message_nr,
                          attachments = attachments,
                          assignee_ids = assignee_ids)

    def task_done(self, conversation_id, message_nr, from_message_nr = None):
        self._webapi_call('api/task/done', conversation_id,
                          message_nr = message_nr,
                          from_message_nr = from_message_nr)

    def task_todo(self, conversation_id, message_nr, from_message_nr = None):
        self._webapi_call('api/task/todo', conversation_id,
                          message_nr = message_nr,
                          from_message_nr = from_message_nr)

    def task_sort(self, conversation_id, message_nr, below_task_weight = None, is_my_tasklist = None, from_message_nr = None):
        self._webapi_call('api/task/sort', conversation_id,
                          message_nr = message_nr,
                          below_task_weight = below_task_weight,
                          is_my_tasklist = is_my_tasklist,
                          from_message_nr = from_message_nr)

    def task_make(self, conversation_id, message_nr, from_message_nr = None):
        self._webapi_call('api/task/make', conversation_id,
                          message_nr = message_nr,
                          from_message_nr = from_message_nr)

    def task_assign(self, conversation_id, message_nr, assignee_ids = None, from_message_nr = None):
        self._webapi_call('api/task/assign', conversation_id,
                          message_nr = message_nr,
                          assignee_ids = assignee_ids,
                          from_message_nr = from_message_nr)

    def task_archive(self, conversation_id, message_nr, from_message_nr = None):
        self._webapi_call('api/task/archive', conversation_id,
                          message_nr = message_nr,
                          from_message_nr = from_message_nr)

    def task_activate(self, conversation_id, message_nr, from_message_nr = None):
        self._webapi_call('api/task/activate', conversation_id,
                          message_nr = message_nr,
                          from_message_nr = from_message_nr)