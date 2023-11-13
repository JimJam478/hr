import csv
import os
import sys

def generate_vcard(file_csv):
    data = []
    with open(file_csv,'r') as f:
        reader = csv.reader(f)
        for item in reader:
            data.append(item)
    for item in data:
            path = r'/home/allen/main_project/vcard'
            filename = f'{item[0].lower()}_{item[1].lower()}.txt'
            f = open(os.path.join(path, filename),'w')
            f.write(f"""BEGIN:VCARD
VERSION:2.1
FN:{item[0]} {item[1]}
ORG:Authors, Inc.
TITLE:{item[2]}
TEL;WORK;VOICE:{item[4]}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{item[3]}
REV:20150922T195243Z
END:VCARD
""")
    return f

def main():
    file_name = sys.argv[1]
    generate_vcard(file_name)
    
if __name__ == "__main__":
    main()