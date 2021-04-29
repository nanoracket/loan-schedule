# EarnUp loan schedule

## Description

Basic application that reads the loans from the earnup rest API produces payment and debit schedules for 3 months
The main.py file takes in the user input, performs the requested task, and prints out the relevant results
The loan.py file contains all classes relevant to producing the schedule for a loan.
The database.py file contains the database class which is the only class to directly interact with the database

## How to use

First run the main file with -i to populate the database with the payments and debits for the inputted loans
```
python3 main.py -i
```

To query for a loan's debits supply the loanId with the -d parameter
```
python3 main.py -d 7B70C36F-8CE7-9F6B-1B25-91AFE40E73F3
```

To query for a loan's payments supply the loanId with the -p parameter
```
python3 main.py -p 7B70C36F-8CE7-9F6B-1B25-91AFE40E73F3
```

To query for a payment's debits supply the paymentId with the -P parameter
```
python3 main.py -P 4eba7204-52c1-4c11-aac1-0f714c3c3a10
```
