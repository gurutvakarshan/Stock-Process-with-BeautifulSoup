import requests
import lxml
import threading
import csv
import sys
from multiprocessing import cpu_count,Pool
from urllib import urlopen
from functools import partial
from bs4 import BeautifulSoup
from threading import Thread 
from Queue import Queue
reload(sys)
sys.setdefaultencoding('utf8')

base_url= "https://www.usedpart.us/database/parts/"
counter = 0
product_list = []
used_prdts_part_list = []
used_prdts_parts_list = []
headers = { 
	"Accept" : "text/html",
	"Accept-Encoding":"gzip",
	"Accept-Language":"en-GB",
	"Connection" : "keep-alive",
	"Host" : "www.usedpart.us",
	"Upgrade-Insecure-Requests" : "1",
	"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/60.0",
}

outfile = open("VehicleParts.csv", "w")
writer = csv.writer(outfile,delimiter='\t', quoting=csv.QUOTE_ALL)
writer.writerow(['Product Name','Used Product Part Name','Used Part Url','Img Url','Part System','Part Name','Description'])

def take_domain_request():
	take_request = requests.get(base_url,headers=headers)
	print (take_request.status_code)
	soup = BeautifulSoup(take_request.content,"lxml")
	first_iteration = soup.find_all("a",{"class":"resort_main_page_link"})
	for product_name in first_iteration:
		product_list.append(str(product_name.get("href")))
	# product_in = list(set(product_list))
# print product_in[:1]

def take_used_product_request(each_prd):
	# for each_prd in list(set(product_list)):
	prd_request = requests.get(each_prd,headers=headers)
	# print (prd_request.status_code)
	prd_soup = BeautifulSoup(prd_request.content,"lxml") 
	second_iteration = prd_soup.find_all("span",{"style":"color: #0000ff;"})
	for each in second_iteration:
		anchor = each.find_all("a")
		for tag in anchor:
			used_prdts_part_list.append(tag.get("href"))

def take_used_products_parts_request(each):
	part_req = requests.get(each,headers=headers)
	part_soup = BeautifulSoup(part_req.content,"lxml")
	third_iteration = part_soup.find_all("p")
	for anchor in third_iteration:
		anchor = anchor.find_all("a")
		for href in anchor:
			used_prdts_parts_list.append({str(each):href.get("href")})
# print used_prdts_parts_list
# print len(used_prdts_parts_list)

def make_meta_request(link):
	# for link in used_prdts_parts_list:
	temp_list = []
	prd_nm = link.keys()[0]
	product = prd_nm.split('/')[5]
	used_product_part_nm = prd_nm.split('/')[6]
	prd_lnk = link.values()[0]
	if 'parts' in prd_lnk.split('/'):
		pass
	else:
		data_url_req = requests.get(prd_lnk,headers=headers)
		data_soup = BeautifulSoup(data_url_req.content,"lxml")
		imgsrc_iteration = data_soup.find("img",{"class":"attachment-full size-full wp-post-image"})
		data_description = data_soup.find_all("span",{"style":"font-size: 14pt;"})
		get_system = prd_lnk.split('/')[4]
		get_part_nm = prd_lnk.split('/')[5] 
		for des in data_description:
			temp_list.append(str(des.get_text()))
		description = str(''.join(temp_list).replace(',','.'))
		
		try:
			imgurl = imgsrc_iteration.get("src")
			img = urlopen(imgurl)
		except (AttributeError,TypeError):
			imgurl = ''
			img = ''
	
		if imgurl != '':
			counter = counter+1
			writer.writerow([product,used_product_part_nm,prd_lnk,imgurl,get_system,get_part_nm,description])	
			with open('PartsImages/'+str(counter)+'.jpeg','wb') as f:
				f.write(img.read())
		else:
			counter = counter+1
			writer.writerow([product,used_product_part_nm,prd_lnk,'',get_system,get_part_nm,description])	
		del temp_list			

class DownloadWorker1(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            each_prd = self.queue.get()
            try:
                take_used_product_part_request(each_prd)
            finally:
                self.queue.task_done()

class DownloadWorker2(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            each = self.queue.get()
            try:
                take_used_products_parts_request(each)
            finally:
                self.queue.task_done()

class DownloadWorker3(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            link = self.queue.get()
            try:
                make_meta_request(link)
            finally:
                self.queue.task_done()


def main1():
	queue = Queue()
	
	for x in range(12):
		worker = DownloadWorker1(queue)
		worker.daemon = True
		worker.start()
	for each in list(set(product_list)):														
		queue.put((each))                      
	queue.join()

def main2():
	queue = Queue()
	
	for x in range(12):
		worker = DownloadWorker2(queue)
		worker.daemon = True
		worker.start()
	for each in used_prdts_part_list:														
		queue.put((each))                      
	queue.join()

def main3():
	queue = Queue()
	for x in range(12):
		worker = DownloadWorker3(queue)
		worker.daemon = True
		worker.start()
	for link in used_prdts_parts_list:														
		queue.put((link))                      
	queue.join()


if __name__ == "__main__":
	print "Inside take_domain_request..."
	take_domain_request()
	print "Inside main1..."
	main1()
	print "Inside main2..."
	main2()
	print "Inside main3..."
	main3()



