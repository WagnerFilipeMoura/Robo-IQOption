from iqoptionapi.stable_api import IQ_Option
import time, json
from datetime import datetime
from dateutil import tz

API = IQ_Option('login', 'senha')
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



## Pegar até 1000 velas #########################
par = 'EURUSD'

vela = API.get_candles(par, 60, 10, time.time())

for velas in vela:
	print('Hora inicio: '+str(timestamp_converter(velas['from']))+' abertura: '+str(velas['open']))


## Pegar mais de 1000 velas #########################
par = 'EURUSD'

total = []
tempo = time.time()

for i in range(2):
	X = API.get_candles(par, 60, 1000, tempo)
	total = X+total
	tempo = int(X[0]['from'])-1

for velas in total:
	print(timestamp_converter(velas['from']))


# Pegar velas em tempo real #########################
par = 'EURUSD'

API.start_candles_stream(par, 60, 1)
time.sleep(1)



while True:
	vela = API.get_realtime_candles(par, 60)
	for velas in vela:
		print(vela[velas]['close'])
	time.sleep(1)
API.stop_candles_stream(par, 60)

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

par = API.get_all_open_time()

for paridade in par['turbo']:
	if par['turbo'][paridade]['open'] == True:
		print('[ TURBO ]: '+paridade+' | Payout: '+str(payout(paridade, 'turbo')))

print('\n')

for paridade in par['digital']:
	if par['digital'][paridade]['open'] == True:
		print('[ DIGITAL ]: '+paridade+' | Payout: '+str( payout(paridade, 'digital') ))


# Retorna o histórico, para pegar o histórico do digital, deve ser colocado 'digital-option' e para pegar binario,
#	deve ser colocado 'turbo-option'
status,historico = API.get_position_history_v2('turbo-option', 7, 0, 0, 0)

'''

:::::::::::::::: [ MODO DIGITAL ] ::::::::::::::::
FINAL OPERACAO : historico['positions']['close_time']
INICIO OPERACAO: historico['positions']['open_time']
LUCRO          : historico['positions']['close_profit']
ENTRADA        : historico['positions']['invest']
PARIDADE       : historico['positions']['raw_event']['instrument_underlying']
DIRECAO        : historico['positions']['raw_event']['instrument_dir']
VALOR          : historico['positions']['raw_event']['buy_amount']

:::::::::::::::: [ MODO BINARIO ] ::::::::::::::::
MODO TURBO tem as chaves do dict diferentes para a direção da operação(put ou call)
	e para exibir a paridade, deve ser utilizado:
DIRECAO : historico['positions']['raw_event']['direction']
PARIDADE: historico['positions']['raw_event']['active']
'''

for x in historico['positions']:
	print('PAR: '+str(x['raw_event']['active'])+' /  DIRECAO: '+str(x['raw_event']['direction'])+' / VALOR: '+str(x['invest']))
	print('LUCRO: '+str(x['close_profit'] if x['close_profit'] == 0 else round(x['close_profit']-x['invest'], 2) ) + ' | INICIO OP: '+str(timestamp_converter(x['open_time'] / 1000))+' / FIM OP: '+str(timestamp_converter(x['close_time'] / 1000)))
	print('\n')

par = 'EURUSD'
entrada = 2
direcao = 'call'
timeframe = 1

# Entradas na digital
_,id = API.buy_digital_spot(par, entrada, direcao, timeframe)

if isinstance(id, int):
	while True:
		status,lucro = API.check_win_digital_v2(id)

		if status:
			if lucro > 0:
				print('RESULTADO: WIN / LUCRO: '+str(round(lucro, 2)))
			else:
				print('RESULTADO: LOSS / LUCRO: -'+str(entrada))
			break

# Entradas na binaria
status,id = API.buy(entrada, par, direcao, timeframe)

if status:
	resultado,lucro = API.check_win_v3(id)

	print('RESULTADO: '+resultado+' / LUCRO: '+str(round(lucro, 2)))

def configuracao():
	arquivo = configparser.RawConfigParser()
	arquivo.read('config.txt')

	return {'paridade': arquivo.get('GERAL', 'paridade'), 'valor_entrada': arquivo.get('GERAL', 'entrada'), 'timeframe': arquivo.get('GERAL', 'timeframe')}

print(configuracao())


'''
lista de sinais deve ter o formato:
DATA HORA,PARIDADE,DIRECAO
'''

def carregar_sinais():
	arquivo = open('sinais.txt', encoding='UTF-8')
	lista = arquivo.read()
	arquivo.close

	lista = lista.split('\n')

	for index,a in enumerate(lista):
		if a == '':
			del lista[index]

	return lista


print('\n\n')

lista = carregar_sinais()


for sinal in lista:
	dados = sinal.split(',')

	print(dados[0])
	print(dados[1])
	print(dados[2])
