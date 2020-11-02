from iqoptionapi.stable_api import IQ_Option
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import threading
import time, configparser, logging, sys
from datetime import datetime, timedelta
from dateutil import tz
import json

logging.disable(level=(logging.DEBUG))
logging.disable(level=(logging.ERROR))

def main():
  config = configparser.RawConfigParser()
  config.read('cnf.ini')

  global email
  email = formulario.email.text()
  config.set('GERAL', 'email', str(email))

  cfgfile = open('cnf.ini','w')
  config.write(cfgfile, space_around_delimiters=False)
  cfgfile.close()

  API = IQ_Option(email, formulario.senha.text())
  API.connect()

  while True:
    if API.check_connect() == False:
      formulario.plainTextEdit_2.addItem('Erro ao se conectar!')
      API.connect()
    else:
      formulario.plainTextEdit_2.addItem('Conectado com sucesso!')

      formulario.pushButton.setText('Robo Iniciado com Sucesso!')

      formulario.pushButton.setEnabled(False)
      formulario.comboBox.setEnabled(False)
      formulario.senha.setEnabled(False)
      formulario.email.setEnabled(False)
      formulario.delay.setEnabled(False)
      formulario.payout.setEnabled(False)
      formulario.gales.setEnabled(False)
      formulario.stopgain.setEnabled(False)
      formulario.stoploss.setEnabled(False)
      formulario.primeira.setEnabled(False)
      formulario.segunda.setEnabled(False)
      formulario.terceira.setEnabled(False)
      formulario.pushButton_2.setEnabled(False)
      break

    time.sleep(1)

  API.change_balance(conta)

  def banca():
    return round(API.get_balance(), 2)

  global saldo, saldo_mov
  saldo = banca()
  saldo_mov = saldo
  formulario.banca.setText(str(saldo))

  time.sleep(1)

  def Mensagem(msg):
    formulario.plainTextEdit_2.addItem(msg)

  def Payout(par,timeframe):
    API.subscribe_strike_list(par, timeframe)
    while True:
      d = API.get_digital_current_profit(par, timeframe)
      if d > 0:
        break
      time.sleep(1)
    API.unsubscribe_strike_list(par, timeframe)
    return float(d / 100)

  def carregar_sinais():
    arquivo = open('sinais.txt', encoding='UTF-8')
    lista = arquivo.read()
    arquivo.close

    lista = lista.split('\n')
    for index,a in enumerate(lista):
      if a == '':
        del lista[index]

    return lista

  def HoraAtual():
    hora = datetime.now()
    tm = tz.gettz('America/Sao Paulo')
    hora_atual = hora.astimezone(tm)
    return hora_atual.strftime('%H:%M:%S')

  def CalculaStop(valor_mov):
    global stop
    global stop_mensagem
    global saldo_mov

    saldo_mov = abs(saldo_mov + valor_mov)

    if (saldo + int(stopgain)) <= saldo_mov:
      stop = True
      stop_mensagem = 'Stop Win: ' + str(round((saldo_mov - saldo), 2))
    elif (saldo - int(stoploss)) >= saldo_mov:
      stop = True
      stop_mensagem = 'Stop Loss: ' + str(round((saldo_mov - saldo), 2))

  def entradas(par,entrada,direcao,config,timeframe):
    status,id = API.buy(int(entrada),par,direcao,int(timeframe))

    if status:
      lucro = API.check_win_v3(id)

      if lucro:
        if lucro > 0:
          return 'win',round(lucro, 2)
        elif lucro < 0:
          return 'loss',0
        elif lucro == 0:
          return 'equal',0
      '''
      resultado,lucro = API.check_win_v3(id)

      if resultado:
        if resultado == 'win':
          return 'win',round(lucro, 2)
        elif resultado == 'loose':
          return 'loss',0
        elif resultado == 'equal':
          return 'equal',0
      '''
    else:
      return 'error',0

  def IniciaTrade():
    sinais = carregar_sinais()

    Mensagem('')
    Mensagem('Moedas a serem operadas:')

    for y in sinais:
      Mensagem(y.split(';')[0].upper() + ' / ' + y.split(';')[2])

    for x in sinais:
      timeframe = x.split(';')[4].upper()
      par = x.split(';')[0].upper()
      dia = x.split(';')[1]
      minutos_lista = x.split(';')[2]
      direcao = x.split(';')[3].lower().replace('\n','')
      minutos_lista_delay = format(datetime.strptime(minutos_lista, '%H:%M:%S') - timedelta(seconds=int(delay)),"%H:%M:%S")

      dia_atual = format(datetime.now(), '%d')

      if dia_atual > dia:
        Mensagem('Dia informado é menor que o dia atual!')
        break

      if stop:
        Mensagem('')
        Mensagem(stop_mensagem)
        break

      while True:
        minutos = HoraAtual()

        if minutos_lista_delay < minutos:
          break

        if minutos > minutos_lista_delay:
          break

        entrar = True if (minutos_lista_delay == minutos ) else False

        if entrar:
          if True:
            Mensagem('')
            Mensagem('Iniciando Operaçao')
            Mensagem('Paridade: ' + par + ' / ' + 'Horario: ' + str(minutos_lista))
            resultado,lucro = entradas(par,primeira_entrada, direcao, config,timeframe)
            Mensagem('Paridade: ' + par + ' -> ' + resultado + ' / ' + str(lucro))

            if resultado == 'error':
              break

            if resultado == 'win':
              CalculaStop(lucro)
              break

            '''
            if stop:
              mensagem_stop = '\n\nStop '+ resultado.upper() + ' batido!'
              Mensagem(mensagem_stop)
              sys.exit()
            '''

            if resultado == 'loss' and int(gales) > 0:
              CalculaStop(int(primeira_entrada) * -1)
              valor_entrada = segunda_entrada
              for i in range(int(gales) if int(gales) > 0 else 1):
                Mensagem('Entrada Martingale Nivel ' + str(i+1) + ' - ' + HoraAtual())
                resultado,lucro = entradas(par, valor_entrada, direcao,config,timeframe)
                Mensagem('Resultado Martingale, Paridade: ' + par + ' -> ' + resultado + ' / ' + str(lucro))

                if resultado == 'win':
                  CalculaStop(lucro)
                  break
                else:
                  CalculaStop(int(valor_entrada) * -1)
                  valor_entrada = terceira_entrada
              break
            else:
              break
        time.sleep(0.1)

    Mensagem('')
    formulario.plainTextEdit_2.addItem('Lista Finalizada!')
    #sys.exit()

  threading.Thread(target=IniciaTrade).start()

def grava_configuracoes():
  config = configparser.RawConfigParser()
  config.read('cnf.ini')

  global payout
  payout = formulario.payout.value()
  config.set('ESTRATEGIA', 'payout', str(payout))

  global gales
  gales = formulario.gales.value()
  config.set('ESTRATEGIA', 'gales', str(gales))

  global stopgain
  stopgain = formulario.stopgain.text()
  config.set('ESTRATEGIA', 'stopgain', str(stopgain))

  global stoploss
  stoploss = formulario.stoploss.text()
  config.set('ESTRATEGIA', 'stoploss', str(stoploss))

  global primeira_entrada
  primeira_entrada = formulario.primeira.text()
  config.set('ENTRADAS', 'primeira', str(primeira_entrada))

  global segunda_entrada
  segunda_entrada = formulario.segunda.text()
  config.set('ENTRADAS', 'segunda', str(segunda_entrada))

  global terceira_entrada
  terceira_entrada = formulario.terceira.text()
  config.set('ENTRADAS', 'terceira', str(terceira_entrada))

  global delay
  delay = formulario.delay.value()
  config.set('ESTRATEGIA', 'delay', str(delay))

  cfgfile = open('cnf.ini','w')
  config.write(cfgfile, space_around_delimiters=False)
  cfgfile.close()

  QMessageBox.about(formulario, 'Informação', 'Configurações salvas com sucesso!')

app = QtWidgets.QApplication(sys.argv)

formulario=uic.loadUi("Principal.ui")

saldo = 0
saldo_mov = 0
stop = False
stop_mensagem = ''

arquivo = configparser.RawConfigParser()
arquivo.read('cnf.ini')

email = arquivo.get('GERAL', 'email')
formulario.email.setText(email)

conta = arquivo.get('GERAL', 'conta')
formulario.comboBox.setCurrentIndex(0)

payout = arquivo.get('ESTRATEGIA', 'payout')
formulario.payout.setValue(int(payout))

gales = arquivo.get('ESTRATEGIA', 'gales')
formulario.gales.setValue(int(gales))

stopgain = arquivo.get('ESTRATEGIA', 'stopgain')
formulario.stopgain.setText(stopgain)

stoploss = arquivo.get('ESTRATEGIA', 'stoploss')
formulario.stoploss.setText(stoploss)

primeira_entrada = arquivo.get('ENTRADAS', 'primeira')
formulario.primeira.setText(primeira_entrada)

segunda_entrada = arquivo.get('ENTRADAS', 'segunda')
formulario.segunda.setText(segunda_entrada)

terceira_entrada = arquivo.get('ENTRADAS', 'terceira')
formulario.terceira.setText(terceira_entrada)

delay = arquivo.get('ESTRATEGIA', 'delay')
formulario.delay.setValue(int(delay))

formulario.pushButton.clicked.connect(main)
formulario.pushButton_2.clicked.connect(grava_configuracoes)

formulario.show()
app.exec()
