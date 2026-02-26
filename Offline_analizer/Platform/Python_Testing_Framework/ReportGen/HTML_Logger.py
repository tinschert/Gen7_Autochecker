#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024


"""
HTML logger by Ventsislav Negentsov
"""
import logging
import time
from datetime import datetime
import os
import webbrowser

global_HTML_report_name=""
global_XML_report_name=""
global global_XML_file_handler
global_filename=""

#this is a global variable used in the .format() function that is called automatically by logging library
#if value == True means you want to report an image and then _IMG_FMT is return instead of _MSG_FMT
# 0 -> default formatting (colors - white, yellow, green, no images)
# 1 -> image formatting
# 2 -> BLUE text
# 3 -> HTML Link
# 4 -> Nested HTML with provided filename
# 5 -> JPG/BMP/PNG picture insert
special_formatting = 0

def all_files_under(path):
    """Iterates through all files that are under the given path."""
    for cur_path, dirnames, filenames in os.walk(path):
        for filename in filenames:
            yield os.path.join(cur_path, filename)

def find_newest_file_in_folder(path):
    latest_file = max(all_files_under(path), key=os.path.getmtime)
    latest_file = latest_file.replace(path, "")
    latest_file = latest_file.replace("/", "")
    latest_file = latest_file.replace('\\', "")
    #print("latest_file =", latest_file)
    return latest_file

def generate_report_name():
    import inspect #import has to be here otherwise datetime() function returns the time date of the import operation (always the same)
    #ret_val=""
    if not os.path.exists("Reports"): os.makedirs("Reports")
    if not os.path.exists("Reports\\plots"): os.makedirs("Reports\\plots")
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
width: 2440px;
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
font-size: 16px;
margin : 0;
}
.box {
border : 1px dotted #818286;
padding : 5px;
margin: 5px;
width: 2440px;
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
.blue {
color: #8888FF;
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
</tr>
"""

_IMG_FMT = """
<table>
<tr>
<td width="100">%(time)s</td>
<td class="%(class)s"><pre>%(msg)s</pre></td>
<img src=%(msg)s alt="CANoePy signal trace plot" width="950" height="700">
"""

_HTML_LINK_FMT = """
<tr>
<td width="100"></td>
<td>
<embed type="text/html" src="%(msg)s" width="1600" height="1200">
<a href=%(msg)s>Signal Plot</a>
</td>
"""

_HTML_DF_FMT = """
<tr>
<td width="100"></td>
<td>
%(msg)s
</td>
"""

_HTML_HYPERLINK = """
<tr>
<td width="100"></td>
<td>
<a href=%(msg)s>Signal Plot</a>
</td>
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
        globals()["global_XML_file_handler"].write("</TestCase>\n\n")
        globals()["global_XML_file_handler"].write("</CANoePy_XML_Report>")
        globals()["global_XML_file_handler"].close()


class HTMLFormatter(logging.Formatter):
    """
    Formats each record in html
    """
    CSS_CLASSES = {'WARNING': 'warn',
                   'INFO': 'info',
                   'DEBUG': 'debug',
                   'CRITICAL': 'err',
                   'ERROR': 'err',
                   'BLUE':'blue'}

    def __init__(self):
        super().__init__()
        self._start_time = time.time()

    #this function format() is called automatically by logging library
    def format(self, record):
        global special_formatting    #using the global flag for image or text

        try:
            class_name = self.CSS_CLASSES[record.levelname]
        except KeyError:
            class_name = "info"

        t = time.time() - self._start_time

        # handle '<' and '>' (typically when logging %r)
        msg = record.msg
        if special_formatting != 6:
            msg = msg.replace("<", "&#60")
            msg = msg.replace(">", "&#62")

        # 0 -> default formatting (colors - white, yellow, green, no images)
        # 1 -> image formatting
        # 2 -> BLUE text
        # 3 -> HTML Link
        # 4 -> Nested HTML with provided filename
        # 5 -> JPG/BMP/PNG picture insert
        global global_filename

        if (special_formatting == 0):
            return _MSG_FMT % {"class": class_name, "time": "%.4f" % t, "msg": msg}
        if (special_formatting == 1):
            f_name="plots\\"+find_newest_file_in_folder(r'Reports\plots')
            return _IMG_FMT % {"class": class_name, "time": "%.4f" % t, "msg": f_name}
        if (special_formatting == 2):
            return _MSG_FMT % {"class": self.CSS_CLASSES['BLUE'], "time": "%.4f" % t, "msg": msg}
        if (special_formatting == 3):
            f_name = "plots\\" + find_newest_file_in_folder(r'Reports\plots')
            return _HTML_LINK_FMT % {"class": class_name, "time": "%.4f" % t, "msg": f_name}
        if (special_formatting == 4):
            return _HTML_LINK_FMT % {"class": class_name, "time": "%.4f" % t, "msg": global_filename}
        if (special_formatting == 5):
            return _IMG_FMT % {"class": class_name, "time": "%.4f" % t, "msg": global_filename}
        if (special_formatting == 6):
            return _HTML_DF_FMT % {"class": class_name, "time": "%.4f" % t, "msg": msg}
        if (special_formatting == 7):
            f_name = "plots\\" + find_newest_file_in_folder(r'Reports\plots')
            return _HTML_HYPERLINK % {"class": class_name, "time": "%.4f" % t, "msg": f_name}

class HTMLLogger(logging.Logger):
    """
    Log records to html using a custom HTML formatter and a specialised
    file stream handler.
    """
    f = None
    h = None

    def __init__(self,
                 name="html_logger",
                 level=logging.DEBUG,
                 filename="log.html", mode='w',
                 title="HTML Logger", version="1.0.0"):
        super().__init__(name, level)
        self.f = HTMLFormatter()
        self.h = HTMLFileHandler(title, version, filename, mode)
        self.h.setFormatter(self.f)
        self.addHandler(self.h)

#: Global logger instance
_logger = None


def setup(title, version, filename="Reports\\Test_Report.html", mode='w', level=logging.DEBUG):
    """
    Setup the logger
    :param title: Title of the html document
    :param version: Framework/lib/app version
    :param filename: output filename. Default is "log.html"
    :param mode: File open mode. Default is 'w'
    :param level: handler output level. Default is DEBUG
    """
    globals()["global_HTML_report_name"] = filename
    globals()["global_XML_report_name"] = filename.replace(".html","")+".xml"
    global _logger
    if _logger is None:
        _logger = HTMLLogger(filename=filename, mode=mode, title=title,
                             version=version, level=level)
    globals()["global_XML_file_handler"] = open(globals()["global_XML_report_name"], "w")
    globals()["global_XML_file_handler"].write("<CANoePy_XML_Report>\n")
    globals()["global_XML_file_handler"].write("<TestCase>\n\n")

def ReportGreenMessage(msg, silent_flag=False):
    """
    Logs a debug message
    """
    global _logger
    if (silent_flag == False):
        _logger.debug(msg)
        print(msg)
        globals()["global_XML_file_handler"].write(msg)
        globals()["global_XML_file_handler"].write("\n")

def ReportWhiteMessage(msg, silent_flag=False):
    """
    Logs an info message
    """
    global _logger
    if (silent_flag == False):
        #⎯
        #&#9135;
        print(msg)
        msg = msg.replace("-","&#9135;")
        _logger.info(msg)
        globals()["global_XML_file_handler"].write(msg)
        globals()["global_XML_file_handler"].write("\n")


def ReportYellowMessage(msg, silent_flag=False):
    """
    Logs a warning message
    """
    global _logger
    if (silent_flag == False):
        _logger.warning(msg)
        print(msg)
        globals()["global_XML_file_handler"].write(msg)
        globals()["global_XML_file_handler"].write("\n")


def ReportRedMessage(msg, silent_flag=False):
    """
    Logs an error message
    """
    global _logger
    if (silent_flag == False):
        _logger.error(msg)
        print(msg)
        globals()["global_XML_file_handler"].write(msg)
        globals()["global_XML_file_handler"].write("\n")

def ReportBlueMessage(msg, silent_flag=False):
    """
    Logs an error message
    """

    if (silent_flag == False):
        global special_formatting
        special_formatting = 2
        global _logger
        _logger.warning(msg)
        special_formatting = 0
        print(msg)
        globals()["global_XML_file_handler"].write(msg)
        globals()["global_XML_file_handler"].write("\n")

def ReportImage(msg, path_to_file = "", silent_flag=False):
    """
    Logs an error message
    """
    # 0 -> default formatting (colors - white, yellow, green, no images)
    # 1 -> image formatting
    # 2 -> BLUE text
    # 3 -> HTML Link
    # 4 -> Nested HTML with provided filename
    # 5 -> JPG/BMP/PNG picture insert
    global special_formatting
    global _logger
    global global_filename
    global_filename = path_to_file

    if path_to_file=="": special_formatting = 1
    else:  special_formatting = 5

    _logger.warning(msg)
    special_formatting = 0
    if (silent_flag == False):
        print(msg)

def ReportHTMLLink(msg, path_to_file = "", hyperlink=False, silent_flag=False):
    """
    Logs an error message
    """
    # 0 -> default formatting (colors - white, yellow, green, no images)
    # 1 -> image formatting
    # 2 -> BLUE text
    # 3 -> HTML Link
    # 4 -> Nested HTML with provided filename
    # 5 -> JPG/BMP/PNG picture insert
    global special_formatting
    global _logger
    global global_filename
    global_filename = path_to_file

    if path_to_file == "":
        special_formatting = 3
    elif hyperlink:
        special_formatting = 7
    else:
        special_formatting = 4

    _logger.warning(msg)
    special_formatting = 0
    if (silent_flag == False):
        print(msg)


def ReportDF_HTML(msg, silent_flag=False):
    """
    Logs a warning message
    """
    global _logger
    global special_formatting
    special_formatting = 6
    if (silent_flag == False):
        _logger.warning(msg)
        print(msg)
    special_formatting = 0

# Examples
#if __name__ == "__main__":
#    setup("Example", "1.0")
#    ReportDbgMsg("A debug message")
#    ReportInfoMsg("An information message")
#    ReportWarnMsg("A warning message")
#    time.sleep(1)
#    ReportErrorMsg("An error message")

def Show_HTML_Report(path=None):
    if path:
        webbrowser.open(path)
    else:
        f_name="Reports\\"+find_newest_file_in_folder('Reports')
        webbrowser.open(f_name)



def Offline_Testcase_Start(title, version, filename):
    setup(title, version, filename)  # create the HTML report

def TestReportHeader(string):
    global_XML_file_handler.write("<TestCaseHeader>\n")
    ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    ReportWhiteMessage("|        "+string)
    ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    ReportWhiteMessage("\n")

    #handle RQM data explicitly
    if (string.find("Requirement_ID : ")>=0):
        global_XML_file_handler.write("<Requirement_ID>")
        global_XML_file_handler.write(string.split("Requirement_ID : ")[1])
        global_XML_file_handler.write("</Requirement_ID>\n\n")
    if (string.find("TestCaseName : ")>=0):
        global_XML_file_handler.write("<TestCaseName>")
        global_XML_file_handler.write(string.split("TestCaseName : ")[1])
        global_XML_file_handler.write("</TestCaseName>\n\n")
    if (string.find("RQM_ID : ")>=0):
        global_XML_file_handler.write("<RQM_ID>")
        global_XML_file_handler.write(string.split("RQM_ID : ")[1])
        global_XML_file_handler.write("</RQM_ID>\n\n")

    global_XML_file_handler.write("</TestCaseHeader>\n\n")


def ReportOfflineTestStepPass():
    global_XML_file_handler.write("<TestStepResult>\n")
    ReportGreenMessage("PASSED")  # green colour
    global_XML_file_handler.write("</TestStepResult>\n")


def ReportOfflineTestStepFail():
    global_XML_file_handler.write("<TestStepResult>\n")
    ReportRedMessage("FAILED")  # green colour
    global_XML_file_handler.write("</TestStepResult>\n")

def ReportFinalVerdict():
    #ReportWhiteMessage(80 * "-")
    verdict = "PASSED"

    f_name = "Reports\\" + find_newest_file_in_folder('Reports')

    global_XML_file_handler.write("<FinalResult>\n")
    with open(f_name) as f:
        for line in f:
            if "FAILED" in line:
                verdict = "FAILED"

    if verdict == "PASSED":
        ReportGreenMessage(f"Final Verdict: PASSED")
    else:
        ReportRedMessage(f"Final Verdict: FAILED")

    global_XML_file_handler.write("</FinalResult>\n")

def ReportTestStepStart():
    global_XML_file_handler.write("<TestStep>\n")

def ReportTestStepEnd():
    global_XML_file_handler.write("</TestStep>")

def generate_report_offline(tc_name):
    if not os.path.exists("Reports"): os.makedirs("Reports")
    if not os.path.exists("Reports\\plots"): os.makedirs("Reports\\plots")
    now = datetime.now()
    # Format the date and time with underscores
    formatted_datetime = now.strftime("%Y_%m_%d_%H_%M_%S")
    ret_val = fr"Reports\{tc_name.split('.')[0]}___{formatted_datetime}.html"

    # UNCOMMENT IN CASE TC TO BE CREATED IN A SEPARATE FOLDERS!!!
    # ret_val = fr"Reports\{tc_name.split(".")[0]}_{formatted_datetime}\{tc_name.split(".")[0]}___{formatted_datetime}.html"
    # os.makedirs(fr"Reports\{tc_name.split(".")[0]}_{formatted_datetime}")
    return ret_val