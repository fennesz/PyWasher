import smtplib

import beanstalkc

def main():
    beanstalk = beanstalkc.Connection(host='localhost', port=11300)
    while True:
        job = beanstalk.reserve()
        res_info = str(job.body).split('$')
        if res_info[0] == 'pywasher':
            print("Executing email reminder.")
            machinetype = res_info[1]
            emails = res_info[2]
            password = res_info[3]
            pymail = res_info[4]
            smtpObj = smtplib.SMTP('localhost', 25)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login('pywasher', password)
            mailString = "Husk vasketid om 10 minutter. Maskiner: " + machinetype + "!"
            for m in emails:
                smtpObj.sendmail(pymail, m, mailString)
            smtpObj.quit()

        job.delete()


if __name__ == '__main__':
    main()