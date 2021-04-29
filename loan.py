from datetime import date, datetime, timedelta
from uuid import uuid4
from database import Database

db = Database()
class Loan():
    def __init__(self, data_map):
        self.id = data_map["id"]
        self.monthlyPaymentAmount = data_map["monthlyPaymentAmount"]
        self.paymentDueDay        = data_map["paymentDueDay"]
        self.scheduleType         = data_map["scheduleType"]
        self.debitStartDate       = data_map["debitStartDate"]
        self.daysOfMonth          = data_map["daysOfMonth"]
        self.debitFrequency       = data_map["debitFrequency"]
        self.hasGracePeriod       = data_map["hasGracePeriod"]
        self.schedule = Schedule()
        if not db.queryLoans(self.id):
            db.saveLoan(self)

    def generatePaymentSchedule(self, years=0, months=0):
        for debits, payment in self.schedule.generatePaymentSchedule(self, years, months):
            db.savePaymentAndDebits(debits, payment)

class Debit():
    def __init__(self, loanId, date, amount, debId=None):
        if debId == None:
            self.id = str(uuid4())
        else:
            self.id = debId
        self.loanId = loanId
        self.debitDate = date
        self.debitAmount = amount

class Payment():
    def __init__(self, loanId, date, amount, payId=None):
        if payId == None:
            self.id = str(uuid4())
        else:
            self.id = payId
        self.loanId = loanId
        self.paymentDate = date
        self.paymentAmount = amount

class Calendar():
    def __init__(self):
        self.weekdayMap = {"monday": 0, "tuesday": 1,
                           "wednesday": 2, "thursday": 3,
                           "friday": 4}
    def _scrape_holidays():
        pass

    def getBiweekly(self, start, dayOfWeek, endDate, dateFormat):
        dates = []
        currentDate = datetime.strptime(start, dateFormat).date()
        currentDate = self.nextDay(currentDate, dayOfWeek)
        while currentDate <= endDate:
            dates.append(currentDate)
            currentDate = currentDate + timedelta(weeks=2)
        return dates

    def getSemiMonthly(self, start, days, endDate, dateFormat):
        dates = []
        currentDate = datetime.strptime(start, dateFormat).date()
        while currentDate <= endDate:
            tmpDates = []
            for day in days:
                tmpDate = self.nextOccurence(currentDate.strftime(dateFormat), day, dateFormat)
                tmpDates.append(tmpDate)
            currentDate = min(tmpDates)
            if currentDate > endDate:
                break
            dates.append(currentDate)
            currentDate = currentDate + timedelta(days=1)
        return dates

    def nextDay(self, currDate, dayOfWeek):
        currDay = currDate.weekday()
        targetDay = self.weekdayMap[dayOfWeek]
        if targetDay == currDay:
            return currDate
        if targetDay > currDay:
            delta = targetDay - currDay
        else:
            delta = 7 - (currDay - targetDay)
        return currDate + timedelta(days=delta)

    def getClosestDay(self, year, month, day):
        successFlag = False
        while not successFlag:
            try:
                test = date(year, month, day)
                successFlag = True
            except:
                pass
            day -= 1
        return test.day

    def nextOccurence(self, start, dayOfMonth, dateFormat):
        nextDate = datetime.strptime(start, dateFormat).date()
        #nextDate = date(year=int(year), month=int(month), day=int(day))
        if dayOfMonth >= 28:
            day = self.getClosestDay(nextDate.year, nextDate.month, dayOfMonth)
        else:
            day = dayOfMonth
        if nextDate.day <= day:
            nextDate = nextDate.replace(day=day)
        elif nextDate.month < 12:
            nextDate = nextDate.replace(month=nextDate.month+1, day=1)
            day = self.getClosestDay(nextDate.year, nextDate.month, dayOfMonth)
            nextDate = nextDate.replace(day=day)
        else:
            nextDate = nextDate.replace(year=nextDate.year+1, month=1, day=1)
            day = self.getClosestDay(nextDate.year, nextDate.month, dayOfMonth)
            nextDate = nextDate.replace(day=day)
        return nextDate

    def adjustDate(self, dateObj):
        while self.isHoliday(dateObj) or self.isWeekend(dateObj):
            dateObj = dateObj - timedelta(days=1)
        return dateObj

    def isWeekend(self, dateObj):
        return dateObj.weekday() > 4

    def isHoliday(self, dateObj):
        holidays = ["01/01/2021", "01/18/2021", "02/15/2021",
                    "05/31/2021", "07/05/2021", "09/06/2021",
                    "10/11/2021", "11/11/2021", "11/25/2021",
                    "12/24/2021"]
        return dateObj.strftime("%m/%d/%Y") in holidays

class Schedule():
    def __init__(self):
        self.calendar = Calendar()

    def generatePaymentSchedule(self, loan, years=0, months=0):
        print(loan.id)
        if years > 0:
            months += years*12
        dateFormat = "%m/%d/%Y"
        startDate = loan.debitStartDate
        inclusive = True
        for _ in range(months):
            paymentDate = self.calendar.nextOccurence(startDate, loan.paymentDueDay, dateFormat)
            if loan.scheduleType == "biweekly":
                debitDates = self.calendar.getBiweekly(startDate, loan.debitFrequency, paymentDate, dateFormat)
            else:
                debitDates = self.calendar.getSemiMonthly(startDate, loan.daysOfMonth, paymentDate, dateFormat)
            startDate = (paymentDate + timedelta(days=1)).strftime(dateFormat)
            debits = []
            debitAmount = loan.monthlyPaymentAmount / len(debitDates)
            for date in debitDates:
                debit = Debit(loan.id, date, debitAmount)
                debits.append(debit)
            if not loan.hasGracePeriod:
                paymentDate = self.calendar.adjustDate(paymentDate)
            payment = Payment(loan.id, paymentDate, loan.monthlyPaymentAmount)
            print(debitDates, paymentDate)
            yield debits, payment
