import requests
import bs4
from bs4 import BeautifulSoup
from requests import request

data = request(method='GET', url='https://cdcs.ur.rochester.edu/Default.aspx')

soup = BeautifulSoup(data.content)
# parse and retrieve three vital form values
viewstate = soup.select("#__VIEWSTATE")[0]['value']
viewstategen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']

print viewstategen
formData = {
	'ScriptManager1':'UpdatePanel4|btnSearchTop',
	'__LASTFOCUS': '',
	'__EVENTTARGET': '',
	'__EVENTARGUMENT': '',
    '__EVENTVALIDATION': eventvalidation,
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategen,
   	'ddlTerm:': 'D-20161',
   	'ddlSchool': '',
   	'ddlDept': 'ACM',
	'txtCourse': '',
	'ddlTypes': '',
	'ddlStatus': '',
	'txtDescription': '',
	'txtTitle': '',
	'txtInstructor': '',
	'ddlTimeFrom': '',
	'ddlTimeTo': '',
	'ddlCreditFrom': '', 
	'ddlCreditTo': '',
	'ddlDivision': '',
   	'__ASYNCPOST': 'true',
   	'btnSearchTop' : 'Search',
}

headies = {
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'X-MicrosoftAjax': "Delta=true",
	'Accept-Encoding':'gzip, deflate',
	'Accept' : '*/*',
	'Accept-Language': 'en-US,en;q=0.8',
	'Cache-Control':'no-cache',
	'Connection':'keep-alive',
	'Host':'cdcs.ur.rochester.edu',
	'Origin':'https://cdcs.ur.rochester.edu',
	'Referer':'https://cdcs.ur.rochester.edu/',
}		

data = request(method='POST', url='https://cdcs.ur.rochester.edu/Default.aspx', headers= headies, data=formData)
print data.content
print data.status_code