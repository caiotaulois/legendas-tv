#!/usr/bin/python
import getpass
import platform
from bs4 import BeautifulSoup
import re
import requests
import rarfile
import tempfile
import sys
from tempfile import NamedTemporaryFile
import json
from os.path import expanduser

class Subtitle:
	def __init__(self):
		self._url, self._downloads = '', 0
	
	@property
	def url(self):
		return self._url

	@url.setter
	def url(self, url):
		self._url = url
	
	@property
	def downloads(self):
		return self._downloads

	@url.setter
	def downloads(self, downloads):
		self._downloads = downloads

	def get_best_subtitle(self, response):
		soup = BeautifulSoup(response, 'html.parser')
		for div in soup.find_all('div', {'class': 'f_left'}):
			downloads = int(re.search('<p class="data">(.*) downloads', str(div.contents[1])).group(1))
			if downloads > self._downloads:
				self._downloads = downloads
				self._url = re.search('<p><a href="(/.*/.*)/.*/.*">.*</a></p>', str(div.contents[0])).group(1).replace('download', 'downloadarquivo')

	def extract_subtitles(self, content):
		tempfile = NamedTemporaryFile()
		tempfile.write(content)
		rar = rarfile.RarFile(tempfile)
		for file in rar.infolist():
			print file.filename
			if 'srt' in file.filename:
				rar.extract(file, path=expanduser("~"))

def get_serie_path():
	if len(sys.argv) != 4:
		print 'Argumentos: Serie Temporada Episodio'
		sys.exit(0)
	if int(sys.argv[2]) < 10:
		season = '0' + str(int(sys.argv[2]))
	else:
		season = str(int(sys.argv[2]))
	if int(sys.argv[3]) < 10:
		ep = '0' + str(int(sys.argv[3]))
	else:
		ep = str(int(sys.argv[3]))
	return sys.argv[1] + ' S' + season + 'E' + ep

def check_os():
	global os
	os = platform.system()

def login():
	'''	
	if os == 'Linux':
		config = open('.config', 'w+')
	else:
		print 'not linux'
	'''
	try:
		with open('.config', 'r') as config:
			config_json = json.load(config)
	except IOError:
		config_json = create_config()
	print 'login: ', config_json['username']
	params = {'data[User][username]': config_json['username'], 'data[User][password]': config_json['password']} 
	session = requests.Session()
	response = session.post('http://legendas.tv/login', data=params)
	if config_json['username'] not in response.text:
		print 'erro no login'
		exit(0)
	return session

def create_config():
	with open('.config', 'w+') as config:
		username = raw_input('Entre com o usuario: ')
		password = getpass.getpass('Entre com a senha: ')
		json.dump({'username': username, 'password': password}, config)
	with open('.config', 'r') as config:	
		return json.load(config)

serie_path = get_serie_path()
check_os()

#login
session = login()

#get subtitle rar
subtitle = Subtitle()
subtitle.get_best_subtitle(session.get('http://legendas.tv/util/carrega_legendas_busca/' + serie_path).text)

if subtitle.url:
	#extract subtitles
	subtitle.extract_subtitles(session.get('http://legendas.tv' + subtitle.url).content)	
else:
	print 'Legenda nao encontrada para serie ' + serie_path


