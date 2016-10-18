# coding=utf-8
from time import strptime, localtime
#from base64 import b64decode as decode
from email.mime.text import MIMEText
from email.header import Header
import requests
from bs4 import BeautifulSoup as bs
import smtplib
__VERSION__ = 3.1
__DAYTOREMIND__ = 3
__SSDUT__ = "http://ssdut.dlut.edu.cn/"
__TYPELIST__ = [
    {
        "type_title":u"本科生通知",
        "url":"index/bkstz.htm"
    },
    {
        "type_title":u"学院通知",
        "url":"index/xytz.htm"
    }
]
__RECEIVERS__ = ['haoshui0mail@vip.qq.com',
                 '860895220@qq.com',
                 '965834929@qq.com'
                ]

def get_each_line(type_list_page_url):
    ''' get each line of list page and return a list of line dict.
        
        In: string
        Out:
            {
                "title": string,
                "date": string,
                "url": string
            }
    '''
    result = list()
    type_list_page = requests.get(type_list_page_url).content
    soup = bs(type_list_page, "html.parser")
    noti_area = soup.find(class_="c_hzjl_list1")
    noti_list = noti_area.find_all("a", target="_blank")
    time_list_origin = noti_area.find_all(class_="fr")
    time_list = [x.get_text(strip=True) for x in time_list_origin]

    log_file = open("ssdut-noti.log", "r+")
    existed_urls = [line[:-1] for line in log_file.readlines()]

    for i, line in enumerate(noti_list):
        # if is_new(time_list[i]) && line.get_text() not in:
        line_dict = dict()
        line_dict["title"] = line["title"]
        line_dict["url"] = __SSDUT__ + line["href"][3:]
        line_dict["date"] = time_list[i]
        if is_to_keep(existed_urls, line_dict):
            result.append(line_dict)
            log_file.write("%s\n" % line_dict["url"])

    log_file.close()
    return result

def is_to_keep(existed_urls, line_dict):
    ''' to combine two comparation into only one.
    existed_url is a list formed by file.readlines()
    line_dict you know that.

    return  bool
    '''
    if is_new(line_dict["date"]):
        if line_dict["url"] not in existed_urls:
            return True
    return False

def is_new(date_str):
    ''' judge if date is new (compare with today and __DAYTOREMIND__)
    Out: Bool
    '''
    today = localtime()
    parsed_date = strptime(date_str, '%Y-%m-%d')

    def calc_date_delta(date1, date2):
        list_has_31days = (1, 3, 5, 7, 8, 10, 12)
        list_has_30days = (4, 6, 9, 11)
        if date1[1] == date2[1]:  # Same month
            return date1[2] - date2[2]
        elif date1[1] in list_has_31days:
            return date1[2] + 31 - date2[2]
        elif date1[1] in list_has_30days:
            return date1[2] + 30 - date2[2]
        else:
            return date1[2] + 28 - date2[2]

    return bool(calc_date_delta(today, parsed_date) <= __DAYTOREMIND__)

def get_type_list():
    ''' just to use 'for' to get every type's notice'''
    for each_type in __TYPELIST__:
        each_type["list"] = get_each_line(__SSDUT__ + each_type["url"])

def make_content():
    ''' using globle varity __TYPELIST__ to make push content '''
    result = ''
    for each_type in __TYPELIST__:
        if len(each_type["list"]): # has list
            result += "<h3>We get %d new notifications from column %s</h3>%s<hr>" % (len(each_type["list"]), 
            each_type["type_title"], make_each_line_content(each_type["list"]))
        else:
            result += "<h4>No new notifications in column %s.</h4>" % each_type["type_title"]
    result += "<footer>Powered by <a href='https://XSky123.com'>XSky Notice System</a> version %s</footer>" % __VERSION__

    return result
def make_each_line_content(line_list):
    ''' return each type 's content, and group by date'''
    content = ""
    date_group = dict()

    for line in line_list:
        date_group[line["date"]] = list() # init date_group

    for line in line_list:
        date_group[line["date"]].append({"title":line["title"],"url":line["url"]}) # group by date

    for date, newlist  in date_group.items():
        line_head = '''<h4>%s</h4>''' % date # date
        line_body = ""

        for line in newlist:
            line_body += '''<li><a href=\"%s\">%s</a></li>''' % (line["url"], line["title"])


        content += "%s<ul>%s</ul>" % (line_head, line_body)

    return content

def send_mail(content):

    mail_host = your_host
    mail_user = your_user
    mail_pass = your_pass
    sender = mail_user

    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header("XSky", 'utf-8')
    message['To'] = Header("Receiver", 'utf-8')
    subject = 'SSDUT daily update'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtp_obj = smtplib.SMTP_SSL()
        smtp_obj.connect(mail_host)
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, __RECEIVERS__, message.as_string())
        print "Success"
    except smtplib.SMTPException:
        print "Error"

def main():
    get_type_list()
    content = make_content()
    send_mail(content)

if __name__ == '__main__':
    main()
