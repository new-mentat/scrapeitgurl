import requests
import bs4
from bs4 import BeautifulSoup
from requests import request
from time import sleep



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

data = request(method='GET', url='https://cdcs.ur.rochester.edu/Default.aspx')

soup = BeautifulSoup(data.content)
# parse and retrieve three vital form values
viewstate = soup.select("#__VIEWSTATE")[0]['value']
viewstategen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']




def getpage(category):
	global headies
	form_data = {
	'ScriptManager1':'UpdatePanel4|btnSearchTop',
	'__LASTFOCUS':'',
	'__EVENTTARGET':'',
	'__EVENTARGUMENT':'',
	'__VIEWSTATE': viewstate,
	'__VIEWSTATEGENERATOR': viewstategen,
	'__EVENTVALIDATION': eventvalidation,
	'ddlTerm':'D-20161',
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
	classinfo = request(method='POST', url='https://cdcs.ur.rochester.edu/Default.aspx', headers=headies, data=form_data)
	print classinfo.content
	return classinfo



getpage('AAS')