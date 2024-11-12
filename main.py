import tkinter as tk

from tkinter import messagebox

from tkinter import ttk

from tkcalendar import DateEntry

import mysql.connector

from mysql.connector import Error

import datetime

import string

import sys




# Global variable to hold MySQL connection after user login
mysql_connection = None
uname= None
pword= None






# MySQL Authentication Function (used for user-provided credentials)
def mysql_authenticate(uname, pword):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user=uname,
            password=pword
        )
        
        if connection.is_connected():
            return connection
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    return None


# Login window for MySQL authentication
def mysql_login_window(app):

    def perform_login():
        #make mysql_connection, MySQL--uname, pword gloabal variable for future use
        global mysql_connection, uname, pword
        uname = uname_entry.get()
        pword = pass_entry.get()

        # Authenticate the user with provided credentials
        mysql_connection = mysql_authenticate(uname, pword)
        if mysql_connection:
            messagebox.showinfo("Success", "MySQL Login Successful")
            print('MySQL Login Successful')
            
            # After MySQL login, run the SQL queries to set up the database and tables
            setup_database(mysql_connection)
            
            #to destroy login window
            login_win.destroy()
            app.connection = mysql_connection  # Store the connection in the app objec
            app.deiconify()  #restore a window that has been minimized or hidden.
            show_frame(app,app.login_frame)  # Show the app's login frame after successful MySQL login and setup
            
        else:
            messagebox.showerror("Error", "MySQL Login Failed")
            print('MySQL login Failed')

    # Creating the MySQL login window frame
    login_win = tk.Toplevel() #pop-up that opens over the main application window
    login_win.title("MySQL Login")
    login_win.geometry("400x250")  # Set window size (width x height)
    login_win.config(bg="#d3f8e2")  # #d3f8e2 is a hexadecimal color code greenclr

    
    # Adding labels, entry fields, and buttons
    tk.Label(login_win, text="MySQL Username:", bg="#d3f8e2", font=("Arial", 12)).pack(pady=10)
    uname_entry = tk.Entry(login_win, font=("Arial", 12)) #Creates an input field (entry widget)
    uname_entry.pack(pady=5)#entry field with 5 pixels of vertical padding for spacing.

    tk.Label(login_win, text="MySQL Password:", bg="#d3f8e2", font=("Arial", 12)).pack(pady=10)
    pass_entry = tk.Entry(login_win, show="*", font=("Arial", 12))
    pass_entry.pack(pady=5)

    # Login and Exit Button
    tk.Button(login_win, text="Login", command=perform_login, bg="#6c63ff", fg="white", font=("Arial", 12)).pack(pady=10)
    tk.Button(login_win, text="Exit",command=lambda: (app.quit(), app.destroy()), bg="#ff6b6b", fg="white", font=("Arial", 12)).pack(pady=5)



    
# Setup database with the additional passenger_details table
def setup_database(mysql_connection):
    try:
        cursor = mysql_connection.cursor()
        
        # Create the bus reservation database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS bus_reservation")
        cursor.execute("USE bus_reservation")
        
        # SQL for creating users_auth table
        users_auth_table = """
        CREATE TABLE IF NOT EXISTS users_auth (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(10) NOT NULL CHECK (LENGTH(phone) = 10 AND phone REGEXP '^[0-9]+$'),
            password VARCHAR(256) NOT NULL
        );
        """
        cursor.execute(users_auth_table)
        print("users_auth Table Created")
        
        # SQL for creating buses table
        buses_table = """
        CREATE TABLE IF NOT EXISTS buses (
            bus_id INT AUTO_INCREMENT PRIMARY KEY,
            bus_name VARCHAR(50),
            source VARCHAR(50),
            destination VARCHAR(50),
            departure_time TIME,
            arrival_time TIME,
            fare DECIMAL(10, 2),
            available_seats INT,
            bus_type ENUM('Sleeper', 'Semi-Sleeper', 'Sitting') NOT NULL
        );
        """
        cursor.execute(buses_table)
        print("buses Table Created")
        
        # SQL for creating bookings table
        bookings_table = """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            bus_id INT,
            seats_booked INT,
            booking_date DATE,
            FOREIGN KEY (user_id) REFERENCES users_auth(user_id),
            FOREIGN KEY (bus_id) REFERENCES buses(bus_id)
        );
        """
        cursor.execute(bookings_table)
        print("bookings Table Created")

        # SQL for creating passenger_details table
        passenger_details_table = """
        CREATE TABLE IF NOT EXISTS passenger_details (
            passenger_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL CHECK (age >= 1 AND age <= 99),
            gender ENUM('Male', 'Female', 'Others') NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        );
        """
        cursor.execute(passenger_details_table)
        print("passenger_details Table Created")
        
        # SQL to insert admin data into users_auth table, only if admin does not already exist
        check_admin_query = "SELECT COUNT(*) FROM users_auth WHERE username = 'admin'"
        insert_admin_query = """
            INSERT INTO users_auth (username, email, phone, password)
            VALUES (%s, %s, %s, %s);
        """
        
        # Check if admin already exists
        cursor.execute(check_admin_query)
        admin_exists = cursor.fetchone()[0]
        
        if admin_exists == 0:
            # Encoding admin password using a shift value based on phone's last digit
            admin_password = "admin@07"
            admin_phone = "9874561230"
            last_digit_admin = int(admin_phone[-1])
            
            # Correct encoding call here before saving to the database
            encoded_admin_password = encode(admin_password, last_digit_admin)
            
            # Data to be inserted for admin
            admin_data = ('admin', 'admin@gmail.com', admin_phone, encoded_admin_password)
            cursor.execute(insert_admin_query, admin_data)
            mysql_connection.commit()
            print("Admin details inserted with encoded password")
        else:
            print("Admin already exists, skipping insertion")
        
        messagebox.showinfo("Success", "Database and tables set up successfully")
        print('Database and Table creation success')
    
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        mysql_connection.rollback()

        

#create user login Frame        
def create_login_frame(app):
    
    # Container for all login elements
    main_container = tk.Frame(app.login_frame, bg="#f0f8ff")
    main_container.pack(expand=False, pady=(50, 0))

    # Title of page "Login" 
    tk.Label(main_container, text="Login", font=("Arial", 20), bg="#f0f8ff").pack(pady=(0, 5))
    
    # Container for the username and password fields
    login_container = tk.Frame(main_container, bg="#f0f8ff")
    login_container.pack()

    # Username field
    tk.Label(login_container, text="Username", bg="#f0f8ff").pack(pady=(5, 2))
    app.username_entry = tk.Entry(login_container)
    app.username_entry.pack(pady=(2, 5))

    # Password field
    tk.Label(login_container, text="Password", bg="#f0f8ff").pack(pady=(5, 2))
    app.password_entry = tk.Entry(login_container, show="*")
    app.password_entry.pack(pady=(2, 10))
    
    # Login and Signup Buttons 
    tk.Button(login_container, text="Login", command=lambda: login(app.username_entry.get(), app.password_entry.get(), app)).pack(pady=(10, 2))
    tk.Button(login_container, text="Signup", command=lambda: show_frame(app, app.signup_frame)).pack(pady=(2, 5))
        
        
        
        

        
# Function to handle login
def login(username, password, app):
    connection = mysql_authenticate(uname, pword)
    
    if connection:
        cursor = connection.cursor()
        
        try:
            cursor.execute("USE bus_reservation")
            
            # For login, we need to encode the input password using the same encoding logic (phone's last digit)
            cursor.execute("SELECT phone FROM users_auth WHERE username = %s", (username,))
            user_phone = cursor.fetchone()
            
            if not user_phone:
                messagebox.showerror("Login Failed", "Invalid username or password.")
                return
            
            last_digit = int(user_phone[0][-1])  # Extract last digit from phone for encoding shift
            encoded_password = encode(password, last_digit)
            
            # Check if admin
            if username == "admin" and password == "admin@07":
                # Show bus detail entry for admin
                show_frame(app, app.admin_frame)
                return
            
            # Query for non-admin users with the encoded password
            cursor.execute("SELECT * FROM users_auth WHERE username = %s AND password = %s",
                           (username, encoded_password))
            user = cursor.fetchone()
            
            
            # Query for non-admin users with the encoded password
            cursor.execute("SELECT * FROM users_auth WHERE username = %s AND password = %s",
                           (username, encoded_password))
            user = cursor.fetchone()
            
            
            if user:
                messagebox.showinfo("Login Success", "Welcome!")
                print('User Login Sucessfull')
                app.current_user_id = user[0]
                clear_inputs(app)
                show_frame(app, app.bus_selection_frame)
                populate_cities(app)
                
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
                
        except mysql.connector.Error as e:
            messagebox.showerror("Login Error", f"Error during login: {e}")
            
        finally:
            connection.close()


            
            
#Create Signup frame for user
def create_signup_frame(app):

    # Container for all signup elements 
    main_container = tk.Frame(app.signup_frame, bg="#f0f8ff")
    main_container.pack(expand=False, pady=(50, 0))  # Adjusted padding to move everything up

    # Title "Signup" with controlled padding below
    tk.Label(main_container, text="Signup", font=("Arial", 20), bg="#f0f8ff").pack(pady=(0, 5))  # Minimized bottom padding

    # Container for the form fields
    signup_container = tk.Frame(main_container, bg="#f0f8ff")
    signup_container.pack()  # Center within the main container

    # Username field
    tk.Label(signup_container, text="Username", bg="#f0f8ff").pack(pady=(5, 2))  # Minimized padding for tight grouping
    app.signup_username_entry = tk.Entry(signup_container)
    app.signup_username_entry.pack(pady=(2, 5))

    # Email field
    tk.Label(signup_container, text="Email", bg="#f0f8ff").pack(pady=(5, 2))
    app.signup_email_entry = tk.Entry(signup_container)
    app.signup_email_entry.pack(pady=(2, 5))

    # Phone field
    tk.Label(signup_container, text="Phone", bg="#f0f8ff").pack(pady=(5, 2))
    app.signup_phone_entry = tk.Entry(signup_container)
    app.signup_phone_entry.pack(pady=(2, 5))

    # Password field
    tk.Label(signup_container, text="Password", bg="#f0f8ff").pack(pady=(5, 2))
    app.signup_password_entry = tk.Entry(signup_container, show="*")
    app.signup_password_entry.pack(pady=(2, 10))

    # Signup and back button
    tk.Button(signup_container, text="Signup", command=lambda: signup(app.signup_username_entry.get(), app.signup_email_entry.get(), app.signup_phone_entry.get(), app.signup_password_entry.get(), app)).pack(pady=(10, 2))
    tk.Button(signup_container, text="Back", command=lambda: show_frame(app,app.login_frame)).pack(pady=(2, 5))
            

        

        
# Custom encoding function using last digit of phone number as the shift value
def encode(password, shift):
    encoded_password = ""
    for char in password:
        # Shift each character by the shift value
        encoded_password += chr(ord(char) + shift)
    return encoded_password    
    
    
# Validate email format
def is_valid_email(email):
    return all((iter1 in email) for iter1 in '@.')


# Validate phone number format
def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10



# Validate password
def is_valid_password(password:str):
    # Condition 1: Minimum 7 characters
    if len(password) <= 7:
        messagebox.showerror("Invalid Password", "Password must be at least 7 characters long.")
        return False

    # Condition 2: At least one uppercase letter
    if not any(char.isupper() for char in password):
        messagebox.showerror("Invalid Password", "Password must contain at least one uppercase letter.")
        return False

    # Condition 3: At least one lowercase letter
    if not any(char.islower() for char in password):
        messagebox.showerror("Invalid Password", "Password must contain at least one lowercase letter.")
        return False

    # Condition 4: At least one special character
    special_characters = string.punctuation  # Special characters set from string module
    if not any(char in special_characters for char in password):
        messagebox.showerror("Invalid Password", "Password must contain at least one special character.")
        return False

    return True


# Function to handle Signup details
def signup(username, email, phone, password, app):
    if not is_valid_email(email):
        messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        return

    if not is_valid_phone(phone):
        messagebox.showerror("Invalid Phone Number", "Phone number must be exactly 10 digits.")
        return
    
    if not is_valid_password(password):
        return

    connection = mysql_authenticate(uname, pword)
    
    if connection:
        cursor = connection.cursor()
        
        try:
            cursor.execute("USE bus_reservation")
            
            # Encode the password using the phone number's last digit as the shift value
            last_digit = int(phone[-1])  # Use the last digit of the phone number for shifting
            encoded_password = encode(password, last_digit)
            
            # Check if username already exists
            cursor.execute("SELECT * FROM users_auth WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Username Taken", "This username is already taken. Please choose a different one.")
                return
            
            # Insert the user with encoded password
            cursor.execute("INSERT INTO users_auth (username, email, phone, password) VALUES (%s, %s, %s, %s)",
                           (username, email, phone, encoded_password))
            connection.commit()
            
            messagebox.showinfo("Signup Success", "You have successfully signed up.")
            print('User Signup Sucessful')
            show_frame(app,app.login_frame)
            
        except mysql.connector.Error as e:
            messagebox.showerror("Signup Error", f"Error during signup: {e}")
            
        finally:
            connection.close()                 
        


# Create admin frame to add bus details 
def create_admin_frame(app):

    # Title "Admin - Add Bus Details" centered at the top of the frame
    title_label = tk.Label(app.admin_frame, text="Admin - Add Bus Details", font=("Arial", 20), bg="#f0f8ff")
    title_label.pack(pady=(20, 10))  # 20px padding at the top, 10px at the bottom

    # Container for bus details input fields
    details_container = tk.Frame(app.admin_frame, bg="#f0f8ff")
    details_container.pack(pady=(0, 10))  # 10px padding below

    #Bus name filed
    tk.Label(details_container, text="Bus Name", bg="#f0f8ff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    app.bus_name_entry = tk.Entry(details_container)
    app.bus_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    #sorce field
    tk.Label(details_container, text="Source", bg="#f0f8ff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    app.source_entry = tk.Entry(details_container)
    app.source_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    #destination field
    tk.Label(details_container, text="Destination", bg="#f0f8ff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    app.destination_entry = tk.Entry(details_container)
    app.destination_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    #depature time filed 
    tk.Label(details_container, text="Departure Time", bg="#f0f8ff").grid(row=3, column=0, padx=5, pady=5, sticky="e")

    # Create and assign Comboboxes for departure time in HH:MM:SS format
    #Hour combobox
    app.departure_hour_combobox = ttk.Combobox(details_container, values=[f"{i:02d}" for i in range(24)], state="readonly")
    #readonly means  get only from combobox not by typing
    app.departure_hour_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    app.departure_hour_combobox.set('00')

    #minute combobox
    app.departure_minute_combobox = ttk.Combobox(details_container, values=[f"{i:02d}" for i in range(60)], state="readonly")
    app.departure_minute_combobox.grid(row=3, column=2, padx=5, pady=5, sticky="w")
    app.departure_minute_combobox.set('00')

    #seconds combobox
    app.departure_second_combobox = ttk.Combobox(details_container, values=[f"{i:02d}" for i in range(60)], state="readonly")
    app.departure_second_combobox.grid(row=3, column=3, padx=5, pady=5, sticky="w")
    app.departure_second_combobox.set('00')

    #arrivaltime filed
    tk.Label(details_container, text="Arrival Time", bg="#f0f8ff").grid(row=4, column=0, padx=5, pady=5, sticky="e")

    # Create and assign Comboboxes for arrival time in HH:MM:SS format
    #hour combobox
    app.arrival_hour_combobox = ttk.Combobox(details_container, values=[f"{i:02d}" for i in range(24)], state="readonly")
    app.arrival_hour_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    app.arrival_hour_combobox.set('00')

    #minute combobox
    app.arrival_minute_combobox = ttk.Combobox(details_container, values=[f"{i:02d}" for i in range(60)], state="readonly")
    app.arrival_minute_combobox.grid(row=4, column=2, padx=5, pady=5, sticky="w")
    app.arrival_minute_combobox.set('00')

    app.arrival_second_combobox = ttk.Combobox(details_container, values=[f"{i:02d}" for i in range(60)], state="readonly")
    app.arrival_second_combobox.grid(row=4, column=3, padx=5, pady=5, sticky="w")
    app.arrival_second_combobox.set('00')

    #seconds combobox
    tk.Label(details_container, text="Fare", bg="#f0f8ff").grid(row=5, column=0, padx=5, pady=5, sticky="e")
    app.fare_entry = tk.Entry(details_container)
    app.fare_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    #avaliable seats field
    tk.Label(details_container, text="Available Seats", bg="#f0f8ff").grid(row=6, column=0, padx=5, pady=5, sticky="e")
    app.seats_entry = tk.Entry(details_container)
    app.seats_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

    #bustype field
    tk.Label(details_container, text="Bus Type", bg="#f0f8ff").grid(row=7, column=0, padx=5, pady=5, sticky="e")
    app.bus_type_combobox = ttk.Combobox(details_container, values=["Sleeper", "Semi-Sleeper", "Sitting"], state="readonly")
    app.bus_type_combobox.grid(row=7, column=1, padx=5, pady=5, sticky="w")

    # Button to add bus details
    tk.Button(app.admin_frame, text="Add Bus", command=lambda: add_bus_details(app), bg="#add8e6", activebackground="#87ceeb").pack(pady=(10, 5))

    # Container for the login and exit fields
    button_container = tk.Frame(app.admin_frame, bg="#f0f8ff")
    button_container.pack(pady=(20, 10))  # 20px padding above, 10px below

    #Lginn and Exit button
    tk.Button(button_container, text="Login", command=lambda: show_frame(app,app.login_frame)).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(button_container, text="Exit",command=lambda: (app.quit(), app.destroy())).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(button_container, text="View Bookings",command=lambda: (view_bookings(app))).pack(side=tk.LEFT, padx=5, pady=5)         
   



#to view booking details of the customer
def view_bookings(app):
    # Set up the main frame for the view bookings page
    app.view_bookings_frame = tk.Frame(app, bg="#f0f8ff")
    app.view_bookings_frame.grid(row=0, column=0, sticky="nsew")

    # Back button at the top
    tk.Button(app.view_bookings_frame, text="Back", command=lambda: (show_frame(app,app.admin_frame))).pack(anchor="nw", pady=10, padx=10)

    # Title
    tk.Label(app.view_bookings_frame, text="All Bookings", font=("Arial", 16), bg="#f0f8ff").pack(pady=10)

    # Treeview for displaying booking data
    columns = ("Booking ID", "Username", "Bus Name", "Source", "Destination", "Booking Date", "Passenger Name", "Age", "Gender")
    bookings_tree = ttk.Treeview(app.view_bookings_frame, columns=columns, show="headings")
    for col in columns:
        bookings_tree.heading(col, text=col)
        bookings_tree.column(col, anchor="center", width=120)
    bookings_tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Scroll functionality for Treeview
    scrollbar = ttk.Scrollbar(app.view_bookings_frame, orient="vertical", command=bookings_tree.yview)
    bookings_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Frame for Previous and Next buttons
    nav_frame = tk.Frame(app.view_bookings_frame, bg="#f0f8ff")
    nav_frame.pack(pady=(10, 90))  

    # Previous and Next button commands
    def go_to_previous_page():
        global current_page
        if current_page > 0:
            current_page -= 1
            load_page(current_page)

    def go_to_next_page():
        global current_page
        current_page += 1
        load_page(current_page)

    # Previous and Next buttons
    previous_button = tk.Button(nav_frame, text="Previous", command=go_to_previous_page)
    next_button = tk.Button(nav_frame, text="Next", command=go_to_next_page)
    previous_button.pack(side="left", padx=5)
    next_button.pack(side="left", padx=5)

    # Load bookings with pagination
    def load_page(page_number):
        # Clear existing entries in the Treeview
        bookings_tree.delete(*bookings_tree.get_children())

        # Calculate the offset for the SQL query
        offset = page_number * app.bookings_per_page

        # Connect to the database and retrieve booking data for the current page
        mysql_connection = mysql_authenticate(uname, pword)  # Adjust to your database connection function
        cursor = mysql_connection.cursor()
        cursor.execute("USE bus_reservation")

        # Query to fetch booking, bus, and passenger data
        cursor.execute("""
            SELECT b.booking_id, u.username, bs.bus_name, bs.source, bs.destination, b.booking_date, 
                   p.name, p.age, p.gender
            FROM bookings b
            JOIN users_auth u ON b.user_id = u.user_id
            JOIN buses bs ON b.bus_id = bs.bus_id
            JOIN passenger_details p ON b.booking_id = p.booking_id
            ORDER BY b.booking_id ASC
            LIMIT %s OFFSET %s
        """, (app.bookings_per_page, offset))
        
        all_bookings = cursor.fetchall()

        # Populate the Treeview with booking data and passenger details for the current page
        for booking in all_bookings:
            bookings_tree.insert("", tk.END, values=booking)

        # Check if there are more records for the next page
        cursor.execute("SELECT COUNT(*) FROM passenger_details")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records // app.bookings_per_page)

        # Enable or disable the Previous button
        previous_button.config(state="normal" if  current_page > 0 else "disabled")

        # Enable or disable the Next button
        next_button.config(state="normal" if  current_page < total_pages else "disabled")

        mysql_connection.close()

    # Load the first page initially
    load_page( current_page)




#Creae bus detail frame to add bus detail in buses table
def add_bus_details(app):
    # Retrieve and format time inputs from comboboxes
    departure_time = f"{app.departure_hour_combobox.get()}:{app.departure_minute_combobox.get()}:{app.departure_second_combobox.get()}"
    arrival_time = f"{app.arrival_hour_combobox.get()}:{app.arrival_minute_combobox.get()}:{app.arrival_second_combobox.get()}"

    # Retrieve other bus details
    bus_name = app.bus_name_entry.get().strip().capitalize()  # Stripping to remove extra spaces
    source = app.source_entry.get().strip().capitalize()
    destination = app.destination_entry.get().strip().capitalize()
    fare = app.fare_entry.get().strip()
    available_seats = app.seats_entry.get().strip()
    bus_type = app.bus_type_combobox.get().strip()

    # Check if any field is empty
    if not bus_name:
        messagebox.showerror("Input Error", "Bus Name is empty, please enter the Bus Name.")
        return
    if not source:
        messagebox.showerror("Input Error", "Source is empty, please enter the Source.")
        return
    if not destination:
        messagebox.showerror("Input Error", "Destination is empty, please enter the Destination.")
        return
    if not fare:
        messagebox.showerror("Input Error", "Fare is empty, please enter the Fare.")
        return
    if not available_seats:
        messagebox.showerror("Input Error", "Available Seats is empty, please enter the Available Seats.")
        return
    if not bus_type:
        messagebox.showerror("Input Error", "Bus Type is empty, please select the Bus Type.")
        return
    if app.departure_hour_combobox.get() == '' or app.departure_minute_combobox.get() == '' or app.departure_second_combobox.get() == '':
        messagebox.showerror("Input Error", "Departure Time is incomplete, please enter the full Departure Time.")
        return
    if app.arrival_hour_combobox.get() == '' or app.arrival_minute_combobox.get() == '' or app.arrival_second_combobox.get() == '':
        messagebox.showerror("Input Error", "Arrival Time is incomplete, please enter the full Arrival Time.")
        return

    # Validate time format in HH:MM:SS format
    try:
        datetime.datetime.strptime(departure_time, '%H:%M:%S')
        datetime.datetime.strptime(arrival_time, '%H:%M:%S')

    except ValueError:
        messagebox.showerror("Input Error", "Time format should be hh:mm:ss")
        return

    # Create the SQL query to insert data into the table
    query = """
        INSERT INTO buses (bus_name, source, destination, departure_time, arrival_time, fare, available_seats, bus_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the query
    try:
        connection = mysql_authenticate(uname, pword)  # Ensure this method is defined

        if connection:
            cursor = connection.cursor()
            cursor.execute("USE bus_reservation")
            cursor.execute(query, (bus_name, source, destination, departure_time, arrival_time, fare, available_seats, bus_type))
            connection.commit()
            messagebox.showinfo("Success", "Bus added successfully!")

            # Clear the input fields after adding the bus
            app.bus_name_entry.delete(0, 'end')
            app.source_entry.delete(0, 'end')
            app.destination_entry.delete(0, 'end')
            app.departure_hour_combobox.set('00')
            app.departure_minute_combobox.set('00')
            app.departure_second_combobox.set('00')
            app.arrival_hour_combobox.set('00')
            app.arrival_minute_combobox.set('00')
            app.arrival_second_combobox.set('00')
            app.fare_entry.delete(0, 'end')
            app.seats_entry.delete(0, 'end')
            app.bus_type_combobox.set('')

    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Failed to add bus: {e}")

    finally:
        if connection:
            connection.close()





# Create the bus selection frame
def create_bus_selection_frame(app):
    # Container for all bus selection elements to ensure proper alignment and spacing
    main_container = tk.Frame(app.bus_selection_frame, bg="#f0f8ff")
    main_container.pack(expand=False, pady=(50, 0))

    # Title "Select Bus"
    tk.Label(main_container, text="Select Bus", font=("Arial", 16), bg="#f0f8ff").pack(pady=(0, 5))

    # Container for the bus selection fields
    bus_container = tk.Frame(main_container, bg="#f0f8ff")
    bus_container.pack()

    # From and To fields (Initially empty)
    tk.Label(bus_container, text="From", bg="#f0f8ff").pack(pady=(5, 2))
    app.from_combobox = ttk.Combobox(bus_container, state="readonly")
    app.from_combobox.pack(pady=(2, 5))

    tk.Label(bus_container, text="To", bg="#f0f8ff").pack(pady=(5, 2))
    app.to_combobox = ttk.Combobox(bus_container, state="readonly")
    app.to_combobox.pack(pady=(2, 5))

    # Travel Date field
    tk.Label(bus_container, text="Travel Date", bg="#f0f8ff").pack(pady=(5, 2))
    app.date_entry = DateEntry(bus_container, date_pattern="yyyy-mm-dd", mindate=datetime.datetime.now().date())
    app.date_entry.pack(pady=(2, 5))

    # Search Buses button
    tk.Button(bus_container, text="Search Buses", command=lambda: validate_locations(app)).pack(pady=(10, 2))

    # Treeview for displaying buses
    columns = ("bus_name", "departure", "arrival", "fare", "seats_available", "bus_type")
    app.bus_tree = ttk.Treeview(bus_container, columns=columns, show="headings")
    for col in columns:
        app.bus_tree.heading(col, text=col.capitalize())
    app.bus_tree.pack(pady=(5, 10))

    # Select Bus and Back buttons
    tk.Button(bus_container, text="Select Bus", command=lambda: select_bus(app)).pack(pady=(10, 2))
    tk.Button(bus_container, text="Back", command=lambda: show_frame(app, app.login_frame)).pack(pady=(2, 5))

    
    
    
# Function to check source and destination from database
def populate_cities(app):
    # This function will populate cities only after user login
    mysql_connection = mysql_authenticate(uname, pword)  # Assuming uname and pword hold user credentials
    if mysql_connection:
        cursor = mysql_connection.cursor()
        cursor.execute("USE bus_reservation")

        # Fetch unique cities from both source and destination columns
        cursor.execute("SELECT DISTINCT source FROM buses UNION SELECT DISTINCT destination FROM buses")
        cities = list(set(row[0] for row in cursor.fetchall()))  # Use set to ensure uniqueness
        cities.sort()  # Optional: Sort cities alphabetically

        app.from_combobox['values'] = cities
        app.to_combobox['values'] = cities

        mysql_connection.close()
    else:
        messagebox.showerror("Database Error", "Could not connect to the database.")

    
    
# Function to validate "From" and "To" locations
def validate_locations(app):
    from_location = app.from_combobox.get()
    to_location = app.to_combobox.get()

    if from_location == to_location:
        messagebox.showerror("Invalid Selection", "'From' and 'To' locations cannot be the same!")

    else:
        # Here you would implement the actual function to open bus selection
        open_bus_selection(app)  # Proceed to search buses
    

    
    
    
    
 # Bus selection window after login
def open_bus_selection(app): 
    
    #details from create_bus_selection_frame
    source = app.from_combobox.get()
    destination = app.to_combobox.get()
    travel_date = app.date_entry.get()

    # Ensure travel date is in the correct format
    try:
        travel_date = datetime.datetime.strptime(travel_date, "%Y-%m-%d").date()
        
    except ValueError:
        messagebox.showerror("Invalid Date", "Please select a valid date.")
        return

    connection = mysql_authenticate(uname, pword)
    
    if connection:
        cursor = connection.cursor()
        cursor.execute("USE bus_reservation")
        query = "SELECT * FROM buses WHERE source = %s AND destination = %s"
        cursor.execute(query, (source, destination))
        buses = cursor.fetchall() #fetchall() returns the data as a list of tuples. , it get from buses

        if buses:
            populate_buses(app, buses, travel_date)
            
        else:
            messagebox.showinfo("No Buses", "No buses found for the selected route.")
        connection.close()
        
        
# Populate bus selection to clearing any previous entries
def populate_buses(app, buses, travel_date):
    for row in app.bus_tree.get_children():
        app.bus_tree.delete(row)

    for bus in buses:
        app.bus_tree.insert("", "end", values=(bus[1], bus[4], bus[5], bus[6], bus[7], bus[8]))

    app.selected_date = travel_date
   



# Function to select a bus and check seat availability
def select_bus(app):
    selected_item = app.bus_tree.focus()

    if selected_item:  # If a bus is selected
        bus_details = app.bus_tree.item(selected_item, "values")  # Get bus details from the selected row
        seats_available = int(bus_details[4])  # Assuming "seats_available" is in the 5th column (index 4)

        if seats_available == 0:
            messagebox.showerror("No Seats Available", "Seats are full. Please select another bus.")

        else:
            app.preview_bus = bus_details  # Save bus details for later use
            show_frame(app,app.passenger_details_frame)  # Proceed if seats are available

    else:
        messagebox.showerror("Selection Error", "Please select a bus.")




# Create passenger details frame
def create_passenger_details_frame(app):

    # Container for all passenger details elements 
    main_container = tk.Frame(app.passenger_details_frame, bg="#f0f8ff")
    main_container.pack(expand=False, pady=(50, 0))  # Adjusted padding to move everything up

    # Title "Passenger Details" with controlled padding below
    tk.Label(main_container, text="Passenger Details", font=("Arial", 20), bg="#f0f8ff").pack(pady=(0, 5))  # Minimized bottom padding

    # Container for the passenger details fields
    passenger_container = tk.Frame(main_container, bg="#f0f8ff")
    passenger_container.pack()  # Center within the main container

    # Number of Passengers field
    tk.Label(passenger_container, text="Number of Passengers", bg="#f0f8ff").pack(pady=(5, 2))  # Minimized padding for tight grouping
    app.passenger_count_entry = tk.Entry(passenger_container)
    app.passenger_count_entry.pack(pady=(2, 5))

    # Add Passengers button
    tk.Button(passenger_container, text="Add Passengers", command=lambda: add_passenger_details(app)).pack(pady=(10, 2))

    # Passenger frame for displaying added passengers
    app.passenger_frame = tk.Frame(passenger_container, bg="#f0f8ff")
    app.passenger_frame.pack(pady=(20, 10))

    # Preview Reservation and Back buttons
    tk.Button(passenger_container, text="Preview Reservation", command=lambda: show_reservation_preview(app)).pack(pady=(10, 2))
    tk.Button(passenger_container, text="Back", command=lambda: show_frame(app,app.bus_selection_frame)).pack(pady=(2, 5))


# Add passenger details dynamically based on the number of passengers
def add_passenger_details(app):
    app.passenger_details = []  # Clear any existing details

    for widget in app.passenger_frame.winfo_children():
        widget.destroy()  # Clear previous input fields

    try:
        count = int(app.passenger_count_entry.get())

        if count < 1:
            raise ValueError("Invalid number of passengers")

        elif count > 5:
            raise ValueError("Maximum 5 passengers only")

        app.passenger_entries = []  # Store entry fields for later retrieval

        # Age validation: Allow only two-digit integers, including empty string for backspace
        def validate_age(char):
            return char.isdigit() and len(char) <= 2 or char==""

        # Register the validation command
        vcmd = (app.passenger_details_frame.register(validate_age), '%P')

        # Loop to dynamically create entry fields for each passenger
        for i in range(count):
            tk.Label(app.passenger_frame, text=f"Passenger {i+1}", bg="#f0f8ff").grid(row=i*3, column=0, columnspan=2, pady=5)

            tk.Label(app.passenger_frame, text="Name", bg="#f0f8ff").grid(row=i*3+1, column=0, padx=5, pady=5, sticky="e")
            name_entry = tk.Entry(app.passenger_frame)
            name_entry.grid(row=i*3+1, column=1, padx=5, pady=5, sticky="w")

            tk.Label(app.passenger_frame, text="Age", bg="#f0f8ff").grid(row=i*3+1, column=2, padx=5, pady=5, sticky="e")
            age_entry = tk.Entry(app.passenger_frame, validate='key', validatecommand=vcmd)  # Apply validation here
            age_entry.grid(row=i*3+1, column=3, padx=5, pady=5, sticky="w")

            tk.Label(app.passenger_frame, text="Gender", bg="#f0f8ff").grid(row=i*3+1, column=4, padx=5, pady=5, sticky="e")
            gender_combobox = ttk.Combobox(app.passenger_frame, values=["Male", "Female", "Others"], state="readonly")
            gender_combobox.grid(row=i*3+1, column=5, padx=5, pady=5, sticky="w")

            # Append fields to a list for later access
            app.passenger_entries.append({
                'name_entry': name_entry,
                'age_entry': age_entry,
                'gender_combobox': gender_combobox
            })

        # Button to finalize passenger details and move to preview
        submit_button = tk.Button(app.passenger_frame, text="Submit Passenger Details", command=lambda: save_passenger_details(app), bg="#add8e6", activebackground="#87ceeb")
        submit_button.grid(row=count*3, column=0, columnspan=6, pady=10)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number of passengers. Maximum is 5")


# Save passenger details from dynamically created input fields
def save_passenger_details(app):

    app.passenger_details = []  # Clear previous details

    for passenger in app.passenger_entries:
        name = passenger['name_entry'].get()
        age = passenger['age_entry'].get()
        gender = passenger['gender_combobox'].get()

        if not name or not age or not gender:
            messagebox.showerror("Input Error", "Please fill all fields for each passenger.")
            return

        if not age.isdigit() or int(age) < 0 or int(age) > 99:
            messagebox.showerror("Age Error", "Please enter a valid age (1-99).")
            return

        # Save passenger details
        app.passenger_details.append({
            'name': name,
            'age': int(age),
            'gender': gender
        })

    messagebox.showinfo("Passengers Added", "All passenger details added successfully.")


# Show reservation preview
def show_reservation_preview(app):
    selected_item = app.bus_tree.selection()
    
    if selected_item:
        bus = app.bus_tree.item(selected_item, "values")
        app.preview_bus = bus

        if len(app.passenger_details) == 0:
            messagebox.showerror("Passenger Info", "Please add passenger details.")
            return

        app.preview_text.config(state=tk.NORMAL)
        app.preview_text.delete('1.0', tk.END)
        total_fare = float(bus[3]) * len(app.passenger_details)
        app.preview_text.insert(tk.END, f"Bus Name: {bus[0]}\nDeparture: {bus[1]}\nArrival: {bus[2]}\nFare per Passenger: {bus[3]}\nTotal Fare: {total_fare}\nBus Type: {bus[5]}\n\n")
        
        for i, details in enumerate(app.passenger_details):
            app.preview_text.insert(tk.END, f"Passenger {i+1}: Name {details['name']}, Age {details['age']}, Gender {details['gender']}\n")
        app.preview_text.config(state=tk.DISABLED)

        show_frame(app,app.reservation_preview_frame)
        
    else:
        messagebox.showerror("No Selection", "Please select a bus.")
        



#Create reservation preview frame 
def create_reservation_preview_frame(app):

    # Container for all reservation preview elements 
    main_container = tk.Frame(app.reservation_preview_frame, bg="#f0f8ff")
    main_container.pack(expand=False, pady=(50, 0))  # Adjusted padding to move everything up

    # Title "Reservation Preview" with controlled padding below
    tk.Label(main_container, text="Reservation Preview", font=("Arial", 16), bg="#f0f8ff").pack(pady=(0, 10))  # Minimized top padding, increased bottom padding

    # Container for preview text and buttons
    preview_container = tk.Frame(main_container, bg="#f0f8ff")
    preview_container.pack(expand=True)  # Center within the main container

    # Preview Text Box
    app.preview_text = tk.Text(preview_container, state=tk.DISABLED, width=60, height=15)
    app.preview_text.pack(pady=(5, 10))  # Added padding to create space around the text box

    # Confirm and Print Ticket Button
    tk.Button(preview_container, text="Confirm & Print Ticket", command=lambda: confirm_reservation(app)).pack(pady=(10, 2))  # Adjusted padding

    # Back Button
    tk.Button(preview_container, text="Back", command=lambda: show_frame(app,app.passenger_details_frame)).pack(pady=(2, 10))  # Adjusted padding




#function to confirm the reservation 
def confirm_reservation(app):
    bus = app.preview_bus
    connection = mysql_authenticate(uname, pword)

    if connection:
        cursor = connection.cursor()
        cursor.execute("USE bus_reservation")

        try:
            # Get bus_id and available_seats
            bus_id_query = "SELECT bus_id, available_seats FROM buses WHERE bus_name = %s"
            cursor.execute(bus_id_query, (bus[0],))
            bus_info = cursor.fetchone()
            bus_id, available_seats = bus_info

            # Check seat availability
            if len(app.passenger_details) > available_seats:
                messagebox.showerror("Seat Unavailable", "Not enough seats available.")
                return

            # Update seats in the buses table
            new_seat_count = available_seats - len(app.passenger_details)
            update_seat_query = "UPDATE buses SET available_seats = %s WHERE bus_id = %s"
            cursor.execute(update_seat_query, (new_seat_count, bus_id))

            # Insert into bookings table
            booking_query = """
                INSERT INTO bookings (user_id, bus_id, seats_booked, booking_date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(booking_query, (app.current_user_id, bus_id, len(app.passenger_details), app.selected_date))
            connection.commit()
            booking_id = cursor.lastrowid  # Get the ID of the newly created booking

            # Insert each passenger's details into passenger_details table
            passenger_query = """
                INSERT INTO passenger_details (booking_id, name, age, gender)
                VALUES (%s, %s, %s, %s)
            """
            for passenger in app.passenger_details:
                # Normalize gender value to match ENUM values
                gender = passenger['gender'].capitalize()
                if gender not in ["Male", "Female", "Other"]:
                    gender = "Other"  # Default to 'Other' if input is not valid

                cursor.execute(passenger_query, (booking_id, passenger['name'], passenger['age'], gender))
            connection.commit()

            # Write ticket to file
            with open(f"Ticket_{bus[0]}_{booking_id}.txt", "w") as f:
                f.write(f"Bus Ticket Reservation\n")
                f.write(f"Bus Name: {bus[0]}\nDeparture: {bus[1]}\nArrival: {bus[2]}\n")
                f.write(f"Fare per Passenger: {bus[3]}\nTotal Fare: {float(bus[3]) * len(app.passenger_details)}\n")
                f.write(f"Travel Date: {app.selected_date}\nBus Type: {bus[5]}\n")
                
                for i, details in enumerate(app.passenger_details):
                    f.write(f"Passenger {i+1}: Name: {details['name']}, Age: {details['age']}, Gender: {details['gender']}\n")

            messagebox.showinfo("Ticket Confirmation", "Your ticket has been confirmed and saved.")
            show_post_confirmation_frame(app)

        except mysql.connector.Error as e:
            messagebox.showerror("Booking Error", f"Error during booking: {e}")

        finally:
            connection.close()



#post conformation frame
def show_post_confirmation_frame(app):

    # Clear the content of the reservation preview frame without destroying the frame itapp
    for widget in app.reservation_preview_frame.winfo_children():
        widget.pack_forget()

    # Container for all confirmation elements 
    main_container = tk.Frame(app.reservation_preview_frame, bg="#e0f7fa")
    main_container.pack(expand=False, pady=(50, 0))  # Adjusted padding to move everything up

    # Show the confirmation message with controlled padding below
    tk.Label(main_container, text="Ticket Confirmed!", font=("Arial", 16), bg="#e0f7fa").pack(pady=(0, 10))  # Minimized top padding, increased bottom padding

    # Frame for buttons to ensure better control over layout
    confirmation_container = tk.Frame(main_container, bg="#e0f7fa")
    confirmation_container.pack(expand=True)  # Center within the main container

    # Add Exit, New Booking, and Main Page buttons
    tk.Button(confirmation_container, text="Exit", command=lambda: (app.quit(), app.destroy())).pack(pady=(5, 5))  # Adjusted padding for button spacing
    tk.Button(confirmation_container, text="Main Menu", command=lambda: (reset_for_new_selection(app),show_frame(app,app.bus_selection_frame) )).pack(pady=(5, 5))  # Adjusted padding for button spacing
    tk.Button(confirmation_container, text="New Booking", command=lambda: (reset_for_new_selection(app),show_frame(app,app.login_frame))).pack(pady=(5, 10))  # Adjusted padding for button spacing


#reset window for new selection
def reset_for_new_selection(app):

    # Clear the previous passenger details and bus selection
    app.passenger_details = []
    app.preview_bus = None

    # Clear input fields in both frames
    clear_bus_selection_frame(app)
    clear_passenger_details_frame(app)

    # Clear content in the reservation preview frame
    for widget in app.reservation_preview_frame.winfo_children():
        widget.pack_forget()

    # Recreate the reservation preview frame
    create_reservation_preview_frame(app)



#clear bus sealction frame
def clear_bus_selection_frame(app):

    # Clear the comboboxes
    app.from_combobox.set('')
    app.to_combobox.set('')

    # Clear the date entry
    app.date_entry.set_date(datetime.datetime.now().date())

    # Clear the Treeview
    for item in app.bus_tree.get_children():
        app.bus_tree.delete(item)


#clear passenger details frame
def clear_passenger_details_frame(app):
    # Clear passenger count entry
    app.passenger_count_entry.delete(0, tk.END)

    # Clear dynamically added passenger details
    for widget in app.passenger_frame.winfo_children():
        widget.destroy()

    # Clear passenger details list
    app.passenger_entries = []
        
        
        
                        
# Function to clear all input fields
def clear_inputs(app):
    
    # Clear previous login inputs
    app.username_entry.delete(0, tk.END) #delete the entry strating  from 0 to end
    app.password_entry.delete(0, tk.END)

    # Clear previous signup inputs
    app.signup_username_entry.delete(0, tk.END)
    app.signup_email_entry.delete(0, tk.END)
    app.signup_phone_entry.delete(0, tk.END)
    app.signup_password_entry.delete(0, tk.END)            
    
    

# Switch frame utility function
def show_frame(app,frame):
    clear_inputs(app)
    frame.tkraise() # shows only the current frame and hides rest of the frame 

    
#Main function to initialize the app   
def initialize_app():
    app = tk.Tk()
    app.title("Bus Ticket Reservation System")
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")  # Full screen
    app.resizable(True, True)
    app.configure(bg="#f0f8ff")
    app.withdraw()  # Hide main window initially

    # Initialize state variables
    # Number of bookings per page
    app.bookings_per_page = 10
    
# Global variable to track the current page

    app.selected_date = None
    app.passenger_details = []
    app.preview_bus = None
    app.current_user_id = None
    global current_page
    current_page = 0
    # Open MySQL login window first
    mysql_login_window(app)


    # Create frames
    app.login_frame = tk.Frame(app, bg="#f0f8ff")
    app.signup_frame = tk.Frame(app, bg="#f0f8ff")
    app.bus_selection_frame = tk.Frame(app, bg="#f0f8ff")
    app.passenger_details_frame = tk.Frame(app, bg="#f0f8ff")
    app.reservation_preview_frame = tk.Frame(app, bg="#f0f8ff")
    app.admin_frame = tk.Frame(app, bg="#f0f8ff")
    app.view_bookings_frame = tk.Frame(app, bg="#f0f8ff")


    # Place frames in a grid layout
    for frame in (app.login_frame, app.signup_frame, app.bus_selection_frame,
                  app.passenger_details_frame, app.reservation_preview_frame, app.admin_frame,app.view_bookings_frame):
        frame.grid(row=0, column=0, sticky="nsew")

    # Configure grid row and column weights
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # Create individual frame contents
    create_login_frame(app)
    create_signup_frame(app)
    create_bus_selection_frame(app)
    create_passenger_details_frame(app)
    create_reservation_preview_frame(app)
    create_admin_frame(app) 



    return app
    
    
  
    
# Initialize and run the application
app = initialize_app()
app.mainloop()
