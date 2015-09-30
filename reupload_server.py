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
from os.path import join as path_join, getmtime
from os import listdir

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


ARCHIVE_PATH="/home/archives/128/"
UPLOAD_CMD="/usr/local/bin/upload_archive_file.sh"

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

    def render_POST(self, request):
        global current_upload, current_upload_file, request_list

        error_msg = ""
        if 'stop' in request.args:
            request_list = []
            error_msg = "stoping as requested"
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
                    request_list.extend(
                        gen_files_in_datetime_range(startdatetime,
                                                    enddatetime))

                    if current_upload == None and len(request_list) > 0:
                        self.queue_latest_upload_set_cb()

        return self.render_GET(request, error_msg)


    def queue_latest_upload_set_cb(self):
        global request_list, current_upload, current_upload_file
        current_upload_file = request_list.pop()
        current_upload = utils.getProcessValue(
            UPLOAD_CMD, [current_upload_file])
        current_upload.addCallback(self.upload_done)        

    def upload_done(self, exit_code):
        global request_list, current_upload, current_upload_file
        if len(request_list) >0 :
            self.queue_latest_upload_set_cb()
        else:
            current_upload = None
            current_upload_file = None

def main():
    site = server.Site(FileUploadCheckChange())
    reactor.listenTCP(8888, site)
    reactor.run()

if __name__ == '__main__':
    main()
