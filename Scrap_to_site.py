import requests, fake_useragent, csv
#import numpy as np
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from multiprocessing import Pool


def gen_hd():
	#Создаём новую личность
	#Создаём куки, сайт треубет
	ua = fake_useragent.UserAgent() 	
	headers = {'User-Agent': str(ua.random),
			   'Cookie': 'beget=begetok;expires=Mon,18Dec201817:28:35GMT;path=/'}
	return headers


def get_tor_session():
	#Создаём новую сессию
	#Наполняем прокси
	session = requests.session()
	session.proxies = {
						'http': 'socks5://127.0.0.1:9050',
						'https': 'socks5://127.0.0.1:9050'
					  }
	session.headers = gen_hd()
	return session


def renew_connect():
	#Создание нового подключения 
	with Controller.from_port(port=9051) as controller:
		controller.authenticate(password='Dred1477')
		controller.signal(Signal.NEWNYM)


def get_html(session, url):
	request = session.get(url)
	html = request.content
	soup = BeautifulSoup(html, 'lxml')
	return soup


def soup_find(soup, arg1, arg2, arg3, flag = None):
	if flag:		
		parse = soup.find(arg1, {arg2: arg3})
	else:
		parse = soup.findAll(arg1, {arg2: arg3})
	return parse


def make_urls(links, main_url):
	temp = []
	for link in links:
		url = link.find('a').get('href') 
		url = main_url + url
		temp.append(url)		
	return temp


def make_group(links):
	temp = []
	for link in links:
		url = link.find('a').text.split()
		url = ' '.join(url[:-1])
		temp.append(url)		
	return temp	


def data_find(soup):
	data = {}

	try:
		group = soup.findAll('a', {'class': 'pathway'})
		group = group[-1].text
	except:
		group = 'None'

	try:
		name = soup.find('h1', {'class': 'pro-title'})
		name = name.text
	except:
		name = 'None'
	
	try:
		price = soup.find('span', {'class': 'attribut_actual_price'})
		price = price.text
	except:
		price = 'None'
	
	try:
		about = soup.find('div', {'class': 'jshop_prod_short_description'}).text
		about = about.replace('\r', '')
		about = about.strip().split('\n')
		about = list(filter(None, about))
		about = [i for i in about if i!=' ']
		about = '$ '.join(about)

	except:
		about = 'None'

	try:			
		features = soup.find('div', {'class': 'jshop_prod_description'}).text
		features = features.replace('\r', '')
		features = features.strip().split('\n')
		features = list(filter(None, features))
		features = [i for i in features if i!=' ']
		features = '$ '.join(features)	
	except:
		features = 'None'

	try:
		colors = soup.findAll('span', {'class': 'attribut_name'})
		colors = [i.text.strip() for i in colors]
		colors = '$ '.join(colors)
	except:
		colors	= 'None'	

	data['group'] = group
	data['name'] = name
	data['price'] = price
	data['about'] = about
	data['features'] = features
	data['colors'] = colors
	

	return data


def write_csv(data):
	with open('data.csv','a', encoding='utf8', newline='') as f:
		writer = csv.writer(f, delimiter='|')
		writer.writerow( (data['group'],
						  data['name'],
						  data['price'],
						  data['about'],
						  data['features'], 
						  data['colors']
						  ) 
						)		


def get2poolAll(url):
	session = get_tor_session()
	soup = get_html(session, url)
	data = data_find(soup)
	write_csv(data)
		

def main():

	with open('data.csv','a', encoding='utf8', newline='') as f:
		writer = csv.writer(f, delimiter='|')
		writer.writerow( ('Group',
						  'ID' ,
						  'Price' ,
						  'About' ,
						  'Features', 
						  'Colors' 
						  ) 
						)	

	session = get_tor_session()

	print( 'Tor_IP: ', session.get('http://httpbin.org/ip').text )
	print( 'Real IP: ', requests.get('http://httpbin.org/ip').text )
	print(session.proxies, '\n', session.headers)


	main_url = 'http://bon-papa.ru'

	all_data = {}

	#Пул ссылок 1 уровня
	soup = get_html(session, main_url)
	table = soup.find('div', {'class': 'modcontent-inner clearfix'})
	arg_list = ['div', 'class', 'jshop_menu_level_0 categories_menu']
	links_lvl_1 = soup_find(table, *arg_list)
	groups = make_group(links_lvl_1)
	links_lvl_1 = make_urls(links_lvl_1, main_url)


	#Пул ссылок 2 уровня
	for url in links_lvl_1:	
		soup = get_html(session, url)
		arg_list = ['div', 'class', 'jshop_list_product']
		table = soup_find(soup, *arg_list, 1)
		arg_list = ['div', 'class', 'span4']
		links_lvl_2 = soup_find(soup, *arg_list)
		links_lvl_2 = make_urls(links_lvl_2, main_url)
		print(len(links_lvl_2))
		with Pool(10) as p:
			p.map(get2poolAll, links_lvl_2)
		#print(links_lvl_2[2])
		#get2poolAll(links_lvl_2[2],session)			
		#break


	#3 уровень	
	for urls in links_lvl_2:
		break
		soup = get_html(session, url)
		data = data_find(soup)
		all_data[groups[inx]] = data
		print(url_)
		print(groups[inx])	
		print(data)		


	#Открыть поочерёдно ссылки из пулла ссылок 2 уровня
	#Забрать: 
	#Tag - Название товара
	#Price - Цена товара
	#About[] - Описание
	#TH[] - Характеристики	
	#Images[] - картинки товара в разных цветах -> np.array()
	#Colors[] - название цветов для товара
	#Открыть файл
	#Записать в файл
	#
	#open2write('.h5', 'Уход, кормление', [0.1,55,112,.05],[1,5,1],55,['name'])


if __name__ == '__main__':
	main()
######################################################################
######################################################################
######################################################################
######################################################################

