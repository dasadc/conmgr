# -*- coding: utf-8 -*-
#

from google.appengine.ext import ndb


def qdata_key(year=2015):
    "問題データのparent"
    return ndb.Key('Qdata', year)

def userlist_key():
    "UserInfoのparent"
    return ndb.Key('Users', 'all')

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

class QuestionList(ndb.Model):
    "コンテスト用の、出題問題リスト"
    q = ndb.KeyProperty(kind=Question)
    num = ndb.IntegerProperty()

class Answer(ndb.Model):
    "回答データ"
    anum = ndb.IntegerProperty(indexed=True)
    text = ndb.StringProperty(indexed=False)
    owner = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class AnswerInfo(ndb.Model):
    "回答データの補足情報"
    anum = ndb.IntegerProperty(indexed=True)
    cpu_sec = ndb.FloatProperty(indexed=False)
    mem_byte = ndb.IntegerProperty(indexed=False)
    misc_text = ndb.StringProperty(indexed=False)
    result = ndb.StringProperty() # 採点結果
