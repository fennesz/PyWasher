# -*- coding: utf-8 -*-
import os
import smtplib
import beanstalkc
from datetime import datetime
from datetime import timedelta
import time
from selenium import webdriver
from pyvirtualdisplay import Display

class PyWasher(object):
    '''Reserves a washing machine at a desired time, and sends an e-mail with the time'''

    def __init__(self, user, email, emaildomain, url):
        self.__url = url
        self.__emails = [str(email)]
        self.__user = user
        self.__emaildomain = emaildomain
        self.__pymail = 'pywasher@' + emaildomain
        self.__password = os.environ['WASHPASS']
        print("Opening display.")
        self.__display = Display(visible=0, size=(800, 600))
        self.__display.start()
        try:
            print("Attempting to open browser...")
            self.__browser = webdriver.Firefox(timeout=120)
        except Exception:
            self.__display.stop()
            raise

    WEEKDAYS = {
        0 : 'Mandag',
        1 : 'Tirsdag',
        2 : 'Onsdag',
        3 : 'Torsdag',
        4 : 'Fredag',
        5 : 'Lørdag',
        6 : 'Søndag'
    };

    def __get_conn_string(self):
        '''
        Retrieved password from WASHPASS environment variable, build todays URL, sets it, and returns it.
        :return:
        '''
        login_str = self.__user + ":" + self.__password
        if "http://" in self.__url:
            self.__url = self.__url.replace('http://','',1)
        self.__url = "http://" + login_str + "@" + self.__url
        if not self.__url.endswith('/'):
            self.__url += '/'
        self.__url += "ReserverTid?lg=0&ly=9290&date=" # Could depend on location ...
        return self.__url


    def __get_time_interval(self, time):
        if int(time) < 9:
             return "7:00- 9:00"
        elif int(time) < 11:
             return "9:00-11:00"
        elif int(time) < 13:
             return "11:00-13:00"
        elif int(time) < 15:
             return "13:00-15:00"
        elif int(time) < 17:
             return "15:00-17:00"
        elif int(time) < 19:
             return "17:00-19:00"
        elif int(time) < 21:
             return "19:00-21:00"
        else:
            return "21:00-23:00"

    def find_next_avaliable(self, time_to_reserve, machinetype="M1+2", max_days=7):
        '''
        Find the next available machine at a given time and of type machinetype within max_days.
        :param time_to_reserve: The time we wish to reserve a machine. E.g 18 for 18:00
        :param machinetype: The size of the machine. M5+6 is the biggest.
        :return:
        '''
        self.__machinetype = machinetype
        print("Success! Finding next time available within " + str(max_days) + " days at: " + time_to_reserve + " Machine: " + machinetype)
        self.__today = time.strftime("%Y-%m-%d")
        self.__time_interval = self.__get_time_interval(time_to_reserve)
        url = self.__get_conn_string() #Should only be run once. Needs cleanup
        index = 0
        while max_days > 0:
            print("Going to page: /ReserverTid?lg=0&ly=9290&date=" + str(self.__today))
            self.__browser.get(url + str(self.__today))
            time.sleep(2)
            self.__links = self.__browser.find_elements_by_link_text(machinetype)
            for index in range(len(self.__links)):
                if self.__time_interval in self.__links[index].get_attribute("outerHTML"):
                    return True
                index += 1
            # Add one to current date if no link for machine is found ..
            date_1 = datetime.strptime(self.__today, "%Y-%m-%d")
            self.__end_date = date_1 + timedelta(days=1)
            self.__today = str(self.__end_date.date())
            max_days -= 1
        return False


    def reserve_time(self):
        index = 0
        while index < len(self.__links):
            if self.__time_interval in self.__links[index].get_attribute("outerHTML"):
                self.__links[index].click()
                break
            else:
                index += 1
        time.sleep(1)
        alert = self.__browser.switch_to.alert
        alert.accept()

    def add_receiver(self, email):
        self.__emails.append(str(email))

    def schedule_reminder(self):
        beanstalk = beanstalkc.Connection(host='localhost', port=11300)
        today = datetime.today()
        todayHour = int(self.__time_interval.split(':', 1)[0])
        end_date = self.__end_date
        end_date -= timedelta(seconds=end_date.second, minutes=end_date.minute, microseconds=end_date.microsecond, hours=end_date.hour)
        end_date += timedelta(hours=todayHour-1, minutes=50)
        c = end_date - today
        jid = beanstalk.put('pywasher$%s$%s$%s$%s' % (self.__machinetype, self.__emails,  self.__password, self.__pymail), delay=int(c.total_seconds()))

    def send_email(self):
        '''Configured to send from local SMTP server'''
        print("Successfully reserved time. Sending email!")
        smtpObj = smtplib.SMTP('localhost', 25)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login('pywasher', self.__password)
        mailString = "Subject: Vasketid reserveret til: " + \
                      self.WEEKDAYS[self.__end_date.weekday()] + " d. " + self.__today + \
                     " Kl. " +  self.__time_interval
        for m in self.__emails:
            smtpObj.sendmail(self.__pymail, m, mailString)
        smtpObj.quit()

    def __del__(self):
        self.__browser.close()
        self.__display.stop()
