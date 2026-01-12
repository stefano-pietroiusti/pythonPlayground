Control-M Configuration
Configure a Control-M OS Job to execute this script and handle the return codes. 
Job Type: Create an OS job.
Command: The command line to execute the script (assuming the script is saved as process_data.py on the VM).
Linux/Unix: python3 /path/to/process_data.py success
Windows: python C:\path\to\process_data.py success
On-Do Actions: Use the "On Statement" feature to define how Control-M should react to specific exit codes (return codes).
For success:
On return code = 0
Do Action: OK
For warning:
On return code = 50
Do Action: Set job status to OK (or perform a notification)
For failure:
On return code = 100
Do Action: NOTOK (This will cause the job to fail and potentially trigger alerts or conditional actions) 
By default, any non-zero exit code will cause the Control-M job to end in a NOTOK status unless you explicitly define an "On-Do" action for it. Using this mechanism allows the job scheduler to manage workflow dependencies and send appropriate notifications based on the script's outcome. 