#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################

from osv import osv, fields
from tools.translate import _
from datetime import datetime
from datetime import timedelta
import time
import caldav
import pytz
from pytz import timezone


class caldav_calendar(osv.osv):

    _name = "caldav.calendar"
    _columns = {
        'name': fields.char('Name', size=128),
        'user_id': fields.many2one('res.users', 'User'),
        'selected': fields.boolean('Selected'),
    }

caldav_calendar()

class res_users(osv.osv):

    _name = "res.users"
    _inherit = "res.users"

    _columns = {
        'caldav_usr': fields.char('User', size=64, required=True),
        'caldav_pwd': fields.char('Password', size=64, required=True),
        'caldav_ssl': fields.boolean('Use SSL'),
        'caldav_url': fields.char('CalDav URL', size=256, required=True),
        'caldav_server_url': fields.char('CalDav Server URL', size=256, required=True),
        'caldav_state': fields.selection([('disabled','Disabled'),('validated','Validated'),
            ('error','Error')], 'State', readonly=True),
#        'caldav_calendar_ids': fields.one2many('caldav.calendar', 'user_id', 'Calendars'),
        'caldav_log': fields.text('Log', readonly=True),
        'caldav_ignore_past': fields.boolean('Ignore Past Event'),
    }

    _defautls = {
        'caldav_ssl': True,
        'caldav_state': 'disabled',
    }

    def caldav_client_validate(self, cr, uid, ids, context=None):
        """ Check the CaldDAV server connection and validate it """
        user = self.pool.get('res.users').browse(cr, uid, ids[0])

        # Cleaning up URL
        url = user.caldav_server_url
        if url[:8] == 'https://':
            url = url[8:]
        elif url[:7] == 'http://':
            url = url[7:]
        
        if url.find('@') != -1:
            url = url[url.find('@') + 1:]

        if not user.caldav_ssl:
            cdav_url = 'http://' + user.caldav_usr + ':' + user.caldav_pwd + '@' + url                             
        else:
            cdav_url = 'https://' + user.caldav_usr + ':' + user.caldav_pwd + '@' + url                             

        try:    
            client = caldav.DAVClient(cdav_url)
            principal = caldav.Principal(client, cdav_url)
            calendars = principal.calendars()
            if not calendars:
                raise osv.except_osv(_('CalDav Client Error'), _('No calendars found for user %s'%(user.name)))

            log = '%s INFO Successfully connected to %s\n'%(time.strftime('%Y-%m-%d %H:%M:%S'), url) + (user.caldav_log or "")
            self.write(cr, uid, ids, {'caldav_url':cdav_url, 'caldav_state':'validated', 'caldav_log':log})

#            Draft for multi-calendar management
#            for calendar in calendars:
#                print "CAL:",calendar
#                print dir(calendar)
#                cal_id = self.pool.get('caldav.calendar').create(cr, uid, {'name':calendar})

        except Exception, exception:
            log = '%s ERROR Unable to connect to %s\n'%(time.strftime('%Y-%m-%d %H:%M:%S'), url) + (user.caldav_log or "")
            self.write(cr, uid, ids, {'caldav_url':False, 'caldav_log':log})

        return True

    def caldav_client_disable(self, cr, uid, ids, context=None):
        """ Disable CalDAV sync for a user """
        user = self.pool.get('res.users').browse(cr, uid, ids[0])
        log = '%s INFO Disconected from %s\n'%(time.strftime('%Y-%m-%d %H:%M:%S'), user.caldav_server_url) + (user.caldav_log or "")
        self.write(cr, uid, ids, {'caldav_url':False, 'caldav_log':log, 'caldav_state':'disabled'})
        return True

    def _meeting_create(self, cr, uid, data, context=None):
        """Create the meeting"""
        context['from_caldav'] = True
        vals = {}
  
        # Search for an existing meeting
        #meeting = self.pool.get('crm.meeting').search(cr, uid, [('caldav_uid','=',data['VCALENDAR']['VEVENT']['UID'])])
	# Why is it returning such a strange string instead of ids ???
        cr.execute("SELECT id FROM crm_meeting WHERE caldav_uid = '%s'"%(data['VCALENDAR']['VEVENT']['UID']))
        meeting = cr.fetchone()
	if meeting:
	    meeting = meeting[0]
	print "data:",data['VCALENDAR']['VEVENT']['UID']
	#print "meeting:",meeting
	print "meeting:",meeting

        # Check if the meeting exists and has not been modified
        # WARNING: Not tested as Kerio does not send LAST-MODIFIED
        if meeting and 'LAST-MODIFIED' in data['VCALENDAR']['VEVENT']:
	    print "data:",data['VCALENDAR']['VEVENT']
	    print "meeting_id:",meeting
            cr.execute("SELECT create_date,write_date FROM crm_meeting WHERE id = %s"%(meeting))
            res = cr.fetchone()
            last_modif_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data['VCALENDAR']['VEVENT']['LAST-MODIFIED'], '%Y%m%dT%H%M%SZ'))
            if (res[1] and res[1][:19] == last_modif_date) or res[0][:19] == last_modif_date:
                return True

        # If a meeting is found, delete and recreated it in case LAST-MODIFIED is not implemented by the CalDAV server
        # because then there is no way to know if a meeting have been modified or not
        if meeting and not 'LAST-MODIFIED' in data['VCALENDAR']['VEVENT']:
            self.pool.get('crm.meeting').unlink(cr, uid, meeting, context=context)

        if 'UID' in data['VCALENDAR']['VEVENT']:
            vals['caldav_uid'] = data['VCALENDAR']['VEVENT']['UID']
        if 'SUMMARY' in data['VCALENDAR']['VEVENT']:
            vals['name'] = data['VCALENDAR']['VEVENT']['SUMMARY']
        else:
            vals['name'] = ' '

        if 'DTSTART' in data['VCALENDAR']['VEVENT']:
            if len(data['VCALENDAR']['VEVENT']['DTSTART']) == 15:  
                vals['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data['VCALENDAR']['VEVENT']['DTSTART'], '%Y%m%dT%H%M%S'))
            elif len(data['VCALENDAR']['VEVENT']['DTSTART']) == 16:
                vals['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data['VCALENDAR']['VEVENT']['DTSTART'], '%Y%m%dT%H%M%SZ'))
            elif len(data['VCALENDAR']['VEVENT']['DTSTART']) == 8:
                # When full day meeting
                vals['date'] = time.strftime('%Y-%m-%d 00:00:00', time.strptime(data['VCALENDAR']['VEVENT']['DTSTART'], '%Y%m%d'))
                vals['allday'] = True
                print "DATE:",vals['date']
            else:
                print "ERROR with DTSTART format"
            print "DATE:",vals['date']

        if 'DTEND' in data['VCALENDAR']['VEVENT']:
            if len(data['VCALENDAR']['VEVENT']['DTEND']) == 15:
                vals['date_deadline'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data['VCALENDAR']['VEVENT']['DTEND'], '%Y%m%dT%H%M%S'))
                print "DATE END:",vals['date_deadline']
                duration = datetime.strptime(data['VCALENDAR']['VEVENT']['DTEND'], '%Y%m%dT%H%M%S') - datetime.strptime(data['VCALENDAR']['VEVENT']['DTSTART'], '%Y%m%dT%H%M%S')
                vals['duration'] = float(duration.days)*24 + (float(duration.seconds)/3600)
            elif len(data['VCALENDAR']['VEVENT']['DTEND']) == 16:
                vals['date_deadline'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data['VCALENDAR']['VEVENT']['DTEND'], '%Y%m%dT%H%M%SZ'))
                print "DATE END:",vals['date_deadline']
                duration = datetime.strptime(data['VCALENDAR']['VEVENT']['DTEND'], '%Y%m%dT%H%M%SZ') - datetime.strptime(data['VCALENDAR']['VEVENT']['DTSTART'], '%Y%m%dT%H%M%SZ')
                vals['duration'] = float(duration.days)*24 + (float(duration.seconds)/3600)
            elif len(data['VCALENDAR']['VEVENT']['DTEND']) == 8:
                date_end = datetime.strptime(data['VCALENDAR']['VEVENT']['DTEND'], '%Y%m%d')
                fullday = date_end - timedelta(days=1)
                vals['date_deadline'] = datetime.strftime(fullday, '%Y-%m-%d 00:00:00')
                vals['allday'] = True
                vals['duration'] = 24
                print "DATE END:",vals['date_deadline']
            else:
                print "ERROR with DTEND format"

        # To convert the dates to UTC
        if 'VTIMEZONE' in data['VCALENDAR'] and 'TZID' in data['VCALENDAR']['VTIMEZONE']:
            tzone = timezone(data['VCALENDAR']['VTIMEZONE']['TZID'])
            date = datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S')
            date_loc = tzone.localize(date)
            date_utc = date_loc.astimezone(pytz.utc)
            vals['date'] = date_utc.strftime('%Y-%m-%d %H:%M:%S')
            print "DATE UTC:",vals['date']
            end_date = datetime.strptime(vals['date_deadline'], '%Y-%m-%d %H:%M:%S')
            end_date_loc = tzone.localize(end_date)
            end_date_utc = end_date_loc.astimezone(pytz.utc)
            vals['date_deadline'] = end_date_utc.strftime('%Y-%m-%d %H:%M:%S')
            print "END DATE UTC:",vals['date_deadline']

        if 'CLASS' in data['VCALENDAR']['VEVENT']:
            if data['VCALENDAR']['VEVENT']['CLASS'] == 'PRIVATE':
                vals['class'] = 'private'
            else:
                vals['class'] = 'public'
        if 'X-MICROSOFT-CDO-BUSYSTATUS' in data['VCALENDAR']['VEVENT']:
            if data['VCALENDAR']['VEVENT']['X-MICROSOFT-CDO-BUSYSTATUS'] == 'FREE':
                vals['show_as'] = 'free'
            elif data['VCALENDAR']['VEVENT']['X-MICROSOFT-CDO-BUSYSTATUS'] == 'BUSY':
                vals['show_as'] = 'busy'
        if 'DESCRIPTION' in data['VCALENDAR']['VEVENT']:
            vals['description'] = data['VCALENDAR']['VEVENT']['DESCRIPTION']

        # Recurring events management
        if 'RRULE' in data['VCALENDAR']['VEVENT']:
            rec_data = data['VCALENDAR']['VEVENT']['RRULE'].split(';')
            print 'RECDATA:',rec_data
            vals['recurrency'] = True
            for rec_vals in rec_data:
                rec_item = rec_vals.split('=')
                print 'RECITEM:',rec_item

                if rec_item[0] == 'FREQ':
                    freq = rec_item[1]
                    vals['interval'] = 1

                    # Set default end of recurrency at 6 month if no end date is given
                    # as OpenERP require to set a limit
                    vals['end_type'] = 'end_date'
                    end_date = datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S') + timedelta(days=180)
                    vals['end_date'] = datetime.strftime(end_date, '%Y-%m-%d %H:%M:%S')

                    # Get frequency
                    if freq == 'DAILY':
                        vals['rrule_type'] = 'daily'
                    elif freq == 'WEEKLY':
                        vals['rrule_type'] = 'weekly'
                    elif freq == 'MONTHLY':
                        vals['rrule_type'] = 'monthly'
                    elif freq == 'YEARLY':
                        vals['rrule_type'] = 'yearly'

                    # Get week day
                    mdate = datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S')
                    wday = mdate.weekday()
                    print "WEEKDAY:",mdate.weekday()

                    if wday == 6:
                        vals['su'] = True
                    elif wday == 0:
                        vals['mo'] = True
                    elif wday == 1:
                        vals['tu'] = True
                    elif wday == 2:
                        vals['we'] = True
                    elif wday == 3:
                        vals['th'] = True
                    elif wday == 4:
                        vals['fr'] = True
                    elif wday == 5:
                        vals['sa'] = True

                # Get Weekday
                if rec_item[0] == 'BYDAY':
                    # Reset default week day
                    vals['su'] = False
                    vals['mo'] = False
                    vals['tu'] = False
                    vals['we'] = False
                    vals['th'] = False
                    vals['fr'] = False
                    vals['sa'] = False

                    # Set week days
                    wdays = rec_item[1].split(',')
                    print "WDAYS:",wdays
                    if 'MO' in wdays:
                        vals['mo'] = True
                    if 'TU' in wdays:
                        vals['tu'] = True
                    if 'WE' in wdays:
                        vals['we'] = True
                    if 'TH' in wdays:
                        vals['th'] = True
                    if 'FR' in wdays:
                        vals['fr'] = True
                    if 'SA' in wdays:
                        vals['sa'] = True
                    if 'SU' in wdays:
                        vals['su'] = True

                if rec_item[0] == 'UNTIL':
                    if len(rec_item[1]) == 8:
                        vals['end_date'] = time.strftime('%Y-%m-%d 00:00:00', time.strptime(rec_item[1], '%Y%m%d'))
                    elif len(rec_item[1]) == 15:
                        vals['end_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(rec_item[1], '%Y%m%dT%H%M%S'))
                    elif len(rec_item[1]) == 16:
                        vals['end_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(rec_item[1], '%Y%m%dT%H%M%SZ'))
                    else:
                        print 'ERROR with date format'

                     
        print 'VALS:',vals


        return self.pool.get('crm.meeting').create(cr, uid, vals, context=context)
    
    def caldav_client_sync(self, cr, uid, ids, context=None):
        """ Sync CalDAV Server -> OpenERP user calendar """
        for user in self.browse(cr, uid, ids):
            client = caldav.DAVClient(user.caldav_url)
            print "CLIENT:",client
            principal = caldav.Principal(client, user.caldav_url)
            print "PRINCIPAL:",principal
            calendars = principal.calendars()
            print "CALENDARS:",calendars

            if len(calendars) > 0:
                # To improve for multi-calendars
                calendar = calendars[0]


                # Check if past event should be ignored
                # For performance issue in case LAST-MODIFIED is not send by the CalDAV server
                if user.caldav_ignore_past:
                    events = calendar.date_search(datetime.now())
                else: 
                    events = calendar.events()
                print "events to import:",len(events)
                # Get events from calendar
                i = 0
                for event in events:
                    i += 1
                    print "Importing event : ",i
                    e = event.load()
                    #print "Event:",e.data
                    #print "Event:",e.instance

                    lst_data = list(i.split(':') for i in e.data.split('\n'))

                    # Construct a hierarchical dict from the event
                    data = {}
                    parent = []
                    for item in lst_data:
                        #print 'ITEM %s'%(item)
                        if item[0] == 'BEGIN':
                            element = item[1].strip('\r')
                            if data == {}:
                                parent.append(data)
                                data[element] = {}
                                current = data[element]
                            else:
                                current[element] = {}
                                parent.append(current)
                                current = current[element]
                        elif item[0] == 'END':
                            if len(parent):
                                current = parent[-1]
                            parent.pop()
                        else:
                            if item[0] == "":
                                # Bypass last empty element
                                continue
                            elif len(item) == 1:
                                continue
                            elif item[0][:7] == 'DTSTART':
                                element = 'DTSTART'
                                current[element] = item[1].strip('\r')
                            elif item[0][:5] == 'DTEND':
                                element = 'DTEND'
                                current[element] = item[1].strip('\r')
                            else:
                                element = item[0].strip('\r')
                                current[element] = item[1].strip('\r')
                    print "DATA:",data

                    meeting_id = self._meeting_create(cr, uid, data, context=context)

                log = '%s INFO %s event successfully imported\n'%(time.strftime('%Y-%m-%d %H:%M:%S'), len(events)) + (user.caldav_log or "")
                self.pool.get('res.users').write(cr, uid, [user.id], {'caldav_log':log})


        return True

    def caldav_client_sync_all(self, cr, uid, context=None):
        # Sync CalDAV Server -> OpenERP
        user_ids = self.pool.get('res.users').search(cr, uid, [('caldav_state','=','validated')])
        return self.caldav_client_sync(cr, uid, user_ids, context)

res_users()


class crm_meeting(osv.osv):

    _name = "crm.meeting"
    _inherit = "crm.meeting"

    _columns = {
        'caldav_uid': fields.char('CalDav UID', size=64),
    }


    def create(self, cr, uid, vals, context=None):
        # Synchornize a meeting with a caldav calendar
        # NICETOHAVE: Should be possible to choose not to sync a meeting
        meeting_id = super(crm_meeting, self).create(cr, uid, vals, context=None)
        meeting = self.browse(cr, uid, meeting_id)

        # To change by meeting.responsible_id => What of meetings without responsible ?
        user = self.pool.get('res.users').browse(cr, uid, uid)
        print "MEETING CREATE CONTEXT:",context

        if user.caldav_state == 'validated' and 'from_caldav' not in context:
            # Could thread all this to speed up meeting creation
            try:
                client = caldav.DAVClient(user.caldav_url)
                principal = caldav.Principal(client, user.caldav_url)
                calendars = principal.calendars()
                if not calendars:
                   raise osv.except_osv(_('CalDav Client Error'), _('No CalDav calendar found for user %s'%(user.name)))

                if len(calendars) > 0:
                    # To improve for multi-calendars
                    calendar = calendars[0]

                    # cannot use meeting.class so use vals['class']
                    if vals['class'] in ['private','confidential']:
                        accessrule = 'CONFIDENTIAL'
                        cdclass = 'PRIVATE'
                    else:
                        accessrule = 'PUBLIC'
                        cdclass = 'PUBLIC'

                    uniqueid = 'OPENERP-' + str(time.time())
                    dtstamp = time.strftime('%Y%m%dT%H%M%SZ')

                    # Convert from UTC to user timezone
                    tzone = timezone(self.pool.get('res.users').read(cr, uid, uid, ['tz'])['tz'])
                    dtstart_utc = pytz.utc.localize(datetime.strptime(meeting.date, '%Y-%m-%d %H:%M:%S'))
                    dtstart_loc = dtstart_utc.astimezone(tzone)
                    dtstart = dtstart_loc.strftime('%Y%m%dT%H%M%S')
                    dtend_utc = pytz.utc.localize(datetime.strptime(meeting.date_deadline, '%Y-%m-%d %H:%M:%S'))
                    dtend_loc = dtend_utc.astimezone(tzone)
                    dtend = dtend_loc.strftime('%Y%m%dT%H%M%S')

                    # To avoid 'False' in meeting description
                    if not meeting.description:
                        description = ""
                    else:
                        # TOFIX: bug with \n in description
                        description = repr(meeting.description)[2:-1]

                    if meeting.show_as == 'free':
                        dispo = 'FREE'
                    elif meeting.show_as == 'busy':
                        dispo = 'BUSY'


                    vcal =  """
BEGIN:VCALENDAR
VERSION:2.0
X-CALENDARSERVER-ACCESS:%s
PRODID:-//SmartSolution//CalDAV Client//EN
BEGIN:VEVENT
UID:%s
DTSTAMP:%s
DTSTART:%s
DTEND:%s
SUMMARY:%s
DESCRIPTION:%s
CLASS:%s
X-MICROSOFT-CDO-BUSYSTATUS:%s
END:VEVENT
END:VCALENDAR
"""%(accessrule, uniqueid, dtstamp, dtstart, dtend, meeting.name, description, cdclass, dispo)

                    # Create event in calendar
                    event = caldav.Event(client, data=vcal, parent=calendar).save()
                    print "CREATED EVENT:",event

                    if event:
                        self.write(cr, uid, [meeting_id], {'caldav_uid':uniqueid}, context=context)

            except Exception, exception:
                print exception
                log = '%s ERROR Unable to create event %s\n'%(time.strftime('%Y-%m-%d %H:%M:%S'), meeting.name) + (user.caldav_log or "")
                self.pool.get('res.users').write(cr, uid, [user.id], {'caldav_log':log})

        return meeting_id

        
#    def write(self, cr, uid, ids, vals, context=None):
#        # Just resend everything after meeting modification
#        print "MEETING WRITE CONTEXT:",context
#        res = super(crm_meeting, self).write(cr, uid, ids, vals, context=context)
#
#        for meeting in self.browse(cr, uid, ids):        
#
#            # To change by meeting.responsible_id => What of meetings without responsible ?
#            user = self.pool.get('res.users').browse(cr, uid, uid)
#
#            if user.caldav_state == 'validated' and 'from_caldav' not in context:
#                # TOIMP: Could thread all this to speed up meeting creation
#                try:
#                    client = caldav.DAVClient(user.caldav_url)
#                    principal = caldav.Principal(client, user.caldav_url)
#                    calendars = principal.calendars()
#                    if not calendars:
#                       raise osv.except_osv(_('CalDav Client Error'), _('No CalDav calendar found for user %s'%(user.name)))
#
#                    if len(calendars) > 0:
#                        # To improve for multi-calendars
#                        calendar = calendars[0]
#
#                        # cannot call meeting.class so have to use a sql query
#                        cr.execute("SELECT class FROM crm_meeting WHERE id = %s"%(meeting.id))
#                        classres = cr.fetchone()
#
#                        if classres[0] in ['private','confidential']:
#                            accessrule = 'CONFIDENTIAL'
#                            cdclass = 'PRIVATE'
#                        else:
#                            accessrule = 'PUBLIC'
#                            cdclass = 'PUBLIC'
#
#                        if not meeting.caldav_uid:
#                            uniqueid = 'OPENERP-' + str(time.time())
#                        else:
#                            uniqueid = meeting.caldav_uid
#
#                        dtstamp = time.strftime('%Y%m%dT%H%M%SZ')
#                        dtstart = time.strftime('%Y%m%dT%H%M%S', time.strptime(meeting.date, '%Y-%m-%d %H:%M:%S'))
#                        dtend = time.strftime('%Y%m%dT%H%M%S', time.strptime(meeting.date_deadline, '%Y-%m-%d %H:%M:%S'))
#
#                        # To avoid 'False' in meeting description
#                        if not meeting.description:
#                            description = ""
#                        else:
#                            # To fix bug with \n in description
#                            description = repr(meeting.description)[2:-1]
#
#                        if meeting.show_as == 'free':
#                            dispo = 'FREE'
#                        elif meeting.show_as == 'busy':
#                            dispo = 'BUSY'
#
#
#                        vcal =  """
#BEGIN:VCALENDAR
#VERSION:2.0
#X-CALENDARSERVER-ACCESS:%s
#PRODID:-//SmartSolution//CalDAV Client//EN
#BEGIN:VEVENT
#UID:%s
#DTSTAMP:%s
#DTSTART:%s
#DTEND:%s
#SUMMARY:%s
#DESCRIPTION:%s
#CLASS:%s
#X-MICROSOFT-CDO-BUSYSTATUS:%s
#END:VEVENT
#END:VCALENDAR
#"""%(accessrule, uniqueid, dtstamp, dtstart, dtend, meeting.name, description, cdclass, dispo)
#                        
#                        # Create event in calendar
#                        event = caldav.Event(client, data=vcal, parent=calendar).save()
#                        print "WRITE EVENT:",event
#
#                except Exception, exception:
#                    log = '%s ERROR Unable to modify event %s\n'%(time.strftime('%Y-%m-%d %H:%M:%S'), meeting.name) + (user.caldav_log or "")
#                    self.pool.get('res.users').write(cr, uid, [user.id], {'caldav_log':log})
#
#        return True


#    def unlink(self, cr, uid, ids, context=None):
#        # delete meetings
#
#        print "MEETING DELETE CONTEXT:",context
#        for meeting in self.browse(cr, uid, ids):        
#
#            # To change by meeting.responsible_id => What of meetings without responsible ?
#            user = self.pool.get('res.users').browse(cr, uid, uid)
#
#            if user.caldav_state == 'validated' and 'from_caldav' not in context:
#                # Could thread all this to speed up meeting creation
#                    client = caldav.DAVClient(user.caldav_url)
#                    principal = caldav.Principal(client, user.caldav_url)
#                    calendars = principal.calendars()
#                    if not calendars:
#                       raise osv.except_osv(_('CalDav Client Error'), _('No CalDav calendar found for user %s'%(user.name)))
#
#                    if len(calendars) > 0:
#                        # To improve for multi-calendars
#                        calendar = calendars[0]
#                    
#                    if meeting.caldav_uid:
#                        event = calendar.event(meeting.caldav_uid)
#                        delres = event.delete()
#
#            res = super(crm_meeting, self).unlink(cr, uid, ids, context=context)
#
#        return True
    

crm_meeting()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
