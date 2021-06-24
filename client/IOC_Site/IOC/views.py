from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
import time

from .sawtooth_client import generate_keys,obtain_keys, send_transaction

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.propagate = False
LOGGER.setLevel(logging.DEBUG)
if not LOGGER.handlers:    
    LOGGER.addHandler(logging.StreamHandler())

SAWTOOTH_API = "http://localhost:8008/"

# Create your views here.
def index(request):
	
	r = requests.get(SAWTOOTH_API + "transactions")
	if r.status_code != 200:	
		HttpResponse("Ops something went wrong")
	
	transactions = json.loads(r.text)["data"]

	report_list = []
	for tx in transactions:

		LOGGER.debug(tx["header"]["family_name"])
		if(tx["header"]["family_name"] != "ioc"): continue

		encoded_report = tx["payload"]
		report = json.loads(encoded_report)
		sha1 = report["CAPE"]["payloads"]["sha1"]
		sha256 = report["CAPE"]["payloads"]["sha256"]
		sha512 = report["CAPE"]["payloads"]["sha512"]
		machine = "Windows 7"
		date = report["info"]["Started"]
		sandbox = report["info"]["version"]

		info = {
			"sha1" : sha1,
			"sha256" : sha256,
			"sha512" : sha512,
			"date" : date,
			"machine" : machine,
			"sandbox" : sandbox,
			"tx_id" : tx["header_signature"],
			# Make a request to the global state to check wether this transaction
			# is a root behavioural report or not
			'type' : "Root Behavioural Report"
		}
		report_list.append(info)

	context = {
		'report_list': report_list
	}
	return render(request,"index.html",context)

def details(request):
	return HttpResponse("Hello, world. You're at the IOC submit")

def upload(request):
	time.sleep(3)
	LOGGER.debug("No estoy esperando na de na")
	return HttpResponse("Hello, world. You're at the IOC submit")
