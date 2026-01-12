## Python

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

## dbt

When running a dbt core job on a VM via Control-M, Control-M interprets the operating system (OS) exit code returned by the dbt command. dbt core defines specific exit codes for different outcomes, which Control-M uses to determine the job's final status (e.g., OK or NOTOK). 
dbt Core Return Codes
dbt core is designed to return specific exit codes to the operating system: 
0: The dbt invocation completed without error (success).
1: The dbt invocation completed with at least one handled error (e.g., a model syntax error, a failed test, bad permissions). The run completed, but some models or tests may have been skipped due to the error.
2: The dbt invocation completed with an unhandled error (e.g., a network interruption, ctrl-c event, or a system issue). 
A zero exit code (0) always implies success, while a non-zero exit code (1 or 2) always implies failure. 
Control-M Handling of Return Codes
Control-M captures the exit code (often internally referred to as OSCOMPSTAT) and uses it to determine the job's status. By default: 
An OS exit code of 0 results in a successful (OK) job status in Control-M.
Any non-zero OS exit code (like 1 or 2 from dbt) results in a failed (NOTOK) job status in Control-M. 
Example: Control-M OS Job Definition (via Automation API/JSON)
You can define an OS job in Control-M to run a dbt command on your application VM. The key is how Control-M is configured to handle the exit codes returned by the shell script or direct command execution. 
Here is an example using Control-M Automation API JSON to define a job that runs dbt build within a script on a Linux VM:

