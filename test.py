import os
import subprocess
import json

def export_tasks_to_xml():
    desktop_path = r"C:\Users\goela13\OneDrive - moodys.com\Desktop\Ansh Goel Docs\export_tasks"

    # Create a directory to store individual task files
    output_dir = os.path.join(desktop_path, "task_files")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Fetch all scheduled tasks and their information
        command = """
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\\Microsoft\\Windows*' } |
Get-ScheduledTaskInfo | Select TaskName, TaskPath, LastRunTime, LastTaskResult | ConvertTo-Json
"""

#Get-ScheduledTask | Where-Object { $_.TaskPath -like '\\MyTasks\\*' } | Get-ScheduledTaskInfo | Select TaskName, TaskPath, LastRunTime, LastTaskResult | ConvertTo-Json

        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        tasks = json.loads(result.stdout)

        for task in tasks:
            task_name = task["TaskName"]
            task_path = task["TaskPath"]

            # Filter out system tasks
            if task_path.startswith("\\Microsoft\\Windows"):
                continue

            # Replace backslashes in task path for valid file name
            task_file_path = os.path.join(output_dir, f"{task_name}_{task_path.replace('\\', '_')}.xml")

            # Export the task script to a temporary file
            temp_file_path = os.path.join(output_dir, f"{task_name}_{task_path.replace('\\', '_')}_temp.xml")
            export_command = f"Export-ScheduledTask -TaskName \"{task_name}\" -TaskPath \"{task_path}\" | Out-File -FilePath \"{temp_file_path}\""
            subprocess.run(["powershell", "-Command", export_command], check=True)

            # Compare the content of the existing file and the temporary file
            if os.path.exists(task_file_path):
                with open(task_file_path, 'r') as existing_file:
                    existing_content = existing_file.read()
                with open(temp_file_path, 'r') as temp_file:
                    new_content = temp_file.read()

                if existing_content == new_content:
                    print(f"Task script for {task_name} is already up to date. Skipping.")
                    os.remove(temp_file_path)
                    continue
                else:
                    print(f"Task script for {task_name} has changed. Overwriting.")
                    os.remove(task_file_path)

            # Rename the temporary file to the final file
            os.rename(temp_file_path, task_file_path)
            print(f"Task script exported and saved to {task_file_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error fetching the task information. Error: {e}")

# Run the function
export_tasks_to_xml()
