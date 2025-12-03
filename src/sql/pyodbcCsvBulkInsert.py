import pyodbc

# Connection string using gMSA / Windows Authentication
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=YOUR_SQL_SERVER_HOSTNAME_OR_INSTANCE;"
    "Database=CRMDSL;"
    "Trusted_Connection=yes;"
)

# Path to CSV file accessible to SQL Server
# ⚠️ Important: This path must be visible to SQL Server service account, not just your Python process.
csv_path = r"C:\Data\sample.csv"

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # BULK INSERT command
    bulk_sql = f"""
    BULK INSERT dbo.SampleData
    FROM '{csv_path}'
    WITH (
        FIRSTROW = 2,              -- skip header row
        FIELDTERMINATOR = ',',     -- CSV delimiter
        ROWTERMINATOR = '\\n',     -- line break
        TABLOCK
    );
    """

    cursor.execute(bulk_sql)
    conn.commit()
    print("CSV uploaded via BULK INSERT ✅")

    # Verify
    cursor.execute("SELECT TOP 5 * FROM dbo.SampleData;")
    for row in cursor.fetchall():
        print(row)

    conn.close()

except Exception as e:
    print("Upload failed ❌:", e)
