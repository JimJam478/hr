import gen_vcard
import os

def test_generate_vcard():
        with open('test.csv', 'w') as f:
            f.write('Alice,Bob,Software Engineer,alice@example.com,555-555-5555')
        gen_vcard.generate_vcard('test.csv')
        with open('vcard/alice_bob.txt', 'r') as f:
            vcard = f.read()

        assert os.path.exists('vcard/alice_bob.txt')
        assert f"""BEGIN:VCARD
VERSION:2.1
FN:Alice Bob
ORG:Authors, Inc.
TITLE:Software Engineer
TEL;WORK;VOICE:555-555-5555
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:alice@example.com
REV:20150922T195243Z
END:VCARD""" in vcard