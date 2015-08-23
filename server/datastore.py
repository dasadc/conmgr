# -*- coding: utf-8 -*-
#

from google.appengine.ext import ndb


def qdata_key(year=2015):
    "問題データのparent"
    return ndb.Key('Qdata', str(year))

def userlist_key():
    "UserInfoのparent"
    return ndb.Key('Users', 'all')

def log_key():
    "問題データのparent"
    return ndb.Key('Log', 'root')

class UserInfo(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    displayname = ndb.StringProperty()
    uid = ndb.IntegerProperty()
    gid = ndb.IntegerProperty()

class Question(ndb.Model):
    "問題データ"
    qnum   = ndb.IntegerProperty(indexed=True)
    text = ndb.StringProperty(indexed=False)
    rows = ndb.IntegerProperty()
    cols = ndb.IntegerProperty()
    linenum = ndb.IntegerProperty()
    author = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class QuestionListAll(ndb.Model):
    "コンテスト用の、出題問題リスト。Repeated Propetiyにしてみた"
    qs = ndb.KeyProperty(kind=Question, repeated=True)
    text_admin = ndb.StringProperty('a', indexed=False)
    text_user = ndb.StringProperty('u', indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Answer(ndb.Model):
    "回答データ"
    anum = ndb.IntegerProperty(indexed=True)
    text = ndb.StringProperty(indexed=False)
    owner = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    # 回答データの補足情報
    cpu_sec = ndb.FloatProperty(indexed=False)
    mem_byte = ndb.IntegerProperty(indexed=False)
    misc_text = ndb.StringProperty(indexed=False)
    result = ndb.StringProperty()  # 採点結果
    judge = ndb.IntegerProperty()  # True=1=正解, False=0=不正解
    q_factor = ndb.FloatProperty() # 解の品質

class Log(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    username = ndb.StringProperty()
    what = ndb.StringProperty()

class TimeKeeper(ndb.Model):
    lastUpdate = ndb.DateTimeProperty()
    state = ndb.StringProperty()
    enabled = ndb.IntegerProperty() # 0=disabled, 1=enabled
