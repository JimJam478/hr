import argparse
import csv
import os
import requests
import sys
import logging

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

def parse_args():
  parser = argparse.ArgumentParser(prog="gen_vcard.py", description="Generates employee Vcard and QR codes from a csv file")
  parser.add_argument("ipfile", help="Name of input csv file containing employee details")
  parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
  parser.add_argument("-i", "--concise", help="Print concise logging", action='store_true', default=False)
  parser.add_argument("-n", "--number", help="Number of vcards/qr code to generate", action='store', type=int,default = 10)
  parser.add_argument("-vc", "--vcard", help="Generates only Vcards", action='store_true', default=False)
  parser.add_argument("-qr", "--qrcode", help="Generates only QR codes", action='store_true', default=False)
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

def generate_vcard_content(data):
  l_name,f_name,designation,email,phone = data
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
    with open(f'vcards/{item[0].lower()}_{item[1].lower()}.vcf','w') as f:
      f.write(generate_vcard_content(item))
    i+=1
    logger.debug("%d. Generated %s_%s.vcf",i,item[0],item[1])
  logger.info("Vcard Generation success !")
  
def generate_qr_codes(data):
  i = 0
  for item in data:
    qr_code = requests.get(f"https://chart.googleapis.com/chart?cht=qr&chs=500x500&chl={item}")
    with open(f"vcards/{item[0].lower()}_{item[1].lower()}.qr.png", "wb") as f:
      f.write(qr_code.content)
      i+=1
    logger.debug("%d. Generated %s_%s.qr.png",i,item[0],item[1])
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
  file = args.ipfile
  number = args.number
  if not number:
    data = get_data_full(file)
  else:
    data = get_data(file,number)
  vcard = args.vcard
  qrcode = args.qrcode
  if vcard:
    generate_vcs(data)
  if qrcode:
    generate_qr_codes(data)
  if not vcard and not qrcode: 
    generate_vcs(data)
    generate_qr_codes(data)

if __name__ == "__main__":
  main()    