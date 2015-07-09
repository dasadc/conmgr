# -*- coding: utf-8 ; mode: python -*-
#
# I found this code here (Thanks!):
#   http://stackoverflow.com/questions/680305/using-multipartposthandler-to-post-form-data-with-python
#
# post_multipart():  added argument xheaders and return values 

import httplib
import mimetypes

# def post_multipart(host, selector, fields, files, xheaders={}):
#     content_type, body = encode_multipart_formdata(fields, files)
#     h = httplib.HTTP(host)
#     h.putrequest('POST', selector)
#     for key,val in xheaders.iteritems():
#         h.putheader(key, val)
#     h.putheader('content-type', content_type)
#     h.putheader('content-length', str(len(body)))
#     h.endheaders()
#     h.send(body)
#     errcode, errmsg, headers = h.getreply()
#     return h.file.read(), errcode, errmsg, headers

def encode_multipart_formdata(fields, files):
    LIMIT = '----------lImIt_of_THE_fIle_eW_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + LIMIT)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + LIMIT)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + LIMIT + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % LIMIT
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
