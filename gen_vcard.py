import csv
import os
import sys

def details_from_csv(file_csv):
  data = []
  with open(file_csv,'r') as f:
    reader = csv.reader(f)
    for item in reader:
      data.append(item)
  return data

def generate_vcs(data):
  for item in data:
    with open(f'vcards/{item[0]}_{item[1]}.vcf','w') as f:
        f.write(f"""
BEGIN:VCARD
VERSION:2.1
N:{item[0]};{item[1]}
FN:{item[1]} {item[0]}
ORG:Authors, Inc.
TITLE:{item[2]}
TEL;WORK;VOICE:{item[4]}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{item[3]}
REV:20150922T195243Z
END:VCARD
""")
        
def main():
    if not os.path.exists('/vcard'):
       os.mkdir('vcards')
       file = sys.argv[1]
       data = details_from_csv(file)
       generate_vcs(data)
       

if __name__ == "__main__":
  main()    