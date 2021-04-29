import argparse
import requests
from database import Database
from loan import Loan, Payment, Debit
from pprint import pprint

def get_input():
    samples = []
    url = "https://my-json-server.typicode.com/EarnUp/demo/loans"
    resp = requests.get(url)
    if resp == None:
        return []
    try:
        samples = resp.json()
    except:
        return []
    return samples

def parse_args():
    parser = argparse.ArgumentParser(description="Generate loan schedule")
    parser.add_argument('-i', '--initialize', help='populate database', action='store_true')
    parser.add_argument('-d', '--debits', type=str, help='query debits associated with loan', action='store')
    parser.add_argument('-p', '--payments', type=str, help='query payments associated with loan', action='store')
    parser.add_argument('-P', '--payment-debits', type=str, help='query debits associated with payment', action='store')
    args = parser.parse_args()
    return vars(args)

def main(args):
    db = Database()
    if args['initialize']:
        samples = get_input()
        for sample in samples:
            loan = Loan(sample)
            loan.generatePaymentSchedule(months=3)
        print("Finished populating db!")
    elif args['debits']:
        debits = db.queryLoanDebits(args['debits'])
        if len(debits) == 0:
            print(f"No debits found for loan {args['debits']}")
        else:
            for debit in debits:
                debObj = Debit(*list(debit))
                pprint(vars(debObj))
    elif args['payments']:
        payments = db.queryLoanPayments(args['payments'])
        if len(payments) == 0:
            print(f"No payments found for loan {args['payments']}")
        else:
            for payment in payments:
                payObj = Payment(*list(payment))
                pprint(vars(payObj))
    elif args['payment_debits']:
        debits = db.queryPaymentDebits(args['payment_debits'])
        if len(debits) == 0:
            print(f"No debits found for payment {args['payment_debits']}")
        else:
            for debit in debits:
                debObj = Debit(*list(debit))
                pprint(vars(debObj))
    else:
        print("No action specified!")

if __name__ == "__main__":
    args = parse_args()
    main(args)
