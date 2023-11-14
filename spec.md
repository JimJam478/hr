# Vcard generator
## By: Allen K
## 14.11.2023

### Objective:
	
Generates Vcards and QR codes for a list of employees in a csv file.

### Usage:
	
	Script: python3 gen_vcards.py <csv_file>

Once the script is entered, each row in the csv file which represents a single employee's detail, is taken and a Vcard, QR code is generated for each employee.

A new directory called 'vcards' will be created.
This directory will contain all the Vcards and QR codes.
Note: If the directory 'vcards' already exists, an error will show up.

Each Vcard file will be of the format: lastname_firstname.vcf
Each Qr file will be of the format: lastname_firstname.qr.png

### Output:
	
If the csv file contains the following employee details:
	'Alice','Bob','Software Engineer','alice@example.com','555-555-5555'
	
Files named 'alice_bob.vcf' and 'alice_bob.qr.png' will be generated.
The file 'alice_bob.vcf' will contain the following:

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
	

	   
