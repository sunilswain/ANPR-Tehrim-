import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Create Employees table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Employees (
        EmployeeID INTEGER PRIMARY KEY,
        EmployeeName TEXT NOT NULL
    )
''')

# Create Vehicle_Information table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vehicle_Information (
        VehicleID INTEGER PRIMARY KEY,
        Vehicle_Number TEXT NOT NULL,
        Model_Name TEXT NOT NULL,
        EmployeeID INTEGER,
        FOREIGN KEY (EmployeeID) REFERENCES Employees (EmployeeID)
    )
''')

# Insert dummy data into Employees
employees = [
    (1001, 'Alice Johnson'),
    (1002, 'Bob Smith'),
    (1003, 'Tehrim Siddiqa')
]
cursor.executemany('INSERT OR REPLACE INTO Employees VALUES (?, ?)', employees)

# Insert dummy data into Vehicle_Information
vehicles = [
    (1, 'OD33AL8404', 'YAMAHA RayZR 125', 1003),
    (2, 'OD33J6461', 'KTM RC 200', 1003),
    (3, 'OD02BV2170', 'MG Hector', 1001)
]
cursor.executemany('INSERT OR REPLACE INTO Vehicle_Information VALUES (?, ?, ?, ?)', vehicles)

# Commit changes
conn.commit()

# Run the query
cursor.execute('''
    SELECT e.EmployeeID, e.EmployeeName, v.Vehicle_Number, v.Model_Name
    FROM Employees e
    JOIN Vehicle_Information v ON e.EmployeeID = v.EmployeeID
''')

results = cursor.fetchall()
for row in results:
    print(row)

# Close connection
conn.close()
