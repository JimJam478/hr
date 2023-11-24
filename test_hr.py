import hr
import os

def test_generate_vcs():
    data = ['Alice','Bob','Software Engineer','alice@example.com','555-555-5555']
    l_name,f_name,designation,email,phone = data
    hr.generate_vcard_content(l_name,f_name,designation,email,phone)
    assert f"""
BEGIN:VCARD
VERSION:2.1
N:Alice;Bob
FN:Bob Alice
ORG:Authors, Inc.
TITLE:Software Engineer
TEL;WORK;VOICE:555-555-5555
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:alice@example.com
REV:20150922T195243Z
END:VCARD
""" 
    


    
