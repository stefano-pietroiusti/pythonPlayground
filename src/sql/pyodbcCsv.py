import pyodbc
import csv

# Define connection string using Windows Authentication (gMSA context)
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=YOUR_SQL_SERVER_HOSTNAME_OR_INSTANCE;"
    "Database=CRMDSL;"
    "Trusted_Connection=yes;"
)

try:
    # Connect to SQL Server
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    print("Connected to CRMDSL ✅")

    # Path to your sample CSV file
    csv_file = r"C:\path\to\sample.csv"

    # Example: assume table dbo.SampleData with columns [Id], [Name], [Value]
    insert_sql = "INSERT INTO dbo.SampleData (Id, Name, Value) VALUES (?, ?, ?)"

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        for row in reader:
            # Adjust indexes to match your CSV structure
            cursor.execute(insert_sql, row[0], row[1], row[2])

    conn.commit()
    print("CSV data uploaded successfully ✅")

    # Verify upload
    cursor.execute("SELECT TOP 5 * FROM dbo.SampleData;")
    for row in cursor.fetchall():
        print(row)

    conn.close()

except Exception as e:
    print("Upload failed ❌:", e)
