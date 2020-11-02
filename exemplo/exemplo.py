from iqoptionapi.stable_api import IQ_Option
import time, json, sys, logging, configparser
from datetime import datetime
from dateutil import tz

#logging.disable(level=(logging.DEBUG))

API = IQ_Option('wagnerfilipe10@hotmail.com', 'DALEssandro10')

API.connect()

API.change_balance('PRACTICE')

while True:
	if API.check_connect() == False:
		print('Erro ao se conectar')
		API.connect()
	else:
		print('Conectado com sucesso')
		break

	time.sleep(1)

def perfil():
	perfil = json.loads(json.dumps(API.get_profile_ansyc()))

	return perfil

	'''
		name
		first_name
		last_name
		email
		city
		nickname
		currency
		currency_char
		address
		created
		postal_index
		gender
		birthdate
		balance
	'''

def timestamp_converter(x):
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))

	return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]

def banca():
	return API.get_balance()

def payout(par, tipo, timeframe = 1):
	if tipo == 'turbo':
		a = API.get_all_profit()
		return int(100 * a[par]['turbo'])

	elif tipo == 'digital':

		API.subscribe_strike_list(par, timeframe)
		while True:
			d = API.get_digital_current_profit(par, timeframe)
			if d != False:
				d = int(d)
				break
			time.sleep(1)
		API.unsubscribe_strike_list(par, timeframe)
		return d

def configuracao():
  arquivo = configparser.RawConfigParser()
  arquivo.read('cnf.ini')

  print(arquivo.get('GERAL', 'paridade'))

def carregar_sinais():
  arquivo = open('sinais.txt', encoding='UTF-8')
  lista = arquivo.read()
  arquivo.close

  lista = lista.split('\n')
  for index,a in enumerate(lista):
    if a == '':
      del lista[index]

  return lista

print(json.dumps(carregar_sinais(), indent=1))
