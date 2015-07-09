# -*- coding: utf-8 ; mode: python -*-
#

import os, stat, sys, json
import httplib
from urlparse import urlparse
import Cookie
import http_post
import base64

class ADCClient:
    def __init__(self):
        self.config = os.path.join( os.path.expanduser('~'), 'adcclient.json' )
        self.debug = False
        self.verbose = False
        self.username = None
        self.password = None
        self.url = "http://127.0.0.1:8080/"
        self.cookie = None
        self.output_file = None
        self.scheme = 'http'
        self.hostname = None
        self.port = None
        self.path = None
        self.http_proxy = None
        self.http_proxy_auth = None

    def read_config(self):
        try:
            with open(self.config, "r") as f:
                data = json.load(f)
                #print "data=",data
                for i in ['username', 'cookie', 'url']:
                    if i in data and data[i] is not None:
                        self.__dict__[i] = data[i].encode('utf-8')
        except IOError:
            # No such file or directoryなどの場合
            return False
        except ValueError:
            # No JSON object could be decodedなどの場合
            return False
        except:
            print "Error:", sys.exc_info()[0]
            raise
        return True
                        
    def write_config(self):
        data = { 'username': self.username,
                 'cookie': self.cookie,
                 'url': self.url }
        try:
            with open(self.config, "w") as f:
                json.dump(data, f)
            os.chmod(self.config, stat.S_IRUSR|stat.S_IWUSR)
        except:
            print "Error:", sys.exc_info()[0]
            raise

    def parse_url(self):
        o = urlparse(self.url)
        if not (o.scheme=='http' or o.scheme=='https'):
            print "Error: scheme %s is not supported", o.scheme
            return None
        self.scheme = o.scheme
        self.hostname = o.hostname
        self.port = o.port
        self.path = o.path
        if self.path is None: self.path = '/'
        self.setup_http_proxy(o.hostname)

    def setup_http_proxy(self, hostname):
        "httplibだけでやるとメンドクサイ"
        self.http_proxy = [False]
        if "http_proxy" in os.environ:
            proxy = urlparse(os.environ['http_proxy'])
            use_proxy = True
            if "no_proxy" in os.environ:
                no_proxy = os.environ["no_proxy"].split(',')
                if hostname in no_proxy:
                    return
            # http proxyを使う
            self.http_proxy = [True, proxy.hostname, proxy.port]
            if proxy.username is not None and proxy.password is not None:
                # proxy認証がある場合
                self.http_proxy_auth = 'Basic '+base64.b64encode('%s:%s' % (proxy.username, proxy.password))
                # ステータス407 Proxy Authentication Requiredを確認せずに、いきなりヘッダを送ってもいいのか？


    def http_request(self, method, path, params=None, json=True, headers={}):
        if self.path[-1]=='/' and path[0]=='/': path=path[1:] # 先頭の/は不要
        if json:
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
        else:
            if not 'Content-Type' in headers:
                headers['Content-Type'] = 'text/plain'
        self.http_cookie_header(headers)
        if self.http_proxy[0]:
            if self.http_proxy_auth is not None:
                headers['Proxy-Authorization'] = self.http_proxy_auth
            conn = httplib.HTTPConnection(self.http_proxy[1], self.http_proxy[2])
            port = '' if self.port is None else ':%d' % self.port
            path2 = '%s://%s%s%s%s' % (self.scheme, self.hostname, port, self.path, path)
        else:
            port = self.port
            if port is None: port = 80
            conn = httplib.HTTPConnection(self.hostname, port)
            path2 = self.path + path
        #print "path2=",path2
        conn.request(method, path2, params, headers)
        response = conn.getresponse()
        data = response.read()
        res = [response.version,
               response.status,
               response.reason,
               response.getheader('Content-Type'),
               response.getheader('Set-Cookie'),
               data]
        conn.close()
        return res

    def http_post_multipart(self, path, fields, files):
        content_type, body = http_post.encode_multipart_formdata(fields, files)
        headers = {'Content-Type': content_type,
                   'Content-Length': str(len(body))}
        #print "headers=",headers
        #print "body=",body
        return self.http_request('POST', path, params=body, json=False, headers=headers)


    def http_cookie_header(self, headers):
        if self.cookie is not None:
            C = Cookie.SimpleCookie()
            C.load(self.cookie)
            # C['session']['path']
            # C['session']['httponly']
            if 'session' in C:
                value = 'session=' + C['session'].coded_value
                headers['Cookie'] = value;

    def fin(self, res):
        #print res
        if res[1] == 200:
            if self.debug: print "Success", res[1], res[2], "\n" #, res[5]
            self.cookie = res[4]
        else:
            if self.debug: print "Failed", res[1], res[2], "\n" #, res[5]
        #print type(res[5]), res[5]
        if res[3] is None:
            info = {'msg': res[5]}
        else:
            contenttype = res[3].split(';')
            if contenttype[0] == 'application/json':
                info = json.loads(res[5])
            else:
                info = {'msg': res[5]}
            if self.verbose: print info['msg']
        res.append(info)
        return res

    def login(self, args):
        self.parse_url()
        info = {'username': self.username,
                'password': self.password }
        params = json.dumps(info)
        res = self.http_request('POST', '/login', params=params)
        return self.fin(res)

    def logout(self, args):
        self.parse_url()
        res = self.http_request('GET', '/logout')
        return self.fin(res)

    def whoami(self, args):
        self.parse_url()
        res = self.http_request('GET', '/whoami')
        return self.fin(res)

    def get_root(self, args):
        self.parse_url()
        res = self.http_request('GET', '/2015/')
        return self.fin(res)

    def get_user_list(self):
        self.parse_url()
        res = self.http_request('GET', '/admin/user')
        return self.fin(res)

    def get_user_info(self, args):
        self.parse_url()
        res2 = []
        if len(args) == 0:
            args = [self.username]
        for username in args:
            path = '/admin/user/%s' % username
            res = self.http_request('GET', path)
            res2.append(self.fin(res))
        return res2

    def create_user(self, args):
        self.parse_url()
        info = {'username': args[0],
                'password': args[1],
                'displayname': args[2],
                'uid': int(args[3]),
                'gid': int(args[4])}
        params = json.dumps(info)
        path = '/admin/user/%s' % args[0]
        res = self.http_request('POST', path, params=params)
        return self.fin(res)
    
    def create_users(self, file):
        glo = {}
        execfile(file, glo)
        res2 = []
        for u in glo['USERS']:
            res2.append( self.create_user(u) )
        return res2

    def delete_user(self, username):
        self.parse_url()
        info = {'username': username}
        params = json.dumps(info)
        path = '/admin/user/%s' % username
        res = self.http_request('DELETE', path, json=False)
        return self.fin(res)

    def delete_users(self, args):
        res2 = []
        for username in args:
            res2.append( self.delete_user(username) )
        return res2

    def get_admin_q_all(self, args):
        self.parse_url()
        res = self.http_request('GET', '/admin/Q/all')
        return self.fin(res)

    def get_admin_a_all(self, args):
        self.parse_url()
        res = self.http_request('GET', '/A')
        return self.fin(res)

    def get_admin_q_list(self, args):
        self.parse_url()
        res = self.http_request('GET', '/admin/Q/list')
        return self.fin(res)

    def put_admin_q_list(self, args):
        self.parse_url()
        res = self.http_request('PUT', '/admin/Q/list', params="dummy", json=False)
        return self.fin(res)

    def get_q(self, args):
        self.parse_url()
        if len(args) == 0:
            res = self.http_request('GET', '/Q')
            return self.fin(res)
        else:
            res2 = []
            for i in args:
                path = '/Q/%d' % int(i)
                res = self.http_request('GET', path)
                res2.append(self.fin(res))
            return res2

    def get_a(self, args):
        self.parse_url()
        if len(args) == 0:
            path = '/A/%s' % self.username
            res = self.http_request('GET', path)
            return self.fin(res)
        else:
            res2 = []
            for i in args:
                path = '/A/%s/Q/%d' % (self.username, int(i))
                res = self.http_request('GET', path)
                res2.append(self.fin(res))
            return res2

    def put_a(self, a_num, a_file):
        "PUT /A/<username>/Q/<Q-number>"
        self.parse_url()
        path = '/A/%s/Q/%d' % (self.username, a_num)
        with open(a_file, "r") as f:
            a_text = f.read()
        res = self.http_request('PUT', path, params=a_text, json=False)
        return self.fin(res)

    def get_user_q(self, args):
        "GET /user/<username>/Q/<Q-number>"
        self.parse_url()
        if len(args) == 0:
            path = '/user/%s/Q' % self.username
            res = self.http_request('GET', path)
            return self.fin(res)
        else:
            res2 = []
            for i in args:
                path = '/user/%s/Q/%d' % (self.username, int(i))
                res = self.http_request('GET', path)
                res2.append(self.fin(res))
            return res2

    def post_user_q(self, q_num, q_file):
        "POST /user/<username>/Q/<Q-number>"
        self.parse_url()
        path = "/user/%s/Q/%d" % (self.username, q_num)
        with open(q_file, "r") as f:
            q_text = f.read()
        filename = os.path.basename(q_file)
        files = [('qfile', filename, q_text)]
        fields = []
        res = self.http_post_multipart( path, fields, files)
        return self.fin(res)
        
    def put_user_q(self, q_num, q_file):
        "PUT /user/<username>/Q/<Q-number>"
        self.parse_url()
        path = "/user/%s/Q/%d" % (self.username, q_num)
        with open(q_file, "r") as f:
            q_text = f.read()
        res = self.http_request('PUT', path, params=q_text, json=False)
        return self.fin(res)

    def delete_user_q(self, q_num):
        "DELETE /user/<username>/Q/<Q-number>"
        self.parse_url()
        path = "/user/%s/Q/%d" % (self.username, q_num)
        res = self.http_request('DELETE', path, json=False)
        return self.fin(res)

    def delete_a(self, a_num):
        self.parse_url()
        path = "/A/%s/Q/%d" % (self.username, a_num)
        res = self.http_request('DELETE', path, json=False)
        return self.fin(res)