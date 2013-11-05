import datetime


def console_log(message):
    now = datetime.datetime.now()
    print "%s - %s" % (now.strftime("%Y-%m-%d %H:%M:%S"), message)