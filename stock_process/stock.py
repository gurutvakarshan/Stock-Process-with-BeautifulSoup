from bs4 import BeautifulSoup
import urllib
import csv
import unicodedata
from itertools import izip_longest
import re
def scrap_stock_data():
	# PURPLE = '\033[95m'
	list_of_iter_data=[]
	list_of_iter_company_name=[]
	list_of_iter_detail_info=[]
	site = "http://www.moneycontrol.com"
	ok=urllib.urlopen("http://www.moneycontrol.com/india/stockpricequote/")
	raw_data = ok.read()
	soup = BeautifulSoup(raw_data,'lxml')
	# <div class="MT2 PA10 brdb4px alph_pagn">
	iter = soup.find_all("div",{"class":"MT2 PA10 brdb4px alph_pagn"})
	for each in iter:				
		find_a = each.find_all("a")
		skiped_first = find_a[1:]
		# print skip_first
		for each in skiped_first:
			find_href = each.get("href")
			# print find_href
			pass_url = site+find_href
			# print pass_url
			open_connection_for_hrefs = urllib.urlopen(pass_url)
			read_data = open_connection_for_hrefs.read()
			soup = BeautifulSoup(read_data,'lxml')
			iter = soup.find_all("a",{"class":"bl_12"})
			for each in iter:
				hrefs = each.get("href")#,each.get_text()
				company_href = hrefs.strip("javascript:;")
				if len(company_href)>0:
					# r = re.compile(r"^\s+", re.MULTILINE)
					# l = r.sub("", company_href)
					# print l
					open_connection_for_all_company_hrefs = urllib.urlopen(company_href)
					if open_connection_for_all_company_hrefs.getcode()==200:	
						html_data = open_connection_for_all_company_hrefs.read()
						soup = BeautifulSoup(html_data,'lxml')
						iter_company_name = soup.find_all("h1",{"class":"b_42 company_name"})
						iter_detail_info = soup.find_all("div",{"class":"FL gry10"})
						iter_data = soup.find_all("div",{"class":"brdb PA5"})
						for each in iter_company_name:
							uni_to_str = str(each.getText())
							formated_text = (" ").join(uni_to_str.split())
							# print a
							list_of_iter_company_name.append(formated_text)
						for each in iter_detail_info:
							uni_to_str = str(each.getText())
							formated_text = (" ").join(uni_to_str.split())
							# print a
							list_of_iter_detail_info.append(formated_text)
							# print type(uni_to_str)
						for each in iter_data:
							uni_to_str = str(each.getText())
							formated_text = (" ").join(uni_to_str.split()).strip()
							list_of_iter_data.append(formated_text)
						# 	print "------------------------------------------------------------------------------"
						# data = [list_of_iter_company_name,list_of_iter_detail_info,list_of_iter_data] 
						# print data
						# export_data = izip_longest(data,fillvalue = '')
						with open('stock_detail.csv','w') as v:
							spamwriter = csv.writer(v, delimiter=' ',quotechar=' ')
							# for each in list_of_iter_company_name:	
							# 	spamwriter.writerow(each)
							# for each in list_of_iter_detail_info:
							# 	spamwriter.writerow(each)
							# for each in list_of_iter_data:
							# 	spamwriter.writerow(each)
							for x in zip(list_of_iter_company_name,list_of_iter_detail_info,list_of_iter_data):
								# print x
								spamwriter.writerow(x)
								spamwriter.writerow(' ')
						v.close()
					else:
						pass
				else:
					pass
			
				
				
