# -*- coding: utf-8 -*-
#
# アルゴリズムデザインコンテスト 2015
#
# Web部分
#
# 一応、RESTful Web APIのつもり

from flask import Flask, request, redirect, session, escape, url_for, json, make_response, render_template
import adcconfig
import adcusers
from adcutil import *

app = Flask(__name__)
app.config.from_object(adcconfig)
app.config.from_object(adcusers)
app.secret_key = app.config['SECRET_KEY']

# Google App Engineでpytzを使うのはディスクの無駄遣いらしい
#tz = pytz.timezone(app.config['TZ'])  # time zone

def priv_admin():
    "ログイン中であり、admin権限をもったユーザか？"
    return ('login' in session and session['login']==1 and
            'gid' in session and session['gid']==0 )

def authenticated():
    "ログインしてユーザ認証済のユーザか？"
    return ('login' in session and session['login']==1)

def username_matched(username):
    "ログイン中であり、ユーザ名がusernameに一致しているか？"
    return ('login' in session and session['login']==1 and session['username']==username)

def request_is_json():
    if ('Accept' in request.headers and
        request.headers['Accept'] == 'application/json'):
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if authenticated():
        session['times'] += 1
        msg = "You are already logged-in, %s, %s, %d times" % (escape(session['username']), escape(session['displayName']), session['times'])
        return adc_response(msg, request_is_json())
    if request.method == 'GET':
        return render_template('login.html')
    if request.headers['Content-Type'] == 'application/json':
        try:
            req = json.loads(request.data)
        except ValueError:
            return adc_response("JSON decode error", True, 400)
        if not('username' in req) or not('password' in req):
            return adc_response("username and password are required", True, 400)
        username = req['username']
        password = req['password']
    elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        username = request.form['username']
        password = request.form['password']
    else:
        return adc_response("bogus login request", request_is_json(), 400)
    u = adc_login(app.config['SALT'], username, password, app.config['USERS'])
    if u is None:
        return adc_response("login failed", request_is_json(), 401)
    session['login'] = 1
    session['username'] = username
    session['displayName'] = u[2]
    session['uid'] = u[3]
    session['gid'] = u[4]
    session['times'] = 1
    return adc_response("login OK", request_is_json())

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if authenticated():
        for i in ['login', 'username', 'displayName', 'uid', 'gid']:
            del session[i]
        return adc_response("logout OK", request_is_json())
    else:
        return adc_response("not login yet", request_is_json(), 401)
    
@app.route('/whoami', methods=['GET'])
def whoami():
    if authenticated():
        return adc_response(session['username'], request_is_json())
    else:
        return adc_response("not login yet", request_is_json(), 401)
    
@app.route('/admin/user', methods=['GET'])
def admin_user_list_get():
    "ユーザー一覧リスト"
    if not authenticated():
        return adc_response("access forbidden", request_is_json(), 403)
    res = adc_get_user_list(app.config['USERS'])
    txt = json.dumps(res)
    #print "res=",res
    #print "txt=",txt
    return adc_response(txt, True, json_encoded=True)

@app.route('/admin/user/<username>', methods=['GET'])
def admin_user_get(username):
    if ( not authenticated() or
         (not priv_admin() and session['username'] != username) ):
        return adc_response("access forbidden", request_is_json(), 403)
    u = adc_get_user_info(username, app.config['USERS'])
    if u is None:
        return adc_response("not found", request_is_json(), 404)
    else:
        msg = "%s:%s:%d:%d" % (u[0], u[2], u[3], u[4])
        return adc_response(msg, request_is_json())

@app.route('/admin/user/<username>', methods=['POST','DELETE'])
def admin_user_post(username):
    """
    アカウント作成、アカウント削除
    admin権限がある人だけ可能
    """
    if not priv_admin():
        return adc_response("access forbidden", request_is_json(), 403)
    # POSTの場合、アカウント削除
    if request.method == 'DELETE':
        ret = delete_user(username)
        msg = "delete user %s %d" % (username, ret)
        return adc_response_text(msg)
    # POSTの場合、アカウント作成
    if request.headers['Content-Type'] == 'application/json':
        req = request.get_json()
        #print "req=", req
        if username != req['username']:
            return adc_response("username mismatch error", True, 400)
        ret = create_user(req['username'], req['password'], req['displayname'], req['uid'], req['gid'], app.config['SALT'])
        msg = "create user %s" % username
        return adc_response(msg, True)
    else:
        return adc_response("input data error", True, 400)

@app.route('/admin/Q/all', methods=['GET'])
def admin_Q_all():
    "データベースに登録されたすべての問題の一覧リスト"
    if not priv_admin():
        return adc_response("access forbidden", request_is_json(), 403)
    msg = get_admin_Q_all()
    return adc_response_text(msg)

@app.route('/admin/Q/list', methods=['GET','PUT','DELETE'])
def admin_Q_list():
    "コンテストの出題リスト"
    if not priv_admin():
        return adc_response("access forbidden", request_is_json(), 403)
    if request.method == 'GET':
        msg = admin_Q_list_get()
        return adc_response_text(msg)
    elif request.method == 'PUT':
        msg = admin_Q_list_create()
        return adc_response_text(msg)
    elif request.method == 'DELETE':
        msg = admin_Q_list_delete()
        return adc_response_text(msg)
    else: # ありえない
        return adc_response_text("unknown")

@app.route('/A', methods=['GET'])
def admin_A_all():
    "データベースに登録されたすべての回答データの一覧リスト"
    if not priv_admin():
        return adc_response("access forbidden", request_is_json(), 403)
    msg = get_admin_A_all()
    return adc_response_text(msg)

@app.route('/A/<username>', methods=['GET'])
def admin_A_username(username):
    "回答データの一覧リストを返す"
    if not priv_admin():                        # 管理者ではない
        if ( app.config['TEST_MODE']==False or  # 本番モード
             not username_matched(username) ):  # ユーザ名が一致しない
            return adc_response("permission denied", request_is_json(), 403)
    ret, q, root = get_A_data(username=username)
    if not ret:
        return adc_response_text("no answer data found\n"+q, 404)
    text = ""
    for i in q: # 正常ならば1個しかないはず
        text += "A%d\n" % i.anum
    return adc_response_text(text)
    
@app.route('/A/<username>/Q/<int:a_num>', methods=['PUT','GET','DELETE'])
def a_put(username, a_num):
    "回答データを、登録する、取り出す、削除する"
    if not authenticated():
        return adc_response("not login yet", request_is_json(), 401)
    if not priv_admin():                        # 管理者ではない
        if ( not username_matched(username) ):  # ユーザ名が一致しない
            return adc_response("permission denied", request_is_json(), 403)
    if request.method=='PUT':
        atext = request.data
        result = put_A_data(a_num, username, atext)
        if result[0]:
            code = 200
        else:
            code = 403
        return adc_response_text(result[1], code)
    # GET, DELETEの場合
    if app.config['TEST_MODE']==False:  # 本番モード
        return adc_response("permission denied", request_is_json(), 403)
    delete = True if request.method=='DELETE' else False
    ret, result = get_or_delete_A_data(a_num=a_num, username=username, delete=delete)
    if not ret:
        return adc_response_text("no answer data found\n"+q, 404)
    if len(result) == 0:
        return adc_response_text("no answer data found", 404)
    text = "\n".join(result)
    return adc_response_text(text)

@app.route('/A/<username>/Q/<int:a_num>/info', methods=['GET','PUT','DELETE'])
def a_info_put(username, a_num):
    "回答データの補足情報を、登録する、取り出す、削除する"
    if not authenticated():
        return adc_response("not login yet", request_is_json(), 401)
    if not priv_admin():                        # 管理者ではない
        if ( not username_matched(username) ):  # ユーザ名が一致しない
            return adc_response("permission denied", request_is_json(), 403)
    if request.method == 'PUT':
        info = json.loads(request.data)
        result = put_A_info(a_num, username, info)
        if result[0]:
            code = 200
        else:
            code = 403
        return adc_response_text(result[1], code)
    else: # GET or DELETE
        if a_num == 0: a_num = None
        if username == '*': username = None
        delete = True if request.method == 'DELETE' else False
        ret, msg, results = get_or_delete_A_info(a_num=a_num, username=username, delete=delete)
        tmp = {'msg': msg,  'results':results }
        body = json.dumps(tmp)
        return adc_response_json(body)


@app.route('/user/<username>/Q', methods=['GET'])
def get_user_q_list(username):
    # ユーザを指定して、問題データの一覧リストを返す
    if not authenticated():
        return adc_response("not login yet", request_is_json(), 401)
    if session['gid'] != 0: # 管理者以外の場合
        if session['username'] != username: # ユーザ名チェック
            return adc_response("permission denied", request_is_json(), 403)
    msg = get_user_Q_all(username)
    return adc_response_text(msg)
    
@app.route('/user/<username>/Q/<int:q_num>', methods=['GET','PUT','POST','DELETE'])
def user_q(username, q_num):
    # ユーザを指定して、問題データを、ダウンロード、アップロード、削除
    if not authenticated():
        return adc_response("not login yet", request_is_json(), 401)
    if session['gid'] != 0: # 管理者以外の場合
        if session['username'] != username: # ユーザ名チェック
            return adc_response("permission denied", request_is_json(), 403)
        if q_num <= 0 or 4 <= q_num: # 問題番号の範囲チェック
            return adc_response("Q number is out of range", request_is_json(), 403)
    if request.method == 'GET':
        result = get_user_Q_data(q_num, username)
        return adc_response_Q_data(result)
    elif request.method == 'PUT':
        qtext = request.data
        (num, size, line_num) = update_Q_data(q_num, qtext, username )
        msg = "PUT OK update %d %s Q%d size %dx%d line_num %d" % (num, username, q_num, size[0], size[1], line_num)
        return adc_response_text(msg)
    elif request.method == 'POST':
        f = request.files['qfile']
        qtext = f.read() # すべて読み込む
        res = insert_Q_data(q_num, qtext, author=username)
        if res[0]:
            size, line_num = res[1:]
            msg = "POST OK insert %s Q%d size %dx%d line_num %d" % (username, q_num, size[0], size[1], line_num)
            code = 200
        else:
            msg = res[1]
            code = 403
        return adc_response_text(msg, code)
    elif request.method == 'DELETE':
        msg = delete_user_Q_data(q_num, author=username)
        return adc_response_text(msg)

@app.route('/Q/<int:q_num>', methods=['GET'])
def q_get(q_num):
    if not authenticated():
        return adc_response("not login yet", request_is_json(), 401)
    result = get_Q_data(q_num)
    return adc_response_Q_data(result)

@app.route('/Q', methods=['GET'])
def q_get_list():
    if not authenticated():
        return adc_response("not login yet", request_is_json(), 401)
    msg = get_Q_all()
    return adc_response_text(msg)
    

@app.route('/2015/', methods=['GET'])
def root():
    msg = r"Hello world\n"
    msg += r"Test mode: %s\n" % app.config['TEST_MODE']
    return adc_response(msg, request_is_json())


######以下、互換性のために、2014年版をコピペ。いつか削除する###################
#from flask import Flask, request
from werkzeug import secure_filename
import nlcheck
import sys
import io
from xml.sax.saxutils import escape, unescape

#app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    results = ""
    if request.method == 'POST':
        o = nlcheck.NLCheck()
        finp = request.files['inputfile']
        input = finp.read() # すべて読み込む
        #print "input=",input
        #print "finp=", finp.filename
        ftgt = request.files['targetfile']
        target = ftgt.read()
        #print "target=",target
        #print "ftgt=", ftgt.filename
        web = False
        try:
            if request.form['debug'] != "":
                o.debug = True
        except KeyError:
            # checkboxがオフのとき。何もしない
            pass
        try:
            if request.form['verbose'] != "":
                o.verbose = True
        except KeyError:
            pass
        try:
            if request.form['web'] != "":
                web = True
        except KeyError:
            pass
        out = io.BytesIO() # io.StringIO()だとTypeError: unicode argument expected, got 'str'
        #out = open("/tmp/nlcheck_log.txt","w")
        sys.stdout = out # 標準出力を付け替える
        input_data  = o.read_input_str(input)
        target_data = o.read_target_str(target)
        judges = o.check(input_data, target_data)
        print "judges = ", judges
        o.check_filename(str(secure_filename(finp.filename)),
                         str(secure_filename(ftgt.filename)))
        results += escape(out.getvalue())
        out.close()
        sys.stdout = sys.__stdout__ # もとに戻す
        if not web:
            return results

    return u'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
<title>nlcheck</title>
<pre id="results">%s</pre>
<h1>nlcheck</h1>
<form action="/" method="post" enctype="multipart/form-data">
input <input type="file" name="inputfile"><br />
target <input type="file" name="targetfile"><br />
<input type="checkbox" name="verbose" value="1" />verbose<br />
<input type="checkbox" name="debug" value="1" />debug<br />
<input type="hidden" name="web" value="1" />
<input type="submit" value="check now">
</form>
''' % results


# @app.errorhandler(404)
# def page_not_found(e):
#     """Return a custom 404 error."""
#     return 'Sorry, Nothing at this URL.', 404


# @app.errorhandler(500)
# def page_not_found(e):
#     """Return a custom 500 error."""
#     return 'Sorry, unexpected error: {}'.format(e), 500


#if __name__ == '__main__':
#    app.run(debug=True, port=8888)
