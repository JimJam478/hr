import argparse
import csv 
import logging
import os
import sys

import psycopg2
import requests

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
    parser = argparse.ArgumentParser(description="HR tool")
    parser.add_argument("--dbname", help="Name of database to use", default="hr")
    parser.add_argument("-v", help="Enable verbose debug logging", action="store_true", default=False)
    subparsers = parser.add_subparsers(dest="subcommand",help='sub command help')
    subparsers.add_parser("initdb", help="initialise the database")

    load_parser = subparsers.add_parser("load", help="load data from csv file")
    load_parser.add_argument("employees_file", help="List of employees to import")
    
    info_parser = subparsers.add_parser("info", help="Get information for a single employee")
    info_parser.add_argument("id", help="employee id")
    info_parser.add_argument("--vcard", action="store_true", default=False, help="Generate vcard for employee")
    info_parser.add_argument("--qrcode", action="store_true", default=False, help="Generate qrcode for employee")
    info_parser.add_argument("-s", "--size", help="Size of qr codes", action='store', type=int, default=500)
   
    leave_parser = subparsers.add_parser("leave", help="Leave commands of employee")
    leave_parser.add_argument("date",help="Date of leave",type=str)
    leave_parser.add_argument("reason",help="Reason for leave",type=str)
    leave_parser.add_argument("id",help="Id of employee on leave",type=int)

    leave_info_parser = subparsers.add_parser("linfo", help="Get leave information for a single employee")
    leave_info_parser.add_argument("empid",help='Id of employee',type=int)
    leave_info_parser.add_argument("--exp",help="export into csv file")

    
    args = parser.parse_args()
    return args

def get_table_in_db(args):
    with open("queries/init.sql") as f:
        query = f.read()
        logger.debug(query)
    try:
        conn = psycopg2.connect(dbname=args.dbname)
        cursor = conn.cursor()
        cursor.execute(query)   
        logger.info("Tables created successfully!!")
        conn.commit()
        conn.close()

    except psycopg2.OperationalError as e:
        raise HRException(f"Database '{args.dbname}' doesn't exist")

def truncate_table():
    args = parse_args()
    conn = psycopg2.connect(dbname=args.dbname)
    cursor = conn.cursor()
    truncate_table = "TRUNCATE TABLE employees RESTART IDENTITY CASCADE"
    cursor.execute(truncate_table)
    conn.commit()
    conn.close()

def load_data_employees(args):
    truncate_table()
    conn = psycopg2.connect(dbname=args.dbname)
    cursor = conn.cursor()
    with open(args.employees_file) as f:
        reader = csv.reader(f)
        for lname, fname, designation, email, phone in reader:
            logger.debug("Inserting %s", email)
            query = "insert into employees(last_name, first_name, designation, email, phone_number) values (%s, %s, %s, %s, %s)"
            cursor.execute(query, (lname, fname, designation, email, phone))
        conn.commit()
        logger.info("Employees updated successfully!!")
    cursor.close()
    conn.close()

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
  return f"""BEGIN:VCARD
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
    query = "SELECT first_name, last_name, designation, email, phone_number from employees where id = %s"
    cursor.execute(query, (args.id,))
    fname, lname, designation, email, phone = cursor.fetchone()

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
        with open(os.path.join('vcards',f'{lname.lower()}_{fname.lower()}.qr.png'),'wb') as f:
            qr = generate_qr_code_content(lname, fname, designation, email, phone,args.size)
            f.write(qr)
            logger.info("Generated %s_%s.png",lname,fname)

    cursor.close()
    conn.close()

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
            print('Employee with id',id,'doesn\'t exist')
    
def writer_csv(file,f_name, l_name, email, designation, max_leaves,leaves_left):
    with open(file, 'a',newline="") as outcsv:   
        writer = csv.writer(outcsv)
        writer.writerow((f_name, l_name, email, designation, max_leaves,leaves_left))
    return file  
    
def main():
    if not os.path.exists('vcards'):
        os.mkdir('vcards')
    try:
        args = parse_args()
        setup_logging(args.v)
        operations = {"initdb":get_table_in_db,
                      "load":load_data_employees,
                      "info":get_info_employee,
                      "leave":load_data_leaves,
                      "linfo":get_employee_leave_data}
        operations[args.subcommand](args)
    except HRException as e:
        logger.error("Program aborted, %s", e)
        sys.exit(-1)

if __name__ == "__main__":
    main()