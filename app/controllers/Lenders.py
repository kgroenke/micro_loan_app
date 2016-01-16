from system.core.controller import *
from flask import Flask, session
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
flask_bcrypt = Bcrypt(app)
import re

class Lenders(Controller):
    def __init__(self, action):
        super(Lenders, self).__init__(action)
        self.load_model('Lender')

    def index(self):
        return self.load_view('register.html')

    def register_lender(self):
            lender_info = {
            "first_name" : request.form.get('first_name'),
            "last_name" : request.form.get('last_name'),
            "email" : request.form.get('email'),
            "password" : request.form.get('password'),
            "pw_confirm" : request.form.get('pw_confirm'),
            "account_bal" : request.form.get('start_bal')
        }
            create_status = self.models['Lender'].add_lender(lender_info)
            if create_status['status'] == True:
                return redirect('/lenders/home')
            else:
                for message in create_status['errors']:
                    flash(create_status['errors'])
                    return redirect('/')

    def register_borrower(self):
            borrower_info = {
            "first_name" : request.form.get('first_name'),
            "last_name" : request.form.get('last_name'),
            "email" : request.form.get('email'),
            "password" : request.form.get('password'),
            "pw_confirm" : request.form.get('pw_confirm'),
            "need" : request.form.get('need'),
            "title" : request.form.get('title'),
            "description" : request.form.get('description')
        }
            create_status = self.models['Lender'].add_borrower(borrower_info)
            if create_status['status'] == True:
                return redirect('/borrowers/home')
            else:
                for message in create_status['errors']:
                    flash(create_status['errors'])
                    return redirect('/')

    def lender_home(self):
        lender_profile_info = self.models['Lender'].lender_profile()
        borrowers_need = self.models['Lender'].get_borrowers_need()
        my_borrowers = self.models['Lender'].get_my_borrowers()
        return self.load_view('lender_home.html', profile_info=lender_profile_info[0], borrowers_need=borrowers_need, my_borrowers=my_borrowers)

    def borrower_home(self):
        borrower_profile_info = self.models['Lender'].borrower_profile()
        borrower_loans = self.models['Lender'].get_borrower_loans()
        print "@@@@@@@@@@@@@@@@@@@"
        print borrower_profile_info[0]
        print borrower_loans
        return self.load_view('borrower_home.html', profile_info=borrower_profile_info[0], borrower_loans=borrower_loans)

    def login_view(self):
        return self.load_view('login.html')

    def login(self):
        login_info = {
        "email" : request.form.get('email'),
        "password" : request.form.get('password')
        }
        login_status = self.models['Lender'].login_user(login_info)

        if login_status['status'] == True:
            if login_status['type'] == "lender":
                return redirect('/lenders/home')
            elif login_status['type'] == "borrower":
                return redirect('/borrowers/home')
        else:
            invalid = "Error: invalid username or password"
            return redirect

    def logout(self):
        session.clear()
        return redirect('/')

    def lend(self, bor_id):
        loan_amount = request.form.get('loan_amount')
        loan_info = self.models['Lender'].create_loan(loan_amount, bor_id)
        return redirect('/lenders/home')
