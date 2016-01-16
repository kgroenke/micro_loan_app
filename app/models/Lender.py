from system.core.model import Model
from flask import Flask, session
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
flask_bcrypt = Bcrypt(app)
import re

class Lender(Model):
    def __init__(self):
        super(Lender, self).__init__()

    def add_lender(self, lender_info):
        password = lender_info['password']

        EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
        errors = []

        if len(lender_info['first_name']) < 1:
            errors.append('First name cannot be blank')
        if len(lender_info['last_name']) < 1:
            errors.append('Last name cannot be blank')
        if len(lender_info['email']) < 1:
            errors.append('email cannot be blank')
        if not EMAIL_REGEX.match(lender_info['email']):
            errors.append('Must enter a valid email')
        if len(lender_info['password']) < 8:
            errors.append('Password must be at least 8 characters')
        if lender_info['password'] != lender_info['pw_confirm']:
            errors.append('Passwords must match')

        if errors:
            return {
            "status" : False,
            "errors" : errors
            }
            print errors['errors']

        else:
            pw_hash = self.bcrypt.generate_password_hash(password)
            registration_query = "INSERT INTO lenders (first_name, last_name, email, pw_hash, account_bal, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', NOW(), NOW())".format(lender_info['first_name'], lender_info['last_name'], lender_info['email'], pw_hash, lender_info['account_bal'])
            self.db.query_db(registration_query)

            select_lender_query = "SELECT * FROM lenders ORDER BY id DESC LIMIT 1"
            lender = self.db.query_db(select_lender_query)
            session['id'] = lender[0]['id']

            session['first_name'] = lender_info['first_name']
            return{"status" : True}

    def add_borrower(self, borrower_info):
            password = borrower_info['password']

            EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
            errors = []

            if len(borrower_info['first_name']) < 1:
                errors.append('First name cannot be blank')
            if len(borrower_info['last_name']) < 1:
                errors.append('Last name cannot be blank')
            if len(borrower_info['email']) < 1:
                errors.append('email cannot be blank')
            if not EMAIL_REGEX.match(borrower_info['email']):
                errors.append('Must enter a valid email')
            if len(borrower_info['password']) < 8:
                errors.append('Password must be at least 8 characters')
            if borrower_info['password'] != borrower_info['pw_confirm']:
                errors.append('Passwords must match')
            if len(borrower_info['title']) < 1:
                errors.append('Must enter a need title')
            if len(borrower_info['description']) < 1:
                errors.append('Must enter a desctiption of your project')

            if errors:
                return {
                "status" : False,
                "errors" : errors
                }
                print errors['errors']

            else:
                pw_hash = self.bcrypt.generate_password_hash(password)
                registration_query = "INSERT INTO borrowers (first_name, last_name, email, pw_hash, funds_bal, need, title, description, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', 0, '{}', '{}','{}', NOW(), NOW())".format(borrower_info['first_name'], borrower_info['last_name'], borrower_info['email'], pw_hash, borrower_info['need'], borrower_info['title'], borrower_info['description'])
                self.db.query_db(registration_query)

                select_borrower_query = "SELECT * FROM borrowers ORDER BY id DESC LIMIT 1"
                borrower = self.db.query_db(select_borrower_query)
                session['id'] = borrower[0]['id']
                session['first_name'] = borrower_info['first_name']
                return{"status" : True}

    def login_user(self, login_info):
        password = login_info['password']
        signin_query = "SELECT * FROM lenders WHERE email='{}' LIMIT 1".format(login_info['email'])
        lender = self.db.query_db(signin_query)

        print "*************"
        print lender

        if lender != []:
            # print self.bcrypt.check_password_hash(user[0]['pw_hash'], password)
            if self.bcrypt.check_password_hash(lender[0]['pw_hash'], password):
                session['first_name'] = lender[0]['first_name']
                session['id'] = lender[0]['id']
                return {"status" : True,
                "type" : "lender"}
            else:
                return{"status" : False}
        else:
            signin_query_2 = "SELECT * FROM borrowers WHERE email='{}' LIMIT 1".format(login_info['email'])
            borrower = self.db.query_db(signin_query_2)

            if borrower != []:
                if self.bcrypt.check_password_hash(borrower[0]['pw_hash'], password):
                    session['first_name'] = borrower[0]['first_name']
                    session['id'] = borrower[0]['id']
                    return {"status" : True, "type" : "borrower" }
                else:
                    return{"status" : False}

    def borrower_profile(self):
        borrower_profile_query = "SELECT first_name, last_name, need, funds_bal FROM borrowers WHERE id= '{}'".format(session['id'])
        return self.db.query_db(borrower_profile_query)

    def get_borrower_loans(self):
        borrower_loans_query = "SELECT lenders.first_name, lenders.last_name, lenders.email, SUM(micro_loans.loan_amount) AS loans FROM lenders LEFT JOIN micro_loans ON lenders.id = micro_loans.lender_id WHERE micro_loans.borrower_id = '{}' GROUP BY lenders.id".format(session['id'])
        return self.db.query_db(borrower_loans_query)

    def lender_profile(self):
        lender_profile_query = "SELECT first_name, last_name, account_bal FROM lenders WHERE id= '{}'".format(session['id'])
        return self.db.query_db(lender_profile_query)

    def get_borrowers_need(self):
        borrower_need_query = "SELECT first_name, last_name, title, description, need, funds_bal, id FROM borrowers WHERE need > funds_bal"
        return self.db.query_db(borrower_need_query)

    def get_my_borrowers(self):
        my_borrowers_query  = "SELECT CONCAT(first_name, ' ', last_name) AS name, title, description, need, funds_bal, SUM(loan_amount) AS amount_lent FROM borrowers LEFT JOIN micro_loans ON borrowers.id = micro_loans.borrower_id WHERE micro_loans.lender_id = '{}' GROUP BY borrowers.id".format(session['id'])
        return self.db.query_db(my_borrowers_query)

    def create_loan(self, loan_amount, bor_id):
        create_loan_query = "INSERT INTO micro_loans (loan_amount, created_at, updated_at, lender_id, borrower_id) VALUES ('{}', NOW(), NOW(), '{}', '{}')".format(loan_amount, session['id'], bor_id)
        self.db.query_db(create_loan_query)

        update_borrower_query = "UPDATE borrowers SET funds_bal = funds_bal + '{}' WHERE id = '{}'".format(loan_amount, bor_id)
        self.db.query_db(update_borrower_query)

        update_lender_query = "UPDATE lenders SET account_bal = account_bal - '{}' WHERE id = '{}'".format(loan_amount, session['id'])
        self.db.query_db(update_lender_query)
