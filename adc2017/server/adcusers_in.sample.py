# -*- coding: utf-8 -*-
"""
adcusers_in.sample py is a sample file of adcusers_in.py 
  cp adcusers_in.sample.py adcusers_in.py 

adcusers_in.py 
input file of user definition
Run "python adcusers_gen.py" to generate adcusers.py
"""

ADMIN_USERNAME='administrator'
ADMIN_PASSWORD='***CHANGE HERE PLEASE!!***'

USERS = [
    # 0:username     1:password       2:displayname        3:uid 4:gid
    [ADMIN_USERNAME, ADMIN_PASSWORD,  u'ADC Manager',      0,    0 ],
    #[ 'usagi',      '***CHANGE***',  u'ウサギさんチーム', 1001, 1000 ],
    #[ 'kame',       '***CHANGE***',  u'カメさんチーム',   1002, 1000 ],
    #[ 'saru',       '***CHANGE***',  u'おさるさんチーム', 1003, 1000 ],
]
