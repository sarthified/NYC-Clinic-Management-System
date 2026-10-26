import mysql.connector
import csv
import random

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)
cur = db.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS doc")
cur.execute("USE doc")

def setup():
    try:
        cur.execute("CREATE TABLE patients (id INT PRIMARY KEY, name VARCHAR(50), phone VARCHAR(15), age INT, password VARCHAR(50))")
    except:
        pass
    try:
        cur.execute("CREATE TABLE pharmacists (id INT PRIMARY KEY, name VARCHAR(50), password VARCHAR(50))")
    except:
        pass
    try:
        cur.execute("CREATE TABLE doctors (id INT PRIMARY KEY, name VARCHAR(50), specialization VARCHAR(50), fee INT)")
    except:
        pass
    try:
        cur.execute("CREATE TABLE doctor_slots (doctor_id INT PRIMARY KEY, total_slots INT)")
    except:
        pass
    try:
        cur.execute("CREATE TABLE doctor_slot_times (doctor_id INT, slot_time VARCHAR(20), booked TINYINT DEFAULT 0)")
    except:
        pass
    try:
        cur.execute("CREATE TABLE appointments (patient_id INT, doctor_id INT, slot_time VARCHAR(20), appointment_date VARCHAR(20))")
    except:
        pass
    try:
        cur.execute("CREATE TABLE bills (id BIGINT PRIMARY KEY, patient_id INT, doctor_id INT, docfee INT, medbill FLOAT DEFAULT 0, total FLOAT)")
    except:
        pass
    db.commit()
    try:
        f = open("medicines.csv", "a+", newline="")
        f.seek(0)
        first_line = f.readline()
        if len(first_line.strip()) == 0:
            writer = csv.writer(f)
            writer.writerow(["name", "price", "stock"])
        f.close()
    except:
        pass

def add_medicine():
    name = input("Medicine Name: ").strip()
    try:
        price = float(input("Price: ").strip())

        stock = int(input("Stock: ").strip())
    except:
        print("Invalid input")
        return
    try:
        f = open("medicines.csv", "a", newline="")
        writer = csv.writer(f)
        writer.writerow([name, price, stock])
        f.close()
        print("Medicine added successfully")
    except:
        print("Could not write to medicines file")

def view_medicines():
    try:
        f = open("medicines.csv", "r")
        f.readline()
        reader = csv.reader(f)
        meds = []
        for row in reader:
            meds.append(row)
        f.close()
        if len(meds) == 0:
            print("No medicines available")
            return
        print("\nAvailable Medicines:")
        for m in meds:
            print("Name:", m[0], "| Price:", m[1], "| Stock:", m[2])
    except:
        print("No medicine data file found")

def update_medicine():
    name = input("Enter medicine name to update: ").strip()
    try:
        f = open("medicines.csv", "r")
        f.readline()
        reader = csv.reader(f)
        meds = []
        for row in reader:
            meds.append(row)
        f.close()
    except:
        print("Medicine file not found")
        return
    found = False
    for m in meds:
        if m[0].lower() == name.lower():
            try:
                new_price = float(input("New Price: ").strip())
                new_stock = int(input("New Stock: ").strip())
            except:
                print("Invalid input")
                return
            m[1] = str(new_price)
            m[2] = str(new_stock)
            found = True
            break
    if found:
        try:
            f = open("medicines.csv", "w", newline="")
            writer = csv.writer(f)
            writer.writerow(["name", "price", "stock"])
            for m in meds:
                writer.writerow(m)
            f.close()
            print("Medicine updated")
        except:
            print("Could not update medicines file")
    else:
        print("Medicine not found")

def remove_medicine():
    name = input("Enter medicine name to remove: ").strip()
    try:
        f = open("medicines.csv", "r")
        f.readline()
        reader = csv.reader(f)
        meds = []
        for row in reader:
            if row[0].lower() != name.lower():
                meds.append(row)
        f.close()
    except:
        print("Medicine file not found")
        return
    try:
        f = open("medicines.csv", "w", newline="")
        writer = csv.writer(f)
        writer.writerow(["name", "price", "stock"])
        for m in meds:
            writer.writerow(m)
        f.close()
        print("Medicine removed if it existed")
    except:
        print("Could not update medicines file")

def patient_signup():
    try:
        pid = int(input("Enter Patient ID: ").strip())
    except:
        print("Invalid ID")
        return
    name = input("Enter Name: ").strip()
    phone = input("Enter Phone: ").strip()
    try:
        age = int(input("Enter Age: ").strip())
    except:
        print("Invalid age")
        return
    password = input("Enter Password: ").strip()
    try:
        cur.execute("INSERT INTO patients VALUES (%s,%s,%s,%s,%s)", (pid, name, phone, age, password))
        db.commit()
    except:
        print("Error: Patient ID may already exist or database error occurred")
        return
    print("Signup successful. Logged in as", name)
    patient_menu(pid, name)

def patient_login():
    try:
        pid = int(input("Enter ID: ").strip())
    except:
        print("Invalid ID")
        return
    password = input("Enter Password: ").strip()
    cur.execute("SELECT name FROM patients WHERE id=%s AND password=%s", (pid, password))
    user = cur.fetchone()
    if user:
        print("Welcome", user[0])
        patient_menu(pid, user[0])
    else:
        print("Invalid credentials")

def book_appointment(pid):
    cur.execute("SELECT id, name, specialization, fee FROM doctors")
    docs = cur.fetchall()
    if len(docs) == 0:
        print("No doctors available")
        return
    print("\nDoctors:")
    for d in docs:
        print("Doctor ID:", d[0], "| Name:", d[1], "| Spec:", d[2], "| Fee:", d[3])
    try:
        did = int(input("Enter doctor ID to book: ").strip())
    except:
        print("Invalid input")
        return
    cur.execute("SELECT slot_time, booked FROM doctor_slot_times WHERE doctor_id=%s", (did,))
    slots = cur.fetchall()
    if len(slots) == 0:
        print("No slots available for this doctor")
        return
    available = []
    for s in slots:
        if s[1] == 0:
            available.append(s[0])
    if len(available) == 0:
        print("No free slots left")
        return
    print("\nAvailable Slots:")
    for s in available:
        print(s)
    st = input("Enter slot time: ").strip()
    if st not in available:
        print("Invalid slot selected")
        return
    date = input("Enter appointment date (DD/MM/YYYY): ").strip()
    cur.execute("UPDATE doctor_slot_times SET booked=1 WHERE doctor_id=%s AND slot_time=%s", (did, st))
    cur.execute("INSERT INTO appointments VALUES (%s,%s,%s,%s)", (pid, did, st, date))
    cur.execute("SELECT fee FROM doctors WHERE id=%s", (did,))
    feeData = cur.fetchone()
    if feeData is None:
        print("Doctor not found")
        return
    fee = feeData[0]
    bid = random.randint(10000, 999999)
    cur.execute("INSERT INTO bills VALUES (%s,%s,%s,%s,%s,%s)", (bid, pid, did, fee, 0.0, fee))
    db.commit()
    print("\n===== APPOINTMENT CONFIRMED =====")
    print("Bill ID        :", bid)
    print("Doctor Fee     :", fee)
    print("Appointment on :", date, "at", st)
    print("Total Amount   :", fee)
    print("================================\n")

def view_appointments(pid):
    cur.execute("SELECT doctor_id, slot_time, appointment_date FROM appointments WHERE patient_id=%s", (pid,))
    apps = cur.fetchall()
    if len(apps) == 0:
        print("No previous appointments found")
    else:
        print("\nYour Appointments:")
        for a in apps:
            print("Doctor ID:", a[0], "| Slot:", a[1], "| Date:", a[2])

def view_bills(pid):
    cur.execute("SELECT id, doctor_id, docfee, medbill, total FROM bills WHERE patient_id=%s", (pid,))
    bills = cur.fetchall()
    if len(bills) == 0:
        print("No bills found")
    else:
        for b in bills:
            print("\n------------------------------")
            print("Bill ID       :", b[0])
            print("Doctor ID     :", b[1])
            print("Doctor Fee    :", b[2])
            print("Medicine Bill :", b[3])
            print("Total Amount  :", b[4])
            print("------------------------------")

def buy_medicines(pid):
    try:
        f = open("medicines.csv", "r")
        f.readline()
        reader = csv.reader(f)
        meds = []
        for row in reader:
            meds.append(row)
        f.close()
    except:
        print("No medicines data file found")
        return
    if len(meds) == 0:
        print("No medicines available")
        return
    print("\nAvailable Medicines:")
    for m in meds:
        print("Name:", m[0], "| Price:", m[1], "| Stock:", m[2])
    name = input("Enter medicine name to buy: ").strip()
    try:
        qty = int(input("Quantity: ").strip())
    except:
        print("Invalid quantity")
        return
    found = False
    bought_price = 0.0
    for m in meds:
        if m[0].lower() == name.lower():
            stock = int(m[2])
            price = float(m[1])
            if stock >= qty:
                m[2] = str(stock - qty)
                bought_price = price * qty
                found = True
            else:
                print("This medicine is not available in sufficient stock")
                return
            break
    if not found:
        print("Medicine not found")
        return
    try:
        f = open("medicines.csv", "w", newline="")
        writer = csv.writer(f)
        writer.writerow(["name", "price", "stock"])
        for m in meds:
            writer.writerow(m)
        f.close()
    except:
        print("Error updating medicines file")
        return
    cur.execute("SELECT id, medbill, docfee FROM bills WHERE patient_id=%s ORDER BY id DESC LIMIT 1", (pid,))
    bill = cur.fetchone()
    if bill is None:
        print("No bill found. Please book an appointment first")
        return
    bid = bill[0]
    old_medbill = float(bill[1])
    docfee = float(bill[2])
    medbill = old_medbill + bought_price
    total = medbill + docfee
    try:
        cur.execute("UPDATE bills SET medbill=%s, total=%s WHERE id=%s", (medbill, total, bid))
        db.commit()
        print("Medicine purchased successfully. Bill updated.")
        print("New Medicine Bill:", medbill, "| New Total:", total)
    except:
        print("Error updating bill")

def pharmacist_menu():
    while True:
        print("\nPharmacist Menu")
        print("1. Add Medicine")
        print("2. View Medicines")
        print("3. Update Medicine")
        print("4. Remove Medicine")
        print("5. Logout")
        ch = input("Enter choice: ").strip()
        if ch == '1':
            add_medicine()
        elif ch == '2':
            view_medicines()
        elif ch == '3':
            update_medicine()
        elif ch == '4':
            remove_medicine()
        elif ch == '5':
            break
        else:
            print("Invalid choice")

def pharmacist_signup():
    try:
        pid = int(input("Enter Pharmacist ID: ").strip())
    except:
        print("Invalid ID")
        return
    name = input("Enter Name: ").strip()
    password = input("Enter Password: ").strip()
    try:
        cur.execute("INSERT INTO pharmacists VALUES (%s,%s,%s)", (pid, name, password))
        db.commit()
    except:
        print("Error: Pharmacist ID may already exist or database error occurred")
        return
    print("Signup successful. Logged in as", name)
    pharmacist_menu()

def pharmacist_login():
    try:
        pid = int(input("Enter ID: ").strip())
    except:
        print("Invalid ID")
        return
    password = input("Enter Password: ").strip()
    cur.execute("SELECT name FROM pharmacists WHERE id=%s AND password=%s", (pid, password))
    user = cur.fetchone()
    if user:
        print("Welcome", user[0])
        pharmacist_menu()
    else:
        print("Invalid credentials")

def admin_menu():
    while True:
        print("\nAdmin Menu")
        print("1. Add Doctor")
        print("2. Remove Doctor")
        print("3. Set / Reset Slots for a Doctor")
        print("4. View All Bills")
        print("5. View All Appointments")
        print("6. Logout")
        ch = input("Enter choice: ").strip()
        if ch == '1':
            try:
                did = int(input("Doctor ID: ").strip())
            except:
                print("Invalid ID")
                continue
            name = input("Name: ").strip()
            spec = input("Specialization: ").strip()
            try:
                fee = int(input("Fee: ").strip())
                slots = int(input("Total Slots: ").strip())
            except:
                print("Invalid fee or slots")
                continue
            try:
                cur.execute("INSERT INTO doctors VALUES (%s,%s,%s,%s)", (did, name, spec, fee))
                cur.execute("INSERT INTO doctor_slots VALUES (%s,%s)", (did, slots))
                for i in range(slots):
                    st = input("Slot time: ").strip()
                    cur.execute("INSERT INTO doctor_slot_times VALUES (%s,%s,0)", (did, st))
                db.commit()
                print("Doctor added with slots")
            except:
                print("Error adding doctor")
        elif ch == '2':
            try:
                did = int(input("Enter doctor ID to remove: ").strip())
            except:
                print("Invalid ID")
                continue
            try:
                cur.execute("DELETE FROM doctors WHERE id=%s", (did,))
                cur.execute("DELETE FROM doctor_slots WHERE doctor_id=%s", (did,))
                cur.execute("DELETE FROM doctor_slot_times WHERE doctor_id=%s", (did,))
                cur.execute("DELETE FROM appointments WHERE doctor_id=%s", (did,))
                db.commit()
                print("Doctor removed")
            except:
                print("Error removing doctor")
        elif ch == '3':
            try:
                did = int(input("Enter doctor ID to set/reset slots: ").strip())
            except:
                print("Invalid ID")
                continue
            try:
                cur.execute("DELETE FROM doctor_slot_times WHERE doctor_id=%s", (did,))
                cur.execute("DELETE FROM doctor_slots WHERE doctor_id=%s", (did,))
                slots = int(input("Enter new total slots: ").strip())
                cur.execute("INSERT INTO doctor_slots VALUES (%s,%s)", (did, slots))
                for i in range(slots):
                    st = input("Slot time: ").strip()
                    cur.execute("INSERT INTO doctor_slot_times VALUES (%s,%s,0)", (did, st))
                db.commit()
                print("Slots set/reset for doctor", did)
            except:
                print("Error setting slots")
        elif ch == '4':
            cur.execute("SELECT * FROM bills")
            bills = cur.fetchall()
            if len(bills) == 0:
                print("No bills available")
            else:
                print("\nAll Bills:")
                for b in bills:
                    print(b)
        elif ch == '5':
            cur.execute("SELECT * FROM appointments")
            apps = cur.fetchall()
            if len(apps) == 0:
                print("No appointments found")
            else:
                print("\nAll Appointments:")
                for a in apps:
                    print(a)
        elif ch == '6':
            break
        else:
            print("Invalid choice")

def admin_login():
    username = input("Enter username: ").strip()
    pw = input("Enter password: ").strip()
    if username == "admin" and pw == "admin":
        admin_menu()
    else:
        print("Invalid admin credentials")

def patient_menu(pid, name):
    while True:
        print("\nPatient Menu")
        print("1. Book Appointment")
        print("2. Buy Medicines")
        print("3. View Appointments")
        print("4. View Bills")
        print("5. Logout")
        ch = input("Enter choice: ").strip()
        if ch == '1':
            book_appointment(pid)
        elif ch == '2':
            buy_medicines(pid)
        elif ch == '3':
            view_appointments(pid)
        elif ch == '4':
            view_bills(pid)
        elif ch == '5':
            break
        else:
            print("Invalid choice")

def main():
    print('=============Welcome To NYC clinic===========')
    setup()
    while True:
        print("\nMain Menu")
        print("1. Patient")
        print("2. Pharmacist")
        print("3. Admin")
        print("4. Exit")
        ch = input("Enter choice: ").strip()
        if ch == '1':
            print("\nPatient: 1. Signup  2. Login")
            c = input("Enter choice: ").strip()
            if c == '1':
                patient_signup()
            elif c == '2':
                patient_login()
            else:
                print("Invalid choice")
        elif ch == '2':
            print("\nPharmacist: 1. Signup  2. Login")
            c = input("Enter choice: ").strip()
            if c == '1':
                pharmacist_signup()
            elif c == '2':
                pharmacist_login()
            else:
                print("Invalid choice")
        elif ch == '3':
            admin_login()
        elif ch == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice")

main()
cur.close()
db.close()
