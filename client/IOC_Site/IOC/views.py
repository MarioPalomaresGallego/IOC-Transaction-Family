import hashlib
from django.http.response import HttpResponseServerError
from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
import time
import base64

from .sawtooth_client import make_address, send_transaction

import logging
import math

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
		return HttpResponseServerError()
	
	transactions = json.loads(r.text)["data"]

	report_list_visible = []
	report_list_hidden = []

	count = 0
	for tx in transactions:

		if(tx["header"]["family_name"] != "ioc"): continue

		count +=1

		encoded_report = tx["payload"]
		try:
			report = json.loads(base64.b64decode(encoded_report))
		except:
			continue

		md5 = report["target"]["file"]["md5"]
		sha1 = report["target"]["file"]["sha1"]
		sha256 = report["target"]["file"]["sha256"]
		machine = "Windows 7"
		date = report["info"]["started"]
		sandbox = report["info"]["version"]

		info = {
			"md5" : md5,
			"sha1" : sha1,
			"sha256" : sha256,
			"date" : date,
			"machine" : machine,
			"sandbox" : sandbox,
			"tx_id" : tx["header_signature"],
			# Make a request to the global state to check wether this transaction
			# is a root behavioural report or not
			'type' : "Root Behavioural Report"
		}

		if count > 5: report_list_hidden.append(info)
		else: report_list_visible.append(info)

	context = {
		'report_list_visible': report_list_visible,
		'report_list_hidden': report_list_hidden,
		'pages': range(1,math.ceil(count/5)+1)
	}
	return render(request,"index.html",context)

def upload(request):

	time.sleep(1)

	#Get all the nodes of the network in order to upload the message
	r = requests.get(SAWTOOTH_API + "peers")

	if(r.status_code !=200):
		return HttpResponseServerError()

	peers = json.loads(r.text)["data"]

	#Function to read the file from the request
	def read_file(file):
		result = b''
		if file.multiple_chunks:
			for chunk in file.chunks():
				result += chunk
		else: result = sample.read()

		return result

	sample = request.FILES["sample"]
	sample_raw = read_file(sample)
	LOGGER.debug("Sample hash: " + hashlib.sha256(sample_raw).hexdigest())

	aux = []
	for p in peers:

		#A peer can be dupplicated in the Sawtooth API response
		if p not in aux:

			addr = p.replace("tcp","http").replace("8800","8080")
			LOGGER.debug("Sending sample to: " + addr)
			r = requests.post(addr, data=sample_raw)
			if r.status_code != 200:	
				return HttpResponseServerError()

			aux.append(p)

	
	report = request.FILES["report"]
	report_raw = read_file(report)
	report = json.loads(report_raw)

	filtered_report = {
		"target" : report["target"],
		"info" : report["info"],
		"behavior" : report["behavior"]["summary"]
	}
	private_key = request.POST["privkey"]
	LOGGER.debug("Private key: " + private_key)
	send_transaction(json.dumps(filtered_report).encode(),private_key,make_address(sample_raw))

	
	return HttpResponse()


def details(request):

	tx_id = request.GET.__getitem__("tx_id")
	r = requests.get(SAWTOOTH_API + "transactions/" + tx_id)

	if r.status_code != 200:
		return HttpResponseServerError()

	tx = json.loads(r.text)

	report = json.loads(base64.b64decode(tx["data"]["payload"]))

	context = {
		"read_files": report["behavior"]["read_files"],
		"write_files": report["behavior"]["write_files"],
		"read_keys": report["behavior"]["read_keys"],
		"write_keys": report["behavior"]["write_keys"],
		"delete_keys": report["behavior"]["delete_keys"],
		"executed_commands": report["behavior"]["executed_commands"],
		"resolved_api": report["behavior"]["resolved_apis"],
		"created_services": report["behavior"]["created_services"],
		"started_services": report["behavior"]["started_services"],
	}

	return render(request,"details.html",context)

def req_block(request):

	block_id = request.GET.__getitem__("block_id")
	r = requests.get(SAWTOOTH_API + "blocks/" + block_id)
	if(r.status_code!=200): return HttpResponseServerError()

	return HttpResponse(r.text) 

