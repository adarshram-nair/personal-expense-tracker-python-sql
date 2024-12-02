import os, sqlite3, datetime as dt

def new_database():
    tracker_db_cursor.execute('Create Table expense_tracker (TransID int Primary Key, Amount float, Category varchar(25), date date, description varchar(100) default NULL)')
    tracker_db_cursor.execute('Create Table expense_tracker_deleted (TransID int Primary Key, Amount float, Category varchar(25), date date, description varchar(100) default NULL)')

    print('New Database File Created')

def view_expenses(table = 'expenses'):

    rows = []

    if table == 'expenses':
        year, month = year_month()
        category, con = expense_categories_output()
        if con == 0:
            print('No transactions Found')
            return None

        tracker_db_cursor.execute("SELECT * from expense_tracker "
                                  "WHERE (category = ? or ? is null) and "
                                  "(strftime('%Y',date) = ? or ? is null) and (strftime('%m',date) = ? or ? is null) "
                                  "ORDER BY TransID",
                                  (category, category, year, year, month, month))
        rows = tracker_db_cursor.fetchall()

    elif table == 'deleted':
        tracker_db_cursor.execute("SELECT * from expense_tracker_deleted "
                                  "ORDER BY TransID")
        rows = tracker_db_cursor.fetchall()

        if not rows:
            print('No transactions Found')
            return None

    print(('Transaction ID', 'Amount (INR)', 'Category', 'Date', 'Description'))
    for i in rows:
        print(i)

def date_input():
    while True:
        date = input('Date (YYYY-MM-DD): ')
        #to verify whether the entered date is in correct format or not
        try:
            dt.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print('Invalid Input. Please enter date in correct format.')
        else:
            return date

def insert_expense():

    #to find the current TransID, so that we don't send any duplicate TransID.
    #It will be checked from both expense table as well as that of deleted table.

    while True:
        tracker_db_cursor.execute('Select ifnull(max(TransID),0) from expense_tracker')
        max_track = tracker_db_cursor.fetchall()[0][0]

        tracker_db_cursor.execute('Select ifnull(max(TransID),0) from expense_tracker_deleted')
        max_del = tracker_db_cursor.fetchall()[0][0]

        curr_trans_id = max(max_track, max_del)

        del max_track
        del max_del

        id = curr_trans_id + 1
        amount = input('Amount (INR): ')
        category = expense_categories_input()
        date = date_input()
        description = input('Description: ')

        tracker_db_cursor.execute("INSERT INTO expense_tracker VALUES(?,?,?,?,?)", (id, amount, category, date, description))
        tracker_db_conn.commit()

        con = input('Just press enter to go back or enter any character to add another expense: ')
        if con == '':
            break
        else:
            continue

def main_menu():

    #If the required tables are not in the db file due to any modification,
    # then we will create the db file again but the existing data will be lost.

    tracker_db_cursor.execute("SELECT * from sqlite_master where type = 'table'")
    table_details = tracker_db_cursor.fetchall()
    tables = []
    for table in table_details:
        tables.append(table[1])

    # if there is a warning while running the program for the first time, the screen shouldn't be cleared.
    # hence using the following boolean value.
    warning = False

    if 'expense_tracker' not in tables or 'expense_tracker_deleted' not in tables:
        print('No Data is available / the available data is corrupted. New Database is being created.This will erase all previous data.')
        new_database()
        warning = True

    del table_details
    del tables

    exit = False

    while not exit:
        if not warning:
            clear_screen()
        warning = False
        print('\nExpense Tracker\n')

        print('Select from the following operations:\n1. Add a new expense\n2. View expenses')
        print('3. View expense summary\n4. Delete expenses\n5. View deleted expenses')
        print("\nOr enter '0' to exit\n")

        while True:
            option = input('Enter the option number from the above list: ')
            if option in ['0','1','2','3','4','5']:
                break
            else:
                print('Invalid Input')

        if option == '0':
            exit = True
        elif option == '1':
            insert_expense()
            exit = not continue_using()
        elif option == '2':
            view_expenses()
            exit = not continue_using()
        elif option == '3':
            expense_summary()
            exit = not continue_using()
        elif option == '4':
            delete_transaction()
            exit = not continue_using()
        elif option == '5':
            view_expenses('deleted')
            exit = not continue_using()

def continue_using():
    while True:
        cont = (input('\nView/add/delete expenses (Y/N)?')).lower()
        if cont == 'y':
            return True
        elif cont == 'n':
            return False
        else:
            print('Invalid Input')

def clear_screen():
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    except:
        pass


def expense_categories_input():

    categories = {'food', 'medicine', 'fuel', 'grocery', 'clothes', 'bills', 'recharge', 'medicine', 'travel'}

    tracker_db_cursor.execute('SELECT distinct category FROM expense_tracker')
    categories_db = tracker_db_cursor.fetchall()


    if categories_db:
        for i in categories_db:
            categories.add(i[0])

    categories = list(categories)

    for i in range(len(categories)):
        print(f"{i+1}. {categories[i]}")

    while True:
        category = input('Category - Select the number from the above list or mention it directly: ').lower()
        if category.isdigit():
            if int(category) > len(categories) or int(category) < 1:
                print('Invalid Category Number')
            else:
                return categories[int(category) - 1]
        else:
            return category

def expense_categories_output():

    tracker_db_cursor.execute('SELECT distinct category FROM expense_tracker')
    categories_db = tracker_db_cursor.fetchall()
    if not categories_db:
        return None,0
    categories = []
    if categories_db:
        for i in categories_db:
            categories.append(i[0])

    for i in range(len(categories)):
        print(f"{i+1}. {categories[i]}")

    while True:
        print('Please mention the category of expense to filter data. If not required, just press enter')
        category = input('Category - Select the number from the above list or mention it directly: ').lower()
        if category.isdigit():
            if int(category) > len(categories) or int(category) < 1:
                print('Invalid Input')
                continue
            else:
                return categories[int(category) - 1]
        elif category in categories:
            return category,1
        elif category == '':
            return None,1
        else:
            print('Invalid Input')
            continue

def expense_summary():
    clear_screen()
    from calendar import month_name as mn
    print('Expense Summary')

    while True:
        print('\nChoose a filter for summary:'
              '\n1. Year & Month\n2. Category\n3. Year, Month & Category\n'
              '4. No Filter - Summarize by year, month and category\n'
              '\nEnter 0 to go back')
        summary_option = input("Select the option number: ")

        if summary_option in ('0', '00'):
            break

        elif summary_option in ('1', '01'):
            # return summary as per month
            year, month = year_month()
            tracker_db_cursor.execute("SELECT category, "
                                      "count(amount) total_count, sum(amount) total_sum "
                                      "FROM expense_tracker "
                                      "WHERE (strftime('%Y',date) = ? or ? is null) "
                                      "and (strftime('%m',date) = ? or ? is null) "
                                      "GROUP BY category "
                                      "Order BY total_count desc, total_sum desc, category",
                                      (year, year, month, month)
                                      )
            summary_output = tracker_db_cursor.fetchall()
            if not summary_output:
                print('No transactions found!')
            else:
                if (month, year) == (None, None):
                    print('',end='')
                elif month is None:
                    print(f'For {year}:')
                elif year is None:
                    print(f'For Year')
                else: print(f'For {mn[int(month)]}, {year}:')
                for i in summary_output:
                    print(f'Total {i[1]} transaction/s had been done on '
                          f'{i[0]}, accounting to total of INR {i[2]}.')

        elif summary_option in ('2', '02'):
            #return summary as per category
            category, con = expense_categories_output()[0]
            tracker_db_cursor.execute("SELECT strftime('%Y',date) as year, "
                                      "strftime('%m',date) as month, "
                                      "count(amount) total_count, sum(amount) total_sum "
                                      "FROM expense_tracker "
                                      "WHERE (category = ? or ? is null) "
                                      "GROUP BY year, month "
                                      "Order BY year, month, total_count desc, total_sum desc",
                                      (category, category)
                                      )
            summary_output = tracker_db_cursor.fetchall()
            if not summary_output:
                print('No transactions found!')
            else:
                if category is None:
                    print('', end = '')
                else:
                    print(f'For {category}: ')
                for i in summary_output:
                    print(f'Total {i[2]} transaction/s had been done on '
                          f'{mn[int(i[1])]},{i[0]}, accounting to total of INR {i[3]}.')


        elif summary_option in ('3', '03'):
            # return summary as per month and category
            year, month = year_month()
            category = expense_categories_output()[0]
            tracker_db_cursor.execute("SELECT count(amount) total_count, sum(amount) total_sum "
                              "FROM expense_tracker "
                              "WHERE (strftime('%Y',date) = ? or ? is null) "
                              "and (strftime('%m',date) = ? or ? is null) "
                              "and (category = ? or ? is null) "
                              "Order BY total_count desc, total_sum desc",
                              (year, year, month, month, category, category)
                              )
            summary_output = tracker_db_cursor.fetchall()
            if not summary_output:
                print('No transactions found!')
            else:
                print(f'For category - {category} on month - {month}, year - {year}')
                for i in summary_output:
                    print(f'Total {i[0]} transaction/s had been done '
                          f'accounting to total of INR {i[1]}.')

        elif summary_option in ('4', '04'):
            # return summary as per month and category
            tracker_db_cursor.execute("SELECT strftime('%Y',date) as year, "
                                      "strftime('%m',date) as month, category, "
                              "count(amount) total_count, sum(amount) total_sum "
                              "FROM expense_tracker "
                              "GROUP BY year, month, category "
                              "Order BY year, month, total_count desc, total_sum desc, category")
            summary_output = tracker_db_cursor.fetchall()
            if not summary_output:
                print('No transactions found!')
            else:
                summary_output_date = []
                for i in summary_output:
                    if f'{mn[int(i[1])]}, {i[0]}' not in summary_output_date:
                        summary_output_date.append(f'{mn[int(i[1])]}, {i[0]}')
                for j in summary_output_date:
                    print(f'In {j}:')
                    for k in summary_output:
                        if f'{mn[int(k[1])]}, {k[0]}' == j:
                            print(f'Total {k[3]} transaction/s had been done on '
                          f'{k[2]}, accounting to total of INR {k[4]}.')
        else:
            print('Invalid Input')

def year_month():
    while True:
        print('Please mention the year and month to filter data. If not required, just press enter')
        year = input('Year - YYYY: ')
        month = input('Month: ').lower()
        if year == '' or (len(year) == 4 and year.isdigit() and month in ['', '1', 'january', 'jan', '2', 'february', 'feb', '3', 'march', 'mar', '4', 'april', 'apr', '5', 'may', 'may', '6', 'june', 'jun', '7', 'july', 'jul', '8', 'august', 'aug', '9', 'september', 'sep', '10', 'october', 'oct', '11', 'november', 'nov', '12', 'december', 'dec','01', '02', '03', '04', '05', '06', '07', '08', '09']):
            break
        else:
            print('Invalid Input')
            continue
    if year == '':
        year = None

    if month in ('1', 'january', 'jan', '01'):
        return (year, '01')
    elif month in ('2', 'february', 'feb', '02'):
        return (year, '02')
    elif month in ('3', 'march', 'mar', '03'):
        return (year, '03')
    elif month in ('4', 'april', 'apr', '04'):
        return (year, '04')
    elif month in ('5', 'may', 'may', '05'):
        return (year, '05')
    elif month in ('6', 'june', 'jun', '06'):
        return (year, '06')
    elif month in ('7', 'july', 'jul', '07'):
        return (year, '07')
    elif month in ('8', 'august', 'aug', '08'):
        return (year, '08')
    elif month in ('9', 'september', 'sep', '09'):
        return (year, '09')
    elif month in ('10', 'october', 'oct'):
        return (year, '10')
    elif month in ('11', 'november', 'nov'):
        return (year, '11')
    elif month in ('12', 'december', 'dec'):
        return (year, '12')
    else:
        return (year, None)

def delete_transaction():
    clear_screen()
    print('Delete Expenses:')
    print('\nPlease check the available data:\n')
    view_expenses()

    while True:
        print('\nTransaction ID is required to delete any transaction.\n'
              'Please find the Transaction ID from the above data\n'
              'Note: Once deleted data can not be retrieved.'
              "You can view the deleted data in 'View deleted expenses' in the Main Menu")

        tracker_db_cursor.execute('SELECT distinct TransID '
                                  'FROM expense_tracker')
        trans_id_output = tracker_db_cursor.fetchall()
        if not trans_id_output:
            print('No transactions found')
            break
        trans_id_list = [i[0] for i in trans_id_output]
        trans_id_input = input('Enter the Transaction ID (Press enter to exit): ')
        if trans_id_input == '':
            break
        elif not trans_id_input.isdigit():
            print('Invalid Input. Enter a valid number')
            continue
        elif int(trans_id_input) not in trans_id_list:
            print('No transactions found with the entered Transaction ID')
            continue
        else:
            tracker_db_cursor.execute("INSERT INTO expense_tracker_deleted "
                                  "SELECT * FROM expense_tracker WHERE TransId = ?",
                                  trans_id_input)
            tracker_db_cursor.execute('DELETE FROM expense_tracker WHERE TransId = ?',
                                      (trans_id_input))
            print('Deleted')
            tracker_db_conn.commit()
            continue


tracker_db_conn = sqlite3.connect('xpnse_trckr_db.db')
tracker_db_cursor = tracker_db_conn.cursor()

main_menu()

tracker_db_cursor.close()
tracker_db_conn.close()