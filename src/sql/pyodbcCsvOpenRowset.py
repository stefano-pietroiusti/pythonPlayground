import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=YOUR_SQL_SERVER_HOSTNAME_OR_INSTANCE;"
    "Database=CRMDSL;"
    "Trusted_Connection=yes;"
)

csv_path = r"C:\Data\sample.csv"

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # OPENROWSET(BULK) query
    openrowset_sql = f"""
    INSERT INTO dbo.SampleData (Id, Name, Value)
    SELECT Id, Name, Value
    FROM OPENROWSET(
        BULK '{csv_path}',
        FORMAT='CSV',
        FIRSTROW=2
    ) AS rows;
    """

    cursor.execute(openrowset_sql)
    conn.commit()
    print("CSV uploaded via OPENROWSET ✅")

    cursor.execute("SELECT TOP 5 * FROM dbo.SampleData;")
    for row in cursor.fetchall():
        print(row)

    conn.close()

except Exception as e:
    print("Upload failed ❌:", e)
