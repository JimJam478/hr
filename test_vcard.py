import gen_vcard
import os


def test_get_data():
    test = "/tmp/sample"
    number = 1
    with open(test, 'w') as f:
        f.write('Alice,Bob,Software Engineer,alice@example.com,555-555-5555')
    data = gen_vcard.get_data(test,number)
    assert data == [['Alice','Bob','Software Engineer','alice@example.com','555-555-5555']]
    os.unlink(test)

def test_generate_vcs():
    data = ['Alice','Bob','Software Engineer','alice@example.com','555-555-5555']
    gen_vcard.generate_vcard_content(data)
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
    


    
