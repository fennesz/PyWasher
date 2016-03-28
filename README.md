# PyWasher
Automating washing machine reservation for MieleLogic sites, so it can be done automatically on a Raspberry Pi.

As of March 28 2016, the following is implemented:
Currently, PyWasher connects to the site provided to the constructor, performs a login, browses through the current available washing machines, reserves the machine type and size provided by the argument, and finally sends an e-mail to you confirming the date of registration as well as the machine type.

Using pywasherscheduler it then schedules an e-mail to be sent as a reminder 10 minutes before the reserved time. E-mails can be sent to multiple recipients.

Because the MieleLogic website runs javascript, PyWasher depends on selenium, firefox webdriver, beanstalkd, beanstalkc, and pyvirtualdisplay to get everything up and running.
