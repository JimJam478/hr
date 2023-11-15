import gen_vcard
import os

def test_get_data():
    test = "/tmp/sample"
    with open(test, 'w') as f:
        f.write('Alice,Bob,Software Engineer,alice@example.com,555-555-5555')
    data = gen_vcard.get_data(test)
    assert data == [['Alice','Bob','Software Engineer','alice@example.com','555-555-5555']]
    os.unlink(test)

def test_generate_vcs():
    if not os.path.exists('vcards'):
        os.mkdir('vcards')
    data = [['Alice','Bob','Software Engineer','alice@example.com','555-555-5555']]
    gen_vcard.generate_vcs(data)
    with open('vcards/alice_bob.vcf', 'r') as f:
        vcard = f.read()
    assert os.path.exists('vcards/alice_bob.vcf')
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
""" in vcard
    os.unlink('vcards/alice_bob.vcf')

def test_generate_qr():
    if not os.path.exists('vcards'):
        os.mkdir('vcards')
    data = [['Alice','Bob','Software Engineer','alice@example.com','555-555-5555']]
    gen_vcard.generate_qr_codes(data)
    assert os.path.exists('vcards/alice_bob.qr.png')
    
    
