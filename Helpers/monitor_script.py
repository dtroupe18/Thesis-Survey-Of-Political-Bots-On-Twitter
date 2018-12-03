from DataCollection import constants
import psutil
import sys
import smtplib
import time


def start_monitoring(process_name):
    print(process_name)
    while True:
        running = False

        for process in psutil.process_iter():
            process_list = process.cmdline()
            if len(process_list) > 1 and process_list[1] == process_name:
                print('Process found: sleeping')
                running = True

        if not running:
            print('Process not found sending email notification!')
            send_notification_email(process_name)
            sys.exit('Exiting after email notification')

        else:
            time.sleep(30)


def send_notification_email(process_name):
    # Email myself when the script finishes so I can start on the next set of data
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(constants.email_address, constants.password)

    subject = process_name + ' stopped running!'
    text = process_name + ' crashed!'
    message = 'Subject: {}\n\n{}'.format(subject, text)
    server.sendmail(constants.email_address, constants.real_email, message)
    server.quit()

    return


length = len(sys.argv)
if length != 2:
    print('ERROR: Please provide the name of the process to monitor for!')
else:
    arg = sys.argv[1]
    start_monitoring(arg)


