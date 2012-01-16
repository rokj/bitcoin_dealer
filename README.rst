Bitcoin dealer
==============

Bitcoin dealer is simple Django script for trading bitcoins currently only
on MtGox exchange. Now only API version 0 is supported, which will be deprecated on 1th
of March.

Script is most usefull for those who do not have time to watch price of bitcoin 
all the time and know how to write few "Hello worlds" with two if cases.

Installation
------------
* Register to MtGox - https://mtgox.com/
* Install Django - https://www.djangoproject.com/
* Add following variables in settings.py:
 - mtgox_username = 'your mtgox user'
 - mtgox_password = 'your mtgox pass'
 - mtgox_key = 'you get this in mtgox admin page'
 - mtgox_secret = 'you get this also in mtgox admin page'
 - check_interval = 7
 - bd_debug = True
 - "exchange" into INSTALLED_APPS
* Set DEBUG to True in settings.py and set TEMPLATE_DEBUG to DEBUG.
* Start trading script with in root bitcoin dealer folder like:
  python -u scripts/dealing.py
* Start webserver in root bicoin dealer folder like:
  python manage.py runserver 8000
* Goto http://127.0.0.1:8000/admin/ and place trades.

Troubleshooting
---------------
If paths for running script cannot be found and you get errors, set following
variables:
 export DJANGO_SETTINGS_MODULE=bitcoin_dealer.settings (bitcoin_dealer is the
name of the folder you have clonde this project)
 export PYTHONPATH=/your_path_to_one_path_less_than_bitcoin_dealer/
(if you have bitcoin_dealer in /programs/bitcoin_dealer/ then you should
export PYTHONPATH=/programs/

WARNING
-------
Watch out, settings.py should be accessible only by you, your account and your 
permissions.

You find it usefull or want new feature? 
----------------------------------------
You can donate a bitcoin or few on:
1MC1BSkwD45gAuQ8mvXtD1RZWhNtxGV1ho
