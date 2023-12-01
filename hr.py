import argparse
import configparser
import csv 
import logging
import os
import sys

import psycopg2
import sqlalchemy as sa
import sqlalchemy.exc 
import requests

import db 

class HRException(Exception): pass

logger = False

def setup_logging(is_verbose):
    global logger
    if is_verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger = logging.getLogger("hr.py")
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
  
def parse_args():
    
    config = configparser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser(description="HR tool")
    parser.add_argument("--dbname", help="Name of database to use", default=config.get('Database','dbname'))
    parser.add_argument("-v", help="Enable verbose debug logging", action="store_true", default=False)

    subparsers = parser.add_subparsers(dest="subcommand",help='sub command help')
    subparsers.add_parser("initdb", help="initialise the database")

    load_parser = subparsers.add_parser("load", help="load data from csv file")
    load_parser.add_argument("employees_file", help="List of employees to import")
    load_parser.add_argument("-v", help="Enable verbose debug logging", action="store_true", default=False)
    
    info_parser = subparsers.add_parser("info", help="Get information for a single employee")
    info_parser.add_argument("id", help="employee id")
    info_parser.add_argument("--vcard", action="store_true", default=False, help="Generate vcard for employee")
    info_parser.add_argument("--qrcode", action="store_true", default=False, help="Generate qrcode for employee")
    info_parser.add_argument("-s", "--size", help="Size of qr codes", action='store', type=int, default=500)
   
    leave_parser = subparsers.add_parser("leave", help="Add leave for an employee")
    leave_parser.add_argument("id",help="Id of employee on leave",type=int)
    leave_parser.add_argument("date",help="Date of leave [YYYY-MM-DD]",type=str)
    leave_parser.add_argument("reason",help="Reason for leave",type=str)
    
    leave_info_parser = subparsers.add_parser("leave_info", help="Get leave information for a single employee")
    leave_info_parser.add_argument("empid",help='Id of employee',type=int)
    leave_info_parser.add_argument("--exp",help="export into csv file [filename.csv]")

    args = parser.parse_args()
    return args

def config_parse(dbname):
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.set('Database','dbname',dbname)
    with open('config.ini','w') as f:
        config.write(f)

def create_table_in_db(args):
    config_parse(args.dbname)
    try:
        db_uri = f"postgresql:///{args.dbname}"
        db.create_all(db_uri)
        logger.info("Tables created successfully!!")
        session = db.get_session(db_uri)
        d1 = db.Designation(title="Staff Engineer", max_leaves=20)
        d2 = db.Designation(title="Senior Engineer", max_leaves=18)
        d3 = db.Designation(title="Junior Engineer", max_leaves=12)
        d4 = db.Designation(title="Tech Lead", max_leaves=12)
        d5 = db.Designation(title="Project Manager", max_leaves=15)
        session.add(d1)
        session.add(d2)
        session.add(d3)
        session.add(d4)
        session.add(d5)
        session.commit()
        
    except sqlalchemy.exc.OperationalError as e:
        raise HRException(f"Database '{args.dbname}' doesn't exist")

# def truncate_table():
#     args = parse_args()
#     conn = psycopg2.connect(dbname=args.dbname)
#     cursor = conn.cursor()
#     truncate_table = "TRUNCATE TABLE employees RESTART IDENTITY CASCADE"
#     cursor.execute(truncate_table)
#     conn.commit()
#     conn.close()

def load_data_employees(args):
    db_uri = f"postgresql:///{args.dbname}"
    session = db.get_session(db_uri)
    with open(args.employees_file) as f:
        reader = csv.reader(f)
        for lname, fname, title, email, phone in reader:
            q = sa.select(db.Designation).where(db.Designation.title == title)
            designation = session.execute(q).scalar_one_or_none()
            logger.debug("Inserting %s", email)
            employee = db.Employee(
                last_name=lname,
                first_name=fname,
                email=email,
                phone=phone,
                title=designation,
            )
            session.add(employee)
        session.commit()
   
def load_data_leaves(args):
    with open("queries/leaves.sql") as f:
        query = f.read()
        logger.debug(query)
    conn = psycopg2.connect(dbname=args.dbname)
    cursor = conn.cursor()
    cursor.execute(query,(args.date,args.reason,args.id))
    conn.commit()
    logger.info("Employee id:%s added succesfully!",args.id)
    cursor.close()
    conn.close()

def generate_vcard_content(lname,fname,designation,email,phone):
  return f"""
BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
  """

def generate_qr_code_content(lname, fname, designation, email, phone,size):
  qr_code = requests.get(f"https://chart.googleapis.com/chart?cht=qr&chs={size}x{size}&chl={lname, fname, designation, email, phone}")
  return qr_code.content

def get_info_employee(args):
    conn = psycopg2.connect(dbname=args.dbname)
    cursor = conn.cursor()
    try:
        query = "SELECT first_name, last_name, designation, email, phone_number from employees where id = %s"
        cursor.execute(query, (args.id,))
        employee_info = cursor.fetchone()
        fname, lname, designation, email, phone = employee_info
        
        print (f"""
Name        : {fname} {lname}
Designation : {designation}
Email       : {email}
Phone       : {phone}
""")
        
        if (args.vcard):
            with open(os.path.join('vcards',f'{lname.lower()}_{fname.lower()}.vcf'),'w') as f:
                vcard = generate_vcard_content(lname, fname, designation, email, phone)
                f.write(vcard)
            print (f"\n{vcard}")
            logger.info("Generated %s_%s.vcf",lname,fname)

        if (args.qrcode):
            with open(os.path.join('vcards',f'{lname.lower()}_{fname.lower()}.png'),'wb') as f:
                qr = generate_qr_code_content(lname, fname, designation, email, phone,args.size)
                f.write(qr)
                logger.info("Generated %s_%s.png",lname,fname)

        cursor.close()
        conn.close()

    except TypeError:
        raise HRException (f'Employee id. {args.id} does not exist')
    

def join_leave_table(args,id):
    query = '''select count (e.id) as count, e.first_name, e.last_name , e.email , e.designation, d.max_leaves from employees e
join employee_leaves l on e.id = l.employee_id join employee_designation d on e.designation = d.designation
where e.id=%s group by e.id,e.first_name,e.email,d.max_leaves;'''
    conn = psycopg2.connect(dbname=args.dbname)
    cursor = conn.cursor()
    cursor.execute(query,[id])
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_leave_none_taken(args,id):
    sql = '''select e.first_name, e.last_name, e.email, e.designation, d.max_leaves from employees e
join employee_designation d on e.designation = d.designation
where e.id= %s group by e.id,e.first_name,e.email,d.max_leaves;'''
    conn = psycopg2.connect(dbname=args.dbname)
    cursor = conn.cursor()
    cursor.execute(sql,[id])
    info = cursor.fetchall()
    cursor.close()
    conn.close()
    return info

def get_employee_leave_data(args):
    id = args.empid
    employee_leave_data = join_leave_table(args,id)
    
    for item in employee_leave_data:
        if item in employee_leave_data:
            count, f_name, l_name, email, designation, max_leaves = item
            leaves_left = max_leaves - count
            
            if leaves_left <= 0:
                print(f'''
No leaves left for:
Employee Name:          {f_name} {l_name}
Employee Designation:   {designation}
Leaves taken:           {count}/{max_leaves}
''')
                exit()
            
            print(f'''
Employee Name: {f_name} {l_name}
Employee Designation: {designation}
email: {email}
Max leaves:  {max_leaves}
Leaves left: {leaves_left}
''')        
            if args.exp != None:
                writer_csv(args.exp,f_name, l_name, email, designation, max_leaves,leaves_left)

    if employee_leave_data == []:
        ideal_employee_leave_data = get_leave_none_taken(args,id)
        
        for item in ideal_employee_leave_data:
            f_name, l_name, email, designation, max_leaves = item
            leaves_left = max_leaves
            print(f'''
Employee Name: {f_name} {l_name}
Employee Designation: {designation}
email: {email}
Max leaves:  {max_leaves}
Leaves left: {leaves_left}
''')
            if args.exp != None:
                writer_csv(args.exp,f_name, l_name, email, designation, max_leaves,leaves_left)
        
        if ideal_employee_leave_data == []:
            logger.error(f'Employee with id. {id} doesn\'t exist.')
    
def writer_csv(file,f_name, l_name, email, designation, max_leaves,leaves_left):
    with open(file, 'a',newline="") as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow((f_name, l_name, email, designation, max_leaves,leaves_left))
        logger.info(f'Exported into csv file: {file}')
    return file  
    
def main():
    if not os.path.exists('vcards'):
        os.mkdir('vcards')
    try:
        args = parse_args()
        setup_logging(args.v)
        operations = {"initdb":create_table_in_db,
                      "load":load_data_employees,
                      "info":get_info_employee,
                      "leave":load_data_leaves,
                      "leave_info":get_employee_leave_data}
        operations[args.subcommand](args)
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)

if __name__ == "__main__":
    main()