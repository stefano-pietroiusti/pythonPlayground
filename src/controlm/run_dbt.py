import subprocess
import sys
import shutil
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run dbt with environment-specific profiles")
    parser.add_argument("--env", required=True, choices=["dev", "qa", "prod"],
                        help="Environment to run dbt against")
    parser.add_argument("--command", default="build",
                        help="dbt command to run (build, run, test, compile, etc.)")
    args = parser.parse_args()

    environment = args.env
    dbt_command = args.command

    project_dir = "armdsl"
    profiles_dir = os.path.join(project_dir, "profiles")

    source_profile = os.path.join(profiles_dir, f"profiles-{environment}.yml")
    active_profile = os.path.join(profiles_dir, "profiles.yml")

    print(f"Starting dbt job for environment: {environment}")
    print(f"Using dbt command: dbt {dbt_command}")

    # Validate profile exists
    if not os.path.exists(source_profile):
        print(f"ERROR: Profile file not found: {source_profile}")
        sys.exit(99)

    # Copy correct profile into place
    try:
        shutil.copyfile(source_profile, active_profile)
        print(f"Copied profile: {source_profile} → {active_profile}")
    except Exception as e:
        print(f"ERROR copying profile: {e}")
        sys.exit(98)

    # Build dbt command
    cmd = [
        "dbt",
        dbt_command,
        "--project-dir", project_dir,
        "--profiles-dir", profiles_dir,
        "--target", environment
    ]

    print(f"Running command: {' '.join(cmd)}")

    # Execute dbt
    process = subprocess.Popen(cmd)
    process.wait()
    exit_code = process.returncode

    # Handle exit code
    if exit_code != 0:
        print(f"dbt {dbt_command} FAILED with exit code {exit_code}")
        sys.exit(exit_code)
    else:
        print(f"dbt {dbt_command} completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
