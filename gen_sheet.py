import csv

import sys

import faker 

def generate_details():
    f = faker.Faker()
    names = []
    for i in range(100):
        record = []
        lname = f.last_name()
        fname = f.first_name()
        domain = f.domain_name()
        designation = f.job()
        email = f"{fname[:5].lower()}.{lname[:5].lower()}@{domain}"
        phone = f.phone_number()
        record = [lname, fname, designation, email, phone]
        names.append(record)
    return names
    
def writer(file,data):
    with open(file, 'w',newline="") as outcsv:   
        writer = csv.writer(outcsv)
        for item in data:
            writer.writerow(item)
    return file
        
def main():
    details = generate_details()
    file = sys.argv[1]
    writer(file,details)

if __name__ == "__main__":
    main()