import os

from twisted.python import logfile, log


def logger():
    try:
        if "NEXTLINUX_LOGFILE" in os.environ:
            thefile = os.environ["NEXTLINUX_LOGFILE"]
        else:
            thefile = "nextlinux-general.log"
    except:
        thefile = "nextlinux-general.log"

    f = logfile.LogFile(thefile,
                        "/var/log/",
                        rotateLength=10000000,
                        maxRotatedFiles=10)
    log_observer = log.FileLogObserver(f)

    return log_observer.emit


# def logger():
#    return log.PythonLoggingObserver().emit
