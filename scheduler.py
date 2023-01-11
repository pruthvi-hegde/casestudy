"""
Setting up an automated job to run task everyday at 2:00 pm (Note : It does not take different timezones into account)
To run it as a background process : save this as python script. e.g, 'scheduler.py' and then run this script from command line
with a command : 'nohup python scheduler.py &' (without the quotes)
"""

import schedule
import time
import subprocess

def run_script():
    subprocess.call(['python', 'automated_task.py'])

schedule.every().day.at("14:00").do(run_script)

while True:
    schedule.run_pending()
    time.sleep(60)  # wait one minute