import sqlite3
import atexit

class Database():
    def __init__(self):
        self.con = sqlite3.connect('earnup.db')
        self.cur = self.con.cursor()
        self._createTables()
        atexit.register(self._cleanup)

    def _cleanup(self):
        self.con.close()

    def _createTables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS loans
               (id varchar PRIMARY KEY, 
                monthlyPaymentAmount int,
                paymentDueDay int,
                scheduleType text,
                debitStartDate text,
                daysOfMonth text,
                hasGracePeriod int)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS payments
                (id varchar PRIMARY KEY, 
                 loanId varchar,
                 paymentAmount int,
                 paymentDate real,
                 FOREIGN KEY(loanId) REFERENCES loans(id))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS debits
                (id varchar PRIMARY KEY, 
                 loanId varchar,
                 paymentId varchar,
                 debitAmount int,
                 debitDate real,
                 FOREIGN KEY(paymentId) REFERENCES payments(id),
                 FOREIGN KEY(loanId) REFERENCES loans(id))''')
        self.con.commit()

    def savePaymentAndDebits(self, debits, payment):
        if self.queryPayments(payment.paymentDate):
            return
        self.cur.execute("INSERT INTO payments VALUES (?, ?, ?, ?)",
                         (payment.id, payment.loanId,
                         payment.paymentAmount, payment.paymentDate))
        debitParams = []
        for debit in debits:
            params = (debit.id, debit.loanId, payment.id,
                      debit.debitAmount, debit.debitDate)
            debitParams.append(params)
        self.cur.executemany("INSERT INTO debits VALUES (?, ?, ?, ?, ?)", debitParams)
        self.con.commit()

    def saveLoan(self, loan):
        if self.queryLoans(loan.id):
            return
        days = [str(day) for day in loan.daysOfMonth]
        self.cur.execute("INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (loan.id, loan.monthlyPaymentAmount, loan.paymentDueDay,
                            loan.scheduleType, loan.debitStartDate, ".".join(days),
                            1 if loan.hasGracePeriod else 0))
        self.con.commit()

    def queryLoans(self, loanId):
        self.cur.execute("SELECT id FROM loans WHERE id = ?", (loanId,))
        return self.cur.fetchone()

    def queryPayments(self, paymentDate):
        self.cur.execute("SELECT id FROM payments WHERE paymentDate = ?", (paymentDate,))
        return self.cur.fetchone()

    def queryLoanDebits(self, loanId):
        self.cur.execute("SELECT loanId, debitDate, debitAmount, id FROM debits WHERE loanId = ?", (loanId,))
        return self.cur.fetchall()

    def queryLoanPayments(self, loanId):
        self.cur.execute("SELECT loanId, paymentDate, paymentAmount, id FROM payments WHERE loanId = ?", (loanId,))
        return self.cur.fetchall()

    def queryPaymentDebits(self, paymentId):
        self.cur.execute("SELECT loanId, debitDate, debitAmount, id FROM debits WHERE paymentId = ?", (paymentId,))
        return self.cur.fetchall()

    def clearTables(self):
        self.cur.execute("DROP TABLE loans")
        self.cur.execute("DROP TABLE payments")
        self.cur.execute("DROP TABLE debits")
        self.con.commit()
