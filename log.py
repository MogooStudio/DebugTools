import datetime


def info(msg):
    msg = "[{0}][info]: {1}".format(datetime.datetime.now(), msg)
    print(msg)


def error(msg):
    msg = "[{0}][error]: {1}".format(datetime.datetime.now(), msg)
    print(msg)
