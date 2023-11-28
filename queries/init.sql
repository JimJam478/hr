CREATE TABLE if not exists employees( 
id SERIAL PRIMARY KEY, 
last_name VARCHAR(80),
first_name VARCHAR(80), 
designation VARCHAR(80), 
email VARCHAR(80),
phone_number VARCHAR(80) 
);

create table if not exists employee_leaves (
id serial primary key,
leave_date date not null,
reason varchar(80),
employee_id integer references employees(id), 
unique (employee_id,leave_date)
);

create table if not exists employee_designation (
id serial,
designation varchar(50) primary key,
max_leaves integer
);

insert into employee_designation(designation,max_leaves) 
values ('Staff Engineer',20),
('Senior Engineer',18),
('Junior Engineer',12),
('Tech Lead',12),
('Project Manager',15);