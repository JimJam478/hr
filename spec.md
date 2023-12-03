# HR project
## By: Allen K
## 14.11.2023

### Objective:
	
Generates employee details, Vcards, QR codes and leave details. 

### input

csv file containing employee details.\
eg: details.csvs
	
### Usage:

The csv file must contain employee details in the following format:\
	last name, first name, designation, email, phone number.\
Eg: 'Alice','Bob','Software Engineer','alice@example.com','555-555-5555'

The next employee's detail must be written in the next row/line in the csv file.
	
#### Generating employee details, Vcards, QRcodes:

1) Initialize database

		script: python3 hr.py initdb
	This script creates a database and an employees table, employee leaves table and a designation table.

2) Load data

		script: python3 hr.py load <csv_file>

3) Generate details

		script: python3 hr.py info <employee id>

4) Generate Vcards

		script: python3 hr.py info <employee id> --vcard

	This will display a vcard along with the employee details.\
	The vcard will also be saved in a folder called vcards.

5) Generate QR codes:

		script: python3 hr.py info <employee id> --qrcode

	QR code will be saved into the vcards folder.\
	Size of QR can be adjusted by adding -s [size of qr].
	(Max size: 530)

 Sample details for an employee will be of the following format:

		Name        : Craig Tyler
		Designation : Junior Engineer
		Email       : craig.tyler@sanchez.com
		Phone       : (412)411-3060

#### Generating employee leave details:

1) Initializing table:

	Table will be generated while initializing the database.

2) Loading employee leave table:

		script: python3 hr.py leave [date] [reason] [employee id]	

3) Generating details:

		script: python3 gen_vcard linfo <employee id>

Leave details for employees can be exported into a csv file by using the following script:

		script: python3 gen_vcard linfo <employee id> --exp <csv file>

Sample employee leave details will be of the following format:

		Employee Name: Natasha Brown
		Employee Designation: Staff Engineer
		email: natas.brown@contreras.com
		Max leaves:  20
		Leaves left: 17

### Output:

A directory called 'vcards' will be created.\
This directory will contain all the Vcards and QR codes.
Note: If the directory 'vcards' already exists, an error will show up.

A csv file of users choice containing employee leave details. 
	
	

	   
