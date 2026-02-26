#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#HTML logging library

"""
HTML logger library
"""
import logging
import time
from datetime import datetime
import os

def generate_report_name():
    import inspect #import has to be here otherwise datetime() function returns the time date of the import operation (always the same)
    ret_val=""
    if not os.path.exists("Reports"):
        os.makedirs("Reports")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dt_string = dt_string.replace("/","_")
    dt_string = dt_string.replace(":", "_")
    dt_string = dt_string.replace(" ", "_")
    ret_val = "Reports\\"+inspect.stack()[1][3]+"___"+dt_string+"_.html"
    #print("!!!DEBUG!!! ret_val = ",ret_val)
    return ret_val

#: HTML header
_START_OF_DOC_FMT = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>%(title)s</title>
<style type="text/css">
body, html {
background: #000000;
width: 1000px;
font-family: Arial;
font-size: 16px;
color: #C0C0C0;
}
h1 {
color : #FFFFFF;
border-bottom : 1px dotted #888888;
}
pre {
font-family : arial;
margin : 0;
}
.box {
border : 1px dotted #818286;
padding : 5px;
margin: 5px;
width: 950px;
background-color : #292929;
}
.err {
color: #EE1100;
font-weight: bold
}
.warn {
color: #FFCC00;
font-weight: bold
}
.info {
color: #C0C0C0;
}
.debug {
color: #00FF00;
}
</style>
</head>
<body>
<h1>%(title)s</h1>
<h3>%(version)s</h3>
<div class="box">
<table>
"""

_END_OF_DOC_FMT = """</table>
</div>
</body>
</html>
"""

_MSG_FMT = """
<tr>
<td width="100">%(time)s</td>
<td class="%(class)s"><pre>%(msg)s</pre></td>
<tr>
"""



class HTMLFileHandler(logging.FileHandler):
    """
    File handler specialised to write the start of doc as html and to close it
    properly.
    """

    def __init__(self, title, version, *args):
        super().__init__(*args)
        assert self.stream is not None
        # Write header
        self.stream.write(_START_OF_DOC_FMT % {"title": title,
                                               "version": version})

    def close(self):
        # finish document
        self.stream.write(_END_OF_DOC_FMT)
        super().close()


class HTMLFormatter(logging.Formatter):
    """
    Formats each record in html
    """
    CSS_CLASSES = {'WARNING': 'warn',
                   'INFO': 'info',
                   'DEBUG': 'debug',
                   'CRITICAL': 'err',
                   'ERROR': 'err'}

    def __init__(self):
        super().__init__()
        self._start_time = time.time()

    def format(self, record):
        try:
            class_name = self.CSS_CLASSES[record.levelname]
        except KeyError:
            class_name = "info"

        t = time.time() - self._start_time

        # handle '<' and '>' (typically when logging %r)
        msg = record.msg
        msg = msg.replace("<", "&#60")
        msg = msg.replace(">", "&#62")

        return _MSG_FMT % {"class": class_name, "time": "%.4f" % t,
                           "msg": msg}


class HTMLLogger(logging.Logger):
    """
    Log records to html using a custom HTML formatter and a specialised
    file stream handler.
    """

    def __init__(self,
                 name="html_logger",
                 level=logging.DEBUG,
                 filename="log.html", mode='w',
                 title="HTML Logger", version="1.0.0"):
        super().__init__(name, level)
        f = HTMLFormatter()
        h = HTMLFileHandler(title, version, filename, mode)
        h.setFormatter(f)
        self.addHandler(h)


#: Global logger instance
_logger = None


def setup(title, version, filename="Test_Report.html", mode='w', level=logging.DEBUG):
    """
    Setup the logger
    :param title: Title of the html document
    :param version: Framework/lib/app version
    :param filename: output filename. Default is "log.html"
    :param mode: File open mode. Default is 'w'
    :param level: handler output level. Default is DEBUG
    """
    filename=generate_report_name()
    filename=filename.replace("setup", "CanoePy_Robot_Framework_Report_")
    global _logger
    if _logger is None:
        _logger = HTMLLogger(filename=filename, mode=mode, title=title, version=version, level=level)


def ReportGreenMessage(msg, silent_flag="false"):
    """
    Logs a debug message
    """
    global _logger
    _logger.debug(msg)
    if (silent_flag == "false"):
        print(msg)

def ReportWhiteMessage(msg, silent_flag="false"):
    """
    Logs an info message
    """
    global _logger
    _logger.info(msg)
    if (silent_flag == "false"):
        print(msg)


def ReportYellowMessage(msg, silent_flag="false"):
    """
    Logs a warning message
    """
    global _logger
    _logger.warning(msg)
    if (silent_flag == "false"):
        print(msg)


def ReportRedMessage(msg, silent_flag="false"):
    """
    Logs an error message
    """
    global _logger
    _logger.error(msg)
    if (silent_flag == "false"):
        print(msg)


# Examples
#if __name__ == "__main__":
#    setup("Example", "1.0")
#    ReportDbgMsg("A debug message")
#    ReportInfoMsg("An information message")
#    ReportWarnMsg("A warning message")
#    time.sleep(1)
#    ReportErrorMsg("An error message")