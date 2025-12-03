import pyodbc

# Define connection string using Windows Authentication
# Note: No username/password needed — gMSA context provides Kerberos ticket
# psexec -i -u DOMAIN\MyGmsaAccount$ cmd.exe
# cd C:\path\to\your\script
# python connect_sql.py


# Register the scheduled task under gMSA
# $action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Scripts\connect_sql.py"
# $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
# Register-ScheduledTask -TaskName "TestGmsaPython" -Action $action -Trigger $trigger -User "DOMAIN\MyGmsaAccount$" -RunLevel Highest

# # Start the task immediately
# Start-ScheduledTask -TaskName "TestGmsaPython"

# New-Service -Name "PythonSqlTest" -BinaryPathName "python.exe C:\Scripts\connect_sql.py" -Credential "DOMAIN\MyGmsaAccount$"
# Start-Service -Name "PythonSqlTest"

# Register-ScheduledJob -Name "TestGmsaJob" -FilePath "C:\Scripts\connect_sql.py" -Credential (Get-Credential DOMAIN\MyGmsaAccount$)


conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=YOUR_SQL_SERVER_HOSTNAME_OR_INSTANCE;"
    "Database=YOUR_DATABASE_NAME;"
    "Trusted_Connection=yes;"
)

try:
    # Connect to SQL Server
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Run a simple query
    cursor.execute("SELECT TOP 5 name FROM sys.databases;")
    for row in cursor.fetchall():
        print(row)

    conn.close()
    print("Connection successful ✅")

except Exception as e:
    print("Connection failed ❌:", e)
