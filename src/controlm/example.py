import sys

# Check the number of command-line arguments
if len(sys.argv) < 2:
    print("Error: Missing argument.")
    print("Usage: python your_script_name.py <status>")
    sys.exit(1) # Exit with a non-zero code for failure

status = sys.argv[1]

if status == "success":
    print("Job completed successfully.")
    sys.exit(0) # Exit with 0 for success (standard OS practice)
elif status == "warning":
    print("Job completed with warnings.")
    sys.exit(50) # Exit with 50 for a specific warning state
elif status == "failure":
    print("Job failed.")
    sys.exit(100) # Exit with 100 for a specific failure state
else:
    print(f"Unknown status: {status}")
    sys.exit(1) # Exit with 1 for general error
