#!/usr/bin/env python

# test_twisted_server.py
# Copyright (C) 2011 ParIT Worker Co-operative <transparency@parit.ca>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Author(s): Mark Jenkins <mark@parit.ca>

from twisted.web import server, resource
from twisted.internet import utils, reactor, protocol
from datetime import datetime, timedelta
from glob import iglob
from os.path import \
    join as path_join, getmtime, split as path_split, splitext, exists
from os import listdir, getcwd
from threading import Thread, Condition

from ZODB import DB
from persistent import Persistent
from BTrees.OOBTree import OOSet
import transaction

request_list = []
current_upload = None
current_upload_file = None

START = "start"
END = "end"
DATE = "date"
TIME = "time"
STARTDATE = START + DATE
STARTTIME = START + TIME
ENDDATE = END + DATE
ENDTIME = END + TIME
YEAR = "year"
MONTH = "month"
DAY = "day"


ARCHIVE_PATH=getcwd()
UPLOAD_CMD="./test.sh"

def filemod_in_datetime_range(file_path, startdatetime, enddatetime,
                              offset_minutes=0):
    offset = timedelta(minutes=offset_minutes)
    comparison_time = datetime.fromtimestamp(getmtime(file_path)) + offset
    return comparison_time >= startdatetime and \
        comparison_time <= enddatetime

def gen_files_in_datetime_range(startdatetime, enddatetime):
    return (
        file_path
        for file_path in iglob(
            path_join(ARCHIVE_PATH, '????-??-??', '*.mp3'))
        if filemod_in_datetime_range(file_path,
                                     startdatetime, enddatetime,
                                     -2*60+1)
        )
        
def gen_files_after_timestamp(timestamp):
    return (
        file_path for file_path in iglob(
            path_join(ARCHIVE_PATH, '????-??-??', '*.mp3')
        )
        if get_timestamp_from_filename(file_path) > timestamp
    )

def gen_select_list(name, label, list_items):
    return """%s <select name="%s">
%s
</select>
""" % (label, name, '\n'.join("<option>%s</option>" % option
                              for option in list_items) )

def gen_time_html(name):
    return gen_select_list(name, "Select time: ",
                            xrange(0, 24, 2) )

def gen_date_html(name):
    nowdate = datetime.today()
    return '\n'.join((
            gen_select_list(name + YEAR, "Year: ",
                        xrange(nowdate.year - 2, nowdate.year+1) ),
            gen_select_list(name + MONTH, "Month: ",
                            xrange(1, 12+1) ),
            gen_select_list(name + DAY, "Day: ",
                            xrange(1, 31+1) ),
            ))
                        
def extract_datetime(start_or_end, args):
    return datetime( *tuple( int(args[start_or_end + suffix][0])
                             for suffix in (DATE + YEAR,
                                            DATE + MONTH,
                                            DATE + DAY,
                                            TIME) ) )

class FileUploadCheckChange(resource.Resource):
    isLeaf = True
    
    def __init__(
        self,
        stuff_to_add_or_del_cond,
        stuff_to_add, stuff_to_del,
        *args, **kargs):
        global request_list

        resource.Resource.__init__(self, *args, **kargs)
        
        self.stuff_to_add_or_del_cond = stuff_to_add_or_del_cond
        self.stuff_to_add = stuff_to_add
        self.stuff_to_del = stuff_to_del

        if len(request_list) > 0:
            self.queue_latest_upload_set_cb()
                        
    def render_GET(self, request, error_msg=""):
        global current_upload, current_upload_file, request_list
        return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>File re-upload</title>
</head>
<body>
%s
<br />
<form action="/reupload/" method="post">
<strong>Start</strong> %s %s
<br />
<strong>End</strong> %s %s
<br />
<input type="submit"></input>
</form>
<hr />
<form action="/reupload" method="post">
<input type="submit" name="stop" value="stop"></input>
</form>
<hr />

<p>
Currently uploading: %s
<br />
Also in queue:
<pre>
%s
</pre>
</p>
</body>
</html>
""" % (error_msg,
       gen_time_html(STARTTIME), gen_date_html(STARTDATE),
       gen_time_html(ENDTIME), gen_date_html(ENDDATE),
       str(current_upload_file), '\n'.join(request_list) )

    def queue_upload_of_files(self, files_to_add):
        global current_upload, current_upload_file, request_list

        self.stuff_to_add_or_del_cond.acquire()
        self.stuff_to_add.extend(files_to_add)
        request_list.extend(files_to_add)
        self.stuff_to_add_or_del_cond.notify()
        self.stuff_to_add_or_del_cond.release()
        
        if current_upload == None and len(request_list) > 0:
            self.queue_latest_upload_set_cb()
        
    def render_POST(self, request):
        global current_upload, current_upload_file, request_list
       
        error_msg = ""
        if 'stop' in request.args:
            request_list = []
            error_msg = "stoping as requested"
        elif request.path == "/specific_file":
            if "upload" in request.args:
                self.queue_upload_of_files(request.args["upload"])
        else:
            try:
                startdatetime = extract_datetime(START, request.args)
                enddatetime = extract_datetime(END, request.args)
            except ValueError:
                error_msg = "Problem with date/time"
            else:
                if startdatetime > enddatetime:
                    error_msg = "Start date/time is later then end"
                else:
                    self.queue_upload_of_files(
                        tuple(
                            gen_files_in_datetime_range(startdatetime,
                                                        enddatetime) )
                    )

        return self.render_GET(request, error_msg)


    def queue_latest_upload_set_cb(self):
        global request_list, current_upload, current_upload_file
        current_upload_file = request_list.pop()
        # only queue files that exist, otherwise forget about them
        # move on to the next
        while not exists(current_upload_file):

            # tell the worker thread that current_upload_file
            # doesn't exist
            self.tell_worker_thread_we_are_done_with_file(current_upload_file)
            
            if len(request_list) > 0:
                current_upload_file = request_list.pop()
            else:
                current_upload_file = None
                current_upload = None
                return #  spaghetti exit!

        # this point only reached if the return statement above is never hit, 
        # that is current_upload_file is a file that exists
        current_upload = utils.getProcessValue(
            UPLOAD_CMD, [current_upload_file])
        current_upload.addCallback(self.upload_done)        

    def tell_worker_thread_we_are_done_with_file(self, filename):
        self.stuff_to_add_or_del_cond.acquire()
        self.stuff_to_del.append(filename)
        self.stuff_to_add_or_del_cond.notify()
        self.stuff_to_add_or_del_cond.release()
        
    def upload_done(self, exit_code):
        global request_list, current_upload, current_upload_file

        if exit_code == 0:
            self.tell_worker_thread_we_are_done_with_file(current_upload_file)
            if len(request_list) >0 :
                self.queue_latest_upload_set_cb()
            else:
                current_upload = None
                current_upload_file = None
        elif exit_code == 1:
            request_list.append(current_upload_file)
            self.queue_latest_upload_set_cb()


def get_timestamp_from_filename(filename):
    filename_part = path_split(filename)[1] # [1] gets tail
    namepart, extension = splitext(filename_part)
    try:
        return int(namepart)
    except ValueError:
        return 0
            
def update_most_recent_upload(conn, newest_upload):
    if conn.root.most_recent_upload_by_stamp != None:
        most_recent_timestamp = get_timestamp_from_filename(
            conn.root.most_recent_upload_by_stamp)
    else:
        most_recent_timestamp = 0

    timestamp = get_timestamp_from_filename(newest_upload)
    if timestamp > most_recent_timestamp:
        conn.root.most_recent_upload_by_stamp = newest_upload
            

def persist_thread_run(
        stuff_to_add_or_del_cond, 
        stuff_to_add, stuff_to_del, check_keep_going,
        db
        ):
    conn = db.open()

    # acquire for our fist time through
    stuff_to_add_or_del_cond.acquire()

    while True:
        if len(stuff_to_add) > 0 or len(stuff_to_del) > 0:
            conn.root.uploads_to_happen.update(stuff_to_add)
            for del_this in stuff_to_del:
                conn.root.uploads_to_happen.remove(del_this)
                update_most_recent_upload(conn, del_this)
            # delete all the entries, python 3.3 has added a clear() method
            # which would have been prettier
            del stuff_to_add[:]
            del stuff_to_del[:]
            stuff_to_add_or_del_cond.release()

            
            # and this ladies and gentlemen is the point of having a worker
            # thread for the database work, as this is
            transaction.commit()

            # re-acquire the condition as we're going to go back to the
            # top and check if anything changed while we were working
            stuff_to_add_or_del_cond.acquire()

        elif not check_keep_going():
            stuff_to_add_or_del_cond.release()
            break
        else:
            stuff_to_add_or_del_cond.wait()

    conn.close()
            
def main():
    global request_list

    db = DB('uploads.fs')
    conn = db.open()
    if not hasattr(conn.root, 'uploads_to_happen'):
        conn.root.uploads_to_happen = OOSet()

    if not hasattr(conn.root, 'most_recent_upload_by_stamp'):
        conn.root.most_recent_upload_by_stamp = None

    transaction.commit()

    # look for any files with a timestamp later than our latest
    if conn.root.most_recent_upload_by_stamp != None:
        conn.root.uploads_to_happen.update(
            gen_files_after_timestamp(get_timestamp_from_filename(
                conn.root.most_recent_upload_by_stamp)) )
        transaction.commit()
    
    request_list.extend(conn.root.uploads_to_happen)

    server_should_run = True
    def check_keep_going():
        return server_should_run


    stuff_to_add_or_del_cond = Condition()
    stuff_to_add = []
    stuff_to_del = []

    def persist_thread_routine():
        persist_thread_run( stuff_to_add_or_del_cond, 
                            stuff_to_add, stuff_to_del, check_keep_going, db)
    
    persist_thread = Thread(target=persist_thread_routine)
    persist_thread.start()
    
    site = server.Site(FileUploadCheckChange(
            stuff_to_add_or_del_cond,
            stuff_to_add, stuff_to_del,
            ))

    reactor.listenTCP(8888, site)
    reactor.run()

    # we should be sure that there is no possibility that our database thread 
    stuff_to_add_or_del_cond.acquire()
    server_should_run = False
    stuff_to_add_or_del_cond.notify()
    stuff_to_add_or_del_cond.release()
    persist_thread.join()

    
if __name__ == '__main__':
    main()
