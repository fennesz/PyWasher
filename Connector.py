'''
Created on Mar 22, 2016

@author: Martin Dalsgaard Clausen

This is the Connector class for the PyWasher project on GitHub. It's licensed under the GPLv3;
https://github.com/fennesz/PyWasher/blob/master/LICENSE

'''
import os
import requests

class Connector(object):
    '''
    Class for connecting to a Miele Logic reservation site.
    '''

    def __init__(self, url='', user = '', getpassfromenv=True):
        # TODO: Add additional ways to retrieve password.
        # Get pass from environment variable:
        if getpassfromenv:
            self.__pass = os.environ['MIELEPASS']

        self.__url = str(url)
        self.__user = str(user)

    def __str__(self):
        '''Print the info on a Connector instance'''
        return '\
        url:\t\t%s\n\
        user:\t\t%s' % (self.__url, self.__user)

    def __buildConnectionString(self):
        '''
        Input: example.com
        :return: http://example.com/
        '''
        if not "http://" in self.__url:
            self.__url = "http://" + self.__url
        if not self.__url.endswith('/'):
            self.__url += '/'
        return self.__url

    def __getReserveTimeString(self, reqInst):
        '''
        This method scrapes the loginpage for the "Reserv" button, and grabs the link to the reservation page.
        :param reqInst: The request instance of the requests object.
        :return: The URL string that needs to be appended. Ex: ReserveTime?id=32423 etc...
        '''
        resTimeUrlLoc = reqInst.text.encode('utf-8').strip().find('>Reserv') - 2
        urlStr = ''
        while reqInst.text.encode('utf-8').strip()[resTimeUrlLoc] != '/':
            urlStr = reqInst.text.encode('utf-8').strip()[resTimeUrlLoc] + urlStr
            resTimeUrlLoc -= 1
        return urlStr

    def getWebsiteConnection(self):
        '''
        Retrieves the main logon page, logs in, accesses the Reserve Time page, and returns the instance for that.
        :return:Request instance for "Reserve Time" page.
        '''
        connectionString = self.__buildConnectionString()
        r = requests.get(connectionString, auth=(self.__user, self.__pass))
        if r.status_code == requests.codes.ok:
            connectionString += self.__getReserveTimeString(r)
            print(connectionString)
            r = requests.get(connectionString, auth=(self.__user, self.__pass))
            return r
        else:
            r.raise_for_status()
        return r

def main():
    pass

if __name__ == '__main__':
    main()
