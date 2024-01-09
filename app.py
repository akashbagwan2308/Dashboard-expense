from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import pandas as pd
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'asdfghjklpoiuytrewq1234567890mnbvcxz'

current_date = datetime.now()
current_month_number = current_date.month

# Load initial data from the Excel file
excel_file_path = 'E:/expense2024_dashboard.xlsx'
sheet_name = 'Sheet1'
 
df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
budget_df = pd.read_excel(excel_file_path, sheet_name='Sheet2')


def read_data_budget():
    return budget_df.to_dict(orient='records')

def write_data_budget(new_data):
    global budget_df  # Declare df as a global variable
    budget_df_new = pd.DataFrame(new_data)
    budget_df = pd.concat([budget_df, budget_df_new], ignore_index=True)
    budget_df.to_excel(excel_file_path, index=False)
    return {'message': 'Data updated successfully!'}


def read_data():
    return df.to_dict(orient='records')

def write_data(new_data):
    global df  # Declare df as a global variable
    df_new = pd.DataFrame(new_data)
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_excel(excel_file_path, index=False)
    return {'message': 'Data updated successfully!'}


def calculate_financial_metrics():
    total_income = df.loc[df['Transaction'] == 'Deposit', 'Amount'].sum()
    total_expense = df.loc[df['Transaction'] == 'Expense', 'Amount'].sum()
    balance = total_income -total_expense
    return total_income, total_expense, balance

def calulate_expense_metrics():
    food = df.loc[df['Category'].isin(['Lunch', 'Nashta', 'Dinner', 'Eve.Break', 'Off Dinner']), 'Amount'].sum()
    rent = df.loc[df['Category'] == 'Rent', 'Amount'].sum()
    personal = df.loc[df['Category'] == 'Personal', 'Amount'].sum()
    recharge = df.loc[df['Category'] == 'Recharges', 'Amount'].sum()
    e_bill = df.loc[df['Category'] == 'E - Bill', 'Amount'].sum()
    grocery = df.loc[df['Category'] == 'Grocery', 'Amount'].sum()
    travel = df.loc[df['Category'] == 'Travel', 'Amount'].sum()
    stationary = df.loc[df['Category'] == 'Stationary', 'Amount'].sum()
    return food, rent, personal,recharge, e_bill, grocery, travel, stationary


def calculate_expense_metrics(selected_month):
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    #print(df['Date'])
    # Filter data for the selected month
    selected_month_data = df[df['Date'].dt.month == int(selected_month)]


    food = selected_month_data.loc[selected_month_data['Category'].isin(['Lunch', 'Nashta', 'Dinner', 'Eve.Break', 'Off Dinner']), 'Amount'].sum()
    rent = selected_month_data.loc[selected_month_data['Category'] == 'Rent', 'Amount'].sum()
    personal = selected_month_data.loc[selected_month_data['Category'] == 'Personal', 'Amount'].sum()
    recharge = selected_month_data.loc[selected_month_data['Category'] == 'Recharges', 'Amount'].sum()
    e_bill = selected_month_data.loc[selected_month_data['Category'] == 'E - Bill', 'Amount'].sum()
    grocery = selected_month_data.loc[selected_month_data['Category'] == 'Grocery', 'Amount'].sum()
    travel = selected_month_data.loc[selected_month_data['Category'] == 'Travel', 'Amount'].sum()
    stationary = selected_month_data.loc[selected_month_data['Category'] == 'Stationary', 'Amount'].sum()
    expense = selected_month_data.loc[selected_month_data['Transaction'] == 'Expense', 'Amount'].sum()


    return food, rent, personal, recharge, e_bill, grocery, travel, stationary,expense


def login_is_successful(email, password):
    # Replace these values with your actual authentication logic
    valid_email = "akashbagwan01"
    valid_password = "Akash@2308"

    # Check if the provided email and password match the predefined values
    return email == valid_email and password == valid_password


@app.route('/login', methods=['POST'])
def login():

        username = request.form['username']
        password = request.form['password']
        print(username,password)

        if login_is_successful(username, password):
            # If successful, redirect to the profile page
            return redirect(url_for('profile'))
        return render_template('index.html')

@app.route('/logout')
def logout():
    # Redirect to the index page and set headers to prevent caching
    # Clear user session on logout
    session.pop('user', None)
    # Redirect to the index page
    return redirect(url_for('index'))

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/statistics')
def statistics():
    #return render_template('statistics.html')
    total_income, total_expense, balance = calculate_financial_metrics()
    food, rent, personal,recharge, e_bill, grocery, travel, stationary = calulate_expense_metrics()
    profit__loss = int(budget_df[int(current_month_number)][-1:]) + recharge + e_bill - total_expense
    return render_template('statistics.html', total_income=total_income,
                           total_expense=total_expense, profit_loss=profit__loss, balance=balance,food=food, rent=rent, personal=personal,recharge=recharge, e_bill=e_bill,
                           grocery=grocery, travel=travel, stationary=stationary)

@app.route('/dashboard')
def dashboard():
    total_income, total_expense, balance = calculate_financial_metrics()
    food, rent, personal, recharge, e_bill, grocery, travel, stationary = calulate_expense_metrics()
    profit__loss = int(budget_df[int(current_month_number)][-1:]) + recharge + e_bill - total_expense
    return render_template('dashboard.html', total_income=total_income, total_expense=total_expense, profit_loss=profit__loss, balance=balance)

@app.route('/profile')
def profile():

    latest_data = read_data()[-5:][::-1]  # Get the latest 5 data entries
    total_income, total_expense, balance = calculate_financial_metrics()
    food, rent, personal, recharge, e_bill, grocery, travel, stationary = calulate_expense_metrics()
    profit__loss = int(budget_df[int(current_month_number)][-1:]) + recharge + e_bill - total_expense
    return render_template('profile.html', latest_data=latest_data, total_income=total_income,
                           total_expense=total_expense, profit_loss=profit__loss, balance=balance)

# Add a new route to handle data operations
@app.route('/get_data', methods=['GET'])
def get_data():
    data = read_data()
    print("Data Read:", data)
    return jsonify(data)

@app.route('/update_data', methods=['POST'])
def update_data():
    new_data = request.get_json()
    result = write_data(new_data)
    print("Data Updated:", result)
    return jsonify(result)

# Add a new route to handle adding expenses and deposits
@app.route('/add_expense', methods=['POST'])
def add_expense():
    new_expense = {
        'Date': request.form['date'],
        'Transaction': request.form['transaction'],
        'Description': request.form['description'],
        'Amount': float(request.form['amount']),
        'Category': request.form['category']
    }
    result = write_data([new_expense])
    print("Expense/Deposit Added:", result)
    return redirect(url_for('dashboard'))  # Redirect to dashboard after adding expense/deposit




# Example usage for January (month number 1)

@app.route('/filter_by_month', methods=['POST'])
def filter_by_month():
    month = request.form['month']
    food_expense, rent_expense, personal_expense, recharge_expense, e_bill_expense, grocery_expense, travel_expense, stationary_expense ,expense= calculate_expense_metrics(
        month)
    profit = int(budget_df[int(month)][-1:]) + recharge_expense + e_bill_expense -expense
    year = [" Select Month ", 'January','February','March','April','May','June','July','August','September','October','November','December']
    month = year[int(month)]

    #print(month, food_expense, rent_expense, personal_expense, recharge_expense, e_bill_expense, grocery_expense, travel_expense, stationary_expense)
    return render_template('statistics.html', month = month, food= food_expense, rent=rent_expense, personal= personal_expense,
                           recharge = recharge_expense, e_bill= e_bill_expense,grocery =  grocery_expense, travel = travel_expense,
                           stationary = stationary_expense,profit=profit,expense=expense)

@app.route('/set_budget',methods=['POST'])
def set_budget():
    budget = request.form['budget']
    budget_month = request.form['budget_month']
    old_budget = budget_df
    old_budget[int(budget_month)]=budget
    new_budget = old_budget
    write_data_budget(new_budget)
    return redirect(url_for('budget'))


@app.route('/budget')
def budget():
    budget_data = read_data_budget()[-1:]
    print(budget_data)
    return render_template('budget.html',budget_data = budget_data)

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    entry_index = int(request.form['entry_index'])
    #print(-entry_index-1)
    global df
    df = df.drop(df.index[-entry_index-1]).reset_index(drop=True)
    df.to_excel(excel_file_path, index=False)

    return redirect(url_for('profile'))

@app.route('/faq')
def faq():
    return render_template('faq.html')

if __name__ == '__main__':
    app.run(debug=True)

