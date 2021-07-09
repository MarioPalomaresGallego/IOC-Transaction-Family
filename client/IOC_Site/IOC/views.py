import hashlib
from django.http.response import HttpResponseServerError
from django.shortcuts import render
from django.http import HttpResponse
from IOC.models import Upload
import requests
import json
import time
import base64
from datetime import datetime

from .sawtooth_client import make_address, send_transaction

import logging
import math

LOGGER = logging.getLogger(__name__)
LOGGER.propagate = False
LOGGER.setLevel(logging.DEBUG)
if not LOGGER.handlers:    
    LOGGER.addHandler(logging.StreamHandler())

SAWTOOTH_API = "http://localhost:8008/"

RESULTS_PER_PAGE = 4

# Create your views here.
def index(request):
	
	r = requests.get(SAWTOOTH_API + "transactions")
	if r.status_code != 200:	
		return HttpResponseServerError()
	
	transactions = json.loads(r.text)["data"]

	report_list = []

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
		tx_id = tx["header_signature"]

		addr = make_address(1,sha256)
		r = requests.get(SAWTOOTH_API + "state/" + addr)

		if r.status_code!=200:
			_type = "Error"
		else:
			response = json.loads(r.text)
			data = base64.b64decode(response["data"]).decode().split(",")
			if data[0] == tx_id: _type="Root Behavioural Report"
			else: _type="Addition"

		info = {
			"md5" : md5,
			"sha1" : sha1,
			"sha256" : sha256,
			"date" : date,
			"machine" : machine,
			"sandbox" : sandbox,
			"tx_id" : tx_id,
			'type' : _type
		}

		report_list.append(info)

	context = {
		'report_list': report_list,
		'pages': range(0,math.ceil(count/RESULTS_PER_PAGE)),
		'uploads': Upload.objects.all()
	}
	return render(request,"index.html",context)

def upload(request):

	time.sleep(10)

	LOGGER.debug("hola")
	#Get all the nodes of the network in order to upload the message
	r = requests.get(SAWTOOTH_API + "peers")

	if(r.status_code !=200):
		return HttpResponseServerError()

	peers = json.loads(r.text)["data"]

	#Temporary trick to add the local machine to the peer list
	peers.append("tcp://localhost:8800")

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
	r = send_transaction(json.dumps(filtered_report).encode(),private_key,make_address(0,sample_raw))

	if r == -1: return HttpResponseServerError()
	else:
		#Save the upload information
		u = Upload(sample_name = request.FILES["sample"].name, report_name = request.FILES["report"].name,date = datetime.now(), batch_id=r)
		u.save()
		
	return HttpResponse(r)

def details(request):

	details_tx_id = request.GET.__getitem__("tx_id")
	sha256 = request.GET.__getitem__("sha256")
	
	addr = make_address(1,sha256)
	r = requests.get(SAWTOOTH_API + "state/" + addr)

	data = None
	if r.status_code!=200:
		return HttpResponseServerError()
	else:
		response = json.loads(r.text)
		data = base64.b64decode(response["data"]).decode().split(",")

	report_list = []
	background = None
	LOGGER.debug(data)
	for i,tx_id in enumerate(data):

		r = requests.get(SAWTOOTH_API + "transactions/" + tx_id)

		if r.status_code != 200:
			return HttpResponseServerError()

		tx = json.loads(r.text)
		report = json.loads(base64.b64decode(tx["data"]["payload"]))

		if(details_tx_id == tx_id): background = "rgb(170, 248, 193)"
		else: background = "white"

		report_list.append({
			"background":background,
			"margin" : range(i),
			"read_files": report["behavior"]["read_files"],
			"write_files": report["behavior"]["write_files"],
			"read_keys": report["behavior"]["read_keys"],
			"write_keys": report["behavior"]["write_keys"],
			"delete_keys": report["behavior"]["delete_keys"],
			"executed_commands": report["behavior"]["executed_commands"],
			"resolved_api": report["behavior"]["resolved_apis"],
			"created_services": report["behavior"]["created_services"],
			"started_services": report["behavior"]["started_services"],
		})
	context ={
		"reports" : report_list,
		"max":i
	}

	LOGGER.debug(context)

	return render(request,"details.html",context)

def req_block(request):

	block_id = request.GET.__getitem__("block_id")
	r = requests.get(SAWTOOTH_API + "blocks/" + block_id)
	if(r.status_code!=200): return HttpResponseServerError()

	return HttpResponse(r.text) 


def download(request):
	tx_id = request.GET.__getitem__("tx_id")

	r = requests.get(SAWTOOTH_API + "transactions/" + tx_id)

	if r.status_code != 200:
		return HttpResponseServerError()

	tx = json.loads(r.text)
	report = base64.b64decode(tx["data"]["payload"])

	return HttpResponse(report)


def _upload(request):
	pass
