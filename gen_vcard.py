import argparse
import csv
import logging
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extensions import AsIs
import psycopg2.sql as sql
import requests

def parse_args():
  parser = argparse.ArgumentParser(prog="gen_vcard.py", description="Generates employee Vcard and QR codes from a csv file")
  
  subparser = parser.add_subparsers(dest='subcommand',help='sub command help')
  parser_db = subparser.add_parser("db",help="database commands")
  parser_db.add_argument("-i","--initdb",help="Initialize database",action='store_true')
  parser_db.add_argument("--createtb", help="Create a table in database", action='store_true')
  parser_db.add_argument("--deltb", help="Delete specific table in database", action='store', type=str)
  parser_db.add_argument("-d","--deldb",help="delete database",action='store', type=str)

  parser_load = subparser.add_parser("load",help="load file commands")
  parser_load.add_argument("-f","--file",help="csv file name",action="store",type=str)
  parser_load.add_argument("-n", "--number", help="Number of vcards/qr code to generate", action='store', type=int)
  parser_load.add_argument("-l","--loadleave",help="load data into leave table",action="store_true",default=False)

  parser_generate = subparser.add_parser("generate",help="generate commands")
  parser_generate.add_argument("-q","--qrcode",help="Generate qr codes",action="store_true",default=False)
  parser_generate.add_argument("-s", "--size", help="Size of qr codes", action='store', type=int, default=500)
  parser_generate.add_argument("-e", "--empleave", help="Leaves taken by the perticular employee", action='store', type=int)
  parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
  parser.add_argument("-c", "--concise", help="Print concise logging", action='store_true', default=False)
  args = parser.parse_args()
  return args

logger = None

def setup_logging(log_level):
  global logger
  logger = logging.getLogger("gen_vcard")
  handler = logging.StreamHandler()
  fhandler = logging.FileHandler("run.log")
  fhandler.setLevel(logging.DEBUG)
  handler.setLevel(log_level)
  handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
  fhandler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
  logger.setLevel(logging.DEBUG)
  logger.addHandler(handler)
  logger.addHandler(fhandler)

def get_data(file_csv,number):
  data = []
  row_count = 0
  with open(file_csv,'r') as f:
    reader = csv.reader(f)
    for item in reader:
      if row_count >= number:
        break
      row_count += 1
      data.append(item)
  return data

def get_data_full(file_csv):
  data = []
  with open(file_csv,'r') as f:
    reader = csv.reader(f)
    for item in reader:
      data.append(item)
  return data

def create_database():
  conn = psycopg2.connect(database="postgres", user='allen')
  cursor = conn.cursor()
  cursor.execute("commit")
  cursor.execute("create database company")
  logger.info('Database company created succesfully')
  cursor.close()
  conn.close()

def delete_database(name):
  conn = psycopg2.connect(database="postgres", user='allen')
  cursor = conn.cursor()
  cursor.execute("commit")
  cursor.execute("drop database %s",(AsIs(name),))
  logger.info("database %s deleted succesfully",name)
  cursor.close()
  conn.close()

def create_table():
  conn = psycopg2.connect(dbname="company", user="allen")
  cursor = conn.cursor()
  cursor.execute(''' CREATE TABLE employees( 
id SERIAL PRIMARY KEY, 
last_name VARCHAR(80),
first_name VARCHAR(80), 
designation VARCHAR(80), 
email VARCHAR(80),
phone_number VARCHAR(80) 
);''')   
  logger.info("Employee table created successfully!!")
  conn.commit()
  conn.close()

def create_additonal_table(query):
  conn = psycopg2.connect(dbname="company", user="allen")
  cursor = conn.cursor()
  cursor.execute(query)
  logger.info("Employee_leave table created succesfully!")
  conn.commit()
  conn.close()

def delete_table(table):
  conn = psycopg2.connect(dbname="company", user="allen")
  cursor = conn.cursor()
  cursor.execute("Drop table %s",AsIs(table,))
  logger.info("%s deleted successfully!!",table)
  conn.commit()
  conn.close()

def truncate_table():
  conn = psycopg2.connect(dbname="company",user="allen")
  cursor = conn.cursor()
  truncate_table = "TRUNCATE TABLE employees RESTART IDENTITY"
  cursor.execute(truncate_table)
  conn.commit()
  conn.close()

def update_table(data):
  truncate_table()
  conn = psycopg2.connect(dbname="company", user="allen")
  cursor = conn.cursor()
  for item in data:
    cursor.execute("INSERT INTO employees (last_name, first_name, designation, email, phone_number) VALUES (%s,%s,%s,%s,%s)",(item[0], item[1], item[2], item[3], item[4]))
    conn.commit()
  logger.info('Table employees updated succesfully')
  cursor.close()
  conn.close()

def load_leave_table():
  conn = psycopg2.connect(dbname="company", user="allen")
  cursor = conn.cursor()
  query = open('leaves.sql','r')
  cursor.execute(query.read())
  logger.info('Leave table loaded succesfully')
  conn.commit()
  cursor.close()
  conn.close()

def join_leave_table(id):
  query = f'''select count(el.employee_id),e.first_name,e.last_name ,e.id 
  from employees e join employee_leave el on e.id = el.employee_id 
  where e.id={id} group by e.id,e.first_name,el.employee_id;'''
  conn = psycopg2.connect(dbname="company", user="allen")
  cursor = conn.cursor()
  cursor.execute(query)
  data = cursor.fetchall()
  cursor.close()
  conn.close()
  return data

def get_leave_data(data):
  for item in data:
    count, f_name, l_name, e_id = item
  leaves_left = 5 - count
  return f'''Employee Name: {f_name} {l_name}
Employee Id: {e_id}
Max leaves: 5
Leaves left: {leaves_left}
'''

def get_table_data(start, end):
    offset = start-1
    limit = end - start + 1
    conn = psycopg2.connect(dbname='company', user='allen')
    cur = conn.cursor()
    cur.execute(
        "SELECT last_name, first_name, designation, email, phone_number FROM employees LIMIT %s OFFSET %s;",(limit, offset)
    )
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def generate_vcard_content(l_name,f_name,designation,email,phone):
  return f"""
  BEGIN:VCARD
  VERSION:2.1
  N:{l_name};{f_name}
  FN:{f_name} {l_name}
  ORG:Authors, Inc.
  TITLE:{designation}
  TEL;WORK;VOICE:{phone}
  ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
  EMAIL;PREF;INTERNET:{email}
  REV:20150922T195243Z
  END:VCARD
  """
def generate_vcs(data):
  i = 0
  for item in data:
    l_name,f_name,designation,email,phone = item
    with open(os.path.join('vcards',f'{l_name.lower()}_{f_name.lower()}.vcf'),'w') as f:
      f.write(generate_vcard_content(l_name,f_name,designation,email,phone))
    i+=1
    logger.debug("%d. Generated %s_%s.vcf",i,l_name,f_name)
  logger.info("Vcard Generation success !")
  
def generate_qr_code_content(l_name,f_name,designation,email,phone,size):
  qr_code = requests.get(f"https://chart.googleapis.com/chart?cht=qr&chs={size}x{size}&chl={l_name,f_name,designation,email,phone}")
  return qr_code.content
  
def generate_qr_codes(data,size):
  i = 0
  for item in data:
    l_name,f_name,designation,email,phone = item
    with open(f"vcards/{l_name.lower()}_{f_name.lower()}.qr.png", "wb") as f:
      f.write(generate_qr_code_content(l_name,f_name,designation,email,phone,size))
      i+=1
    logger.debug("%d. Generated %s_%s.qr.png",i,l_name,f_name)
  logger.info("QR Generation success !")

def main():
  args = parse_args()
  if args.verbose:
    setup_logging(logging.DEBUG)
  elif args.concise:
    setup_logging(logging.INFO)
  else:
    setup_logging(logging.CRITICAL)
  if not os.path.exists('vcards'):
    os.mkdir('vcards')
  
  if args.subcommand == 'db':
    name = args.initdb
    if name == True:
      create_database()
      create_table()

    create_tb = args.createtb
    del_tb = args.deltb

    if create_tb == True:
      query = '''create table if not exists employee_leave (
id serial,
leave_date date,
reason varchar(80),
employee_id integer references employees(id), 
PRIMARY KEY (employee_id,leave_date)
)'''
      create_additonal_table(query)
  
    if del_tb != None:
      delete_table(del_tb)
    
    del_db = args.deldb
    if del_db != None:
      delete_database(del_db)
  
  if args.subcommand == 'load':
    number = args.number
    if args.file:
      if number == None:
        data = get_data_full(args.file)
      else:
        data = get_data(args.file,number)
      update_table(data)

    if args.loadleave:
      load_leave_table()
    
  if args.subcommand == 'generate':
    data_from_db = list(get_table_data(1, 999999))
    qrcode = args.qrcode
    size = args.size

    if qrcode==True:
      generate_qr_codes(data_from_db,size)
      generate_vcs(data_from_db)
    else: 
      generate_vcs(data_from_db)
    
    e_id = args.empleave
    if e_id != None:
      data = join_leave_table(e_id)
      print(get_leave_data(data))

if __name__ == "__main__":
  main()    



