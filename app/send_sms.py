# -*- coding: utf-8 -*-
# SMSC.RU API (smsc.ru) версия 2.0 (03.07.2019)
import os
from dotenv import load_dotenv

from datetime import datetime
from time import sleep
import smtplib
import random

# from config import (SMSC_LOGIN, SMSC_PASSWORD, SMSC_POST, 
#                     SMSC_HTTPS, SMSC_CHARSET, SMSC_DEBUG)
load_dotenv()

try:
	from urllib import urlopen, quote
except ImportError:
	from urllib.request import urlopen
	from urllib.parse import quote


def get_kod():
    digits=random.sample('1234567890', 6)
    numbers=''.join(digits)
    return numbers


def ifs(cond, val1, val2):
	if cond:
		return val1
	return val2


class SMSC(object):

	def send_sms(self, phones, message, translit=0, time="", id=0, format=0, sender=False, query=""):
		formats=["flash=1", "push=1", "hlr=1", "bin=1", "bin=2", "ping=1", "mms=1", "mail=1", "call=1", "viber=1", "soc=1"]

		m=self._smsc_send_cmd("send", "cost=3&phones=" + quote(phones) + "&mes=" + quote(message) + \
					"&translit=" + str(translit) + "&id=" + str(id) + ifs(format > 0, "&" + formats[format-1], "") + \
					ifs(sender == False, "", "&sender=" + quote(str(sender))) + \
					ifs(time, "&time=" + quote(time), "") + ifs(query, "&" + query, ""))

		# (id, cnt, cost, balance) или (id, -error)

		if os.getenv('SMSC_DEBUG'):
			if m[1] > "0":
				print("Сообщение отправлено успешно. ID: " + m[0] + ", всего SMS: " + m[1] + ", стоимость: " + m[2] + ", баланс: " + m[3])
			else:
				print("Ошибка №" + m[1][1:] + ifs(m[0] > "0", ", ID: " + m[0], ""))

		return m


	def get_sms_cost(self, phones, message, translit=0, format=0, sender=False, query=""):
		formats=["flash=1", "push=1", "hlr=1", "bin=1", "bin=2", "ping=1", "mms=1", "mail=1", "call=1", "viber=1", "soc=1"]

		m=self._smsc_send_cmd("send", "cost=1&phones=" + quote(phones) + "&mes=" + quote(message) + \
					ifs(sender == False, "", "&sender=" + quote(str(sender))) + \
					"&translit=" + str(translit) + ifs(format > 0, "&" + formats[format-1], "") + ifs(query, "&" + query, ""))

		# (cost, cnt) или (0, -error)

		if os.getenv('SMSC_DEBUG'):
			if m[1] > "0":
				print("Стоимость рассылки: " + m[0] + ". Всего SMS: " + m[1])
			else:
				print("Ошибка №" + m[1][1:])

		return m

	def get_balance(self):
		m=self._smsc_send_cmd("balance") # (balance) или (0, -error)

		if os.getenv('SMSC_DEBUG'):
			if len(m) < 2:
				print("Сумма на счете: " + m[0])
			else:
				print("Ошибка №" + m[1][1:])

		return ifs(len(m) > 1, False, m[0])



	def _smsc_send_cmd(self, cmd, arg=""):
		url=ifs(os.getenv('SMSC_HTTPS'), "https", "http") + "://smsc.ru/sys/" + cmd + ".php"
		_url=url
		arg="login=" + quote(os.getenv('SMSC_LOGIN')) + "&psw=" + quote(os.getenv('SMSC_PASSWORD')) + "&fmt=1&charset=" + os.getenv('SMSC_CHARSET') + "&" + arg

		i=0
		ret=""

		while ret == "" and i <= 5:
			if i > 0:
				url=_url.replace("smsc.ru/", "www" + str(i) + ".smsc.ru/")
			else:
				i += 1

			try:
				if os.getenv('SMSC_POST') or len(arg) > 2000:
					data=urlopen(url, arg.encode(os.getenv('SMSC_CHARSET')))
				else:
					data=urlopen(url + "?" + arg)

				ret=str(data.read().decode(os.getenv('SMSC_CHARSET')))
			except:
				ret=""

			i += 1

		if ret == "":
			if os.getenv('SMSC_DEBUG'):
				print("Ошибка чтения адреса: " + url)
			ret="," # фиктивный ответ

		return ret.split(",")


# smsc=SMSC()
# print(f'\n\nКод: {get_kod()}\n\n')
# r=smsc.get_sms_cost('79021624272', get_kod())
# # print(f'Мой баланс: {smsc.get_balance()}')
# print(f'Стоимость смс сообщения: {r[0]}')
