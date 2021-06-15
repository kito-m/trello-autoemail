import subprocess
import os

key = input("Please enter API key:  ")
token = input('Please enter API token:  ')

email_address = input('Please enter sender email address:  ')
email_password = input('Please enter sender email password:  ')


subprocess.run('python3 -m venv venv/', shell=True)
subprocess.run('source venv/bin/activate && pip install -r requirements.txt', shell=True, executable='/bin/bash')
subprocess.run(f"""echo "export PYTHONPATH='{os.getcwd()}/'" >> venv/bin/activate""", shell=True)

subprocess.run(f"""echo "export TRELLO_KEY='{key}'" >> venv/bin/activate""", shell=True)
subprocess.run(f"""echo "export TRELLO_TOKEN='{token}'" >> venv/bin/activate""", shell=True)

subprocess.run(f"""echo "export CBN_EMAIL_PASS='{email_password}'" >> venv/bin/activate""", shell=True)
subprocess.run(f"""echo "export CBN_EMAIL_USER='{email_address}'" >> venv/bin/activate""", shell=True)
