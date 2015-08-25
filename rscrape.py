import requests
import bs4
from bs4 import BeautifulSoup
from requests import request
from time import sleep
import re
import time
from config import CONFIG
import pymongo
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from requests.exceptions import ConnectionError

URI = CONFIG["URI"]
client = MongoClient(URI)
cs_db = client.ur_coursesniper
class_list = cs_db.classes


term = ""
depts = []
while True:
    try:
        data = request(method='GET', url='https://cdcs.ur.rochester.edu/Default.aspx')
        break
    except ConnectionError:
        sleep(5)
        continue
soup = BeautifulSoup(data.content)

# parse and retrieve three vital form values
viewstate = soup.select("#__VIEWSTATE")[0]['value']
viewstategen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']




headies = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'en-US,en;q=0.8',
    'Cache-Control':'no-cache',
    'Connection':'keep-alive',
    'Content-Length':'14069',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Host':'cdcs.ur.rochester.edu',
    'Origin':'https://cdcs.ur.rochester.edu',
    'Referer':'https://cdcs.ur.rochester.edu/',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    'X-MicrosoftAjax':'Delta=true',
}



def getpage(category):
    global headies
    global term
    global viewstate
    global viewstategen
    global eventvalidation


    form_data = {
    'ScriptManager1':'UpdatePanel4|btnSearchTop',
    '__LASTFOCUS':'',
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategen,
    '__EVENTVALIDATION': eventvalidation,
    'ddlTerm':term,
    'ddlSchool':'',
    'ddlDept':category,
    'txtCourse':'',
    'ddlTypes':'',
    'ddlStatus':'',
    'txtDescription':'',
    'txtTitle':'',
    'txtInstructor':'',
    'ddlTimeFrom':'',
    'ddlTimeTo':'',
    'ddlCreditFrom':'',
    'ddlCreditTo':'',
    'ddlDivision':'',
    '__ASYNCPOST':'true',
    'btnSearchTop':'Search',
    }
    while True:
        try:
            classinfo = request(method='POST', url='https://cdcs.ur.rochester.edu/Default.aspx', headers=headies, data=form_data)
            break   
        except ConnectionError:
            print("connection error")
            sleep(5)
            continue
    return classinfo.content

def page_parse(html):
    r_list = []
    crn_list = []
    cnum_list= []
    status_list = []

    aggregated = []
    soup = BeautifulSoup(html)
    crns = soup.find_all(id= re.compile('rpResults_ctl.*_lblCRN'))
    cnums = soup.find_all(id = re.compile('rpResults_ctl.*_lblCNum'))
    statuses = soup.find_all(id=re.compile('rpResults_ctl.*_lblStatus'))

  
    for crn in crns:
        crn = crn.string.strip()
        crn_list.append(crn)

    for cnum in cnums:
        cnum = cnum.string.strip()
        cnum_list.append(cnum)

    for status in statuses:
        status = status.string.strip()
        status_list.append(status)
    
    for x in range(0, len(crn_list)):
        aggregated.append((crn_list[x], cnum_list[x], status_list[x]))

    if(r_list == aggregated):
        print ("true")
    print aggregated
    return aggregated
    
def getlatestoptions():
    global term
    global depts

    while True:
        try:
           infohtml = request(method='GET', url='https://cdcs.ur.rochester.edu')
           break
        except ConnectionError:
            print("connection Error")
            sleep(5)
            continue

    infosoup = BeautifulSoup(infohtml.content)

    termhtml = infosoup.find(id="ddlTerm")
    termhtml = termhtml.prettify()

    termsoup = BeautifulSoup(termhtml)
    termtag = termsoup.find_all("option")

    latestterm = termtag[1]
    latestterm = latestterm['value']

    term = latestterm

    print("Latest term just updated to %s" % latestterm)
    
    infosoup = BeautifulSoup(infohtml.content)
    infosoup = infosoup.find(id="ddlDept")

    infotag = infosoup.find_all("option")

    departments = []

    for dept in infotag[1:len(infotag)]:
        departments.append(dept['value'])

    depts = departments
    print departments

def update_DB(class_tuples):
    global class_list
    posts = []
    for x in class_tuples:
        if(class_list.find_one({"CRN" : x[0] }) == None):
            posts.append({"CRN": x[0], "NAME": x[1], "STATUS": x[2], "Users": []})
        else:
            update_entry(x)

    if(posts):
        class_list.insert_many(posts)

def update_entry(class_tuple):
    global class_list
    post = class_list.find_one({"CRN": class_tuple[0]})

    if(post['STATUS'] == 'Open' and post['Users'] != None):
        snipe(post)
        class_list.update_one({"CRN": class_tuple[0]}, {'$set': {'Users': []}})

    if(post['STATUS'] == 'Closed' and class_tuple[2] == 'Open' ):
        print("Got one!")
        print(post)
        snipe(post)
        class_list.update_one({"CRN": class_tuple[0]}, {'$set': {'Users': []}})
        class_list.update_one({"CRN": class_tuple[0]}, {'$set': {'STATUS': class_tuple[2]}})
    elif(post['STATUS'] != class_tuple[2]):
        class_list.update_one({"CRN": class_tuple[0]}, {'$set': {'STATUS': class_tuple[2]}})

def snipe(post):
    for email in post['Users']:
        send_snipemail(email, post)

def send_snipemail(email, post):
    crn = post['CRN']
    s_class = post['NAME']
    from_addr = CONFIG["EMAIL"]

    #add option to resnipe here, and link to registration page
    msg = MIMEText("Hey!\n\n The class " + s_class + " you are currently sniping has just opened up.\n\nSnag it while it's still available! \n\n GL,\n Your Faithful Snipers")
    msg['From'] = 'ur.snipeteam@gmail.com'
    msg['To'] =  email
    msg['Subject'] = 'The course ' + s_class + ' has just opened up. Snag it!'


    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(from_addr,CONFIG["PASS"])
    server.sendmail('ur.snipeteam', email, msg.as_string())
    server.quit()


def crawl():
    global class_list 

    smartdepts = []

    tracked = class_list.find({"Users": {"$ne": []}})
    print("Going to track these courses:")
    for course in tracked:
        print course['NAME']
        dept = course['NAME'].split(' ')[0]
        smartdepts.append(dept)

    getlatestoptions()

    for dept in smartdepts:
        html = getpage(dept)
        class_tuples = page_parse(html)
        if class_tuples:
            update_DB(class_tuples)




while True:
    crawl()

