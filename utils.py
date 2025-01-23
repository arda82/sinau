#utils.py
import sqlite3
from datetime import date
from table import Table


def count_days():
    today = date.today()
    print(f"Sekarang tanggal: {today.strftime('%d, %m, %Y')}\n")
    
    while True:
        try:
            # Input tanggal awal
            start_input = input("Masukan tanggal mulai (DD,MM,YYYY): ")
            day, month, year = map(int, start_input.split(','))
            start_date = date(year, month, day)

            # Input tanggal akhir
            end_input = input("Masukan tanggal akhir (DD,MM,YYYY) atau tekan Enter untuk tanggal sekarang: ").strip()
            if not end_input:  # Jika pengguna tidak memasukkan tanggal akhir
                end_date = today
            else:
                day, month, year = map(int, end_input.split(','))
                end_date = date(year, month, day)

            # Hitung selisih hari (bisa bernilai negatif jika start_date > end_date)
            difference = (end_date - start_date).days

            # Tampilkan hasil
            print(f"\nSelisih {difference} hari dari {start_date.strftime('%d, %m, %Y')} and {end_date.strftime('%d, %m, %Y')}.\n")

            # Tanya apakah pengguna ingin melanjutkan
            choice_exit = input("Hitung lagi? (y/n): ").strip().lower()
            if choice_exit == 'n':
                print("Program berakhir. Bye!")
                break

        except ValueError:
            print("Format tuliasan salah. masukan data dengan format DD,MM,YYYY dipisah koma.\n")

def get_all_tables(data_file):
    try:
        with sqlite3.connect(data_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'android_%';")
            tables = [row[0] for row in cursor.fetchall()]
        return tables
    except Exception as e:
        print(f"Failed to retrieve table names: {e}")
        return []

def validate_table_name(table_name):
    if not table_name.isidentifier():
        raise ValueError("Invalid table name. Please enter a valid identifier.")

def create_table_with_columns(data_file, table_name, columns, column_types):
    try:
        column_definitions = [f"{col.strip()} {type_.strip()}" for col, type_ in zip(columns, column_types)]
        table = Table(data_file, table_name, column_definitions)
        print(f"Table '{table_name}' created successfully!")
    except Exception as e:
        print(f"Failed to create table: {e}")

def delete_table(data_file, table_name):
    try:
        table = Table(data_file, table_name)
        table.drop()
        print(f"Table '{table_name}' deleted successfully!")
    except Exception as e:
        print(f"Failed to delete table: {e}")

def select_table(data_file, tables):
    table_name = input("Enter name of the table to select: ")
    if table_name not in tables:
        print(f"Table '{table_name}' does not exist. Please select a valid table.")
        return None

    try:
        table = Table(data_file, table_name)
        print(f"Table '{table_name}' selected.")
        return table
    except Exception as e:
        print(f"Failed to select table: {e}")
        return None

def view_table_contents(table):
    if table is None:
        print("No table selected. Please select a table first.")
        return

    try:
        cursor = table.select_all()
        column_names = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        cursor.close()

        for row in results:
            for col_name, col_value in zip(column_names, row):
                print(f"{col_name}: {col_value}")
            print()  # Empty line between rows
        
        print("Table contents displayed successfully.")
    except Exception as e:
        print(f"Failed to display table contents: {e}")

def insert_data_into_table(table):
    if table is None:
        print("No table selected. Please select a table first.")
        return

    try:
        cursor = table.select_all()
        column_names = [description[0] for description in cursor.description]
        cursor.close()

        data_values = []
        for column_name in column_names:
            value = input(f"Enter value for column '{column_name}' (leave empty for NULL): ")
            if value == "":
                data_values.append("")
            else:
                data_values.append(value)

        table.insert(*data_values)
        print("Data inserted into table successfully.")
    except Exception as e:
        print(f"Failed to insert data into table: {e}")

def edit_table_data(table):
    if table is None:
        print("No table selected. Please select a table first.")
        return

    try:
        cursor = table.select_all()
        column_names = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        cursor.close()

        if not results:
            print("The table is empty. No data to edit.")
            return

        for idx, row in enumerate(results):
            print(f"{idx + 1}: {row}")

        while True:
            try:
                row_number = int(input("Enter the row number to edit (starting from 1): "))
                if row_number <= 0 or row_number > len(results):
                    raise ValueError("Invalid row number. Please enter a valid row number.")
                break
            except ValueError as ve:
                print(ve)

        row_data = list(results[row_number - 1])  # Adjust for 0-based indexing

        new_values = []
        for i, (column_name, value) in enumerate(zip(column_names, row_data)):
            new_value = input(f"Enter new value for column '{column_name}' (current value: '{value}'): ")
            if new_value:  # Only update if the user entered a new value
                new_values.append(new_value)
            else:
                new_values.append(value)

        set_args = {col: val for col, val in zip(column_names, new_values)}
        where_args = {column_names[0]: row_data[0]}  # Primary key is used in the WHERE clause

        table.update(set_args, **where_args)
        print("Row data updated successfully!")
    except sqlite3.Error as sql_e:
        print(f"SQLite error occurred: {sql_e}")
    except Exception as e:
        print(f"Failed to edit table data: {e}")
        
def add_column_to_table(table):
    if table is None:
        print("No table selected. Please select a table first.")
        return

    try:
        column_name = input("Enter name for the new column: ")
        column_type = input("Enter data type for the new column (e.g., TEXT, INTEGER): ")
        table_name = table.table_name

        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        table.write(alter_query)
        print(f"Column '{column_name}' added successfully to table '{table_name}'!")
    except Exception as e:
        print(f"Failed to add column to table: {e}")
        
def delete_column_from_table(table):
    if table is None:
        print("No table selected. Please select a table first.")
        return

    try:
        # Fetch the current columns
        cursor = table.select_all()
        column_names = [description[0] for description in cursor.description]
        cursor.close()

        print("Available columns in the table:")
        for col in column_names:
            print(f" - {col}")

        column_name = input("Enter the name of the column to delete: ")

        if column_name not in column_names:
            print(f"Column '{column_name}' does not exist in the table '{table.table_name}'.")
            return

        table_name = table.table_name

        # Prepare new columns excluding the column to be deleted
        new_columns = [col for col in column_names if col != column_name]

        # Create a temporary table with the new columns
        new_table_name = f"{table_name}_new"
        column_definitions = [f"{col} {table.db.execute(f'PRAGMA table_info({table_name})').fetchall()[column_names.index(col)][2]}" for col in new_columns]
        create_temp_table_query = f"CREATE TABLE {new_table_name} ({', '.join(column_definitions)})"
        table.write(create_temp_table_query)

        # Copy data to the temporary table
        columns_str = ", ".join(new_columns)
        copy_data_query = f"INSERT INTO {new_table_name} ({columns_str}) SELECT {columns_str} FROM {table_name}"
        table.write(copy_data_query)

        # Drop the old table
        table.drop_table(table_name)

        # Rename the temporary table to the original table name
        rename_table_query = f"ALTER TABLE {new_table_name} RENAME TO {table_name}"
        table.write(rename_table_query)

        print(f"Column '{column_name}' deleted successfully from table '{table_name}'!")
    except sqlite3.Error as sql_e:
        print(f"SQLite error occurred: {sql_e}")
    except Exception as e:
        print(f"Failed to delete column from table: {e}")