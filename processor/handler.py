import requests
import os
import json
import time
import hashlib
import base64

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

import logging

LOGGER = logging.getLogger(__name__)

IOC_NAMESPACE = hashlib.sha512('ioc'.encode("utf-8")).hexdigest()[0:6]
CAPE_UPLOAD_URL = "http://localhost:8000/apiv2/tasks/create/file/"
CAPE_STATUS_URL = "http://localhost:8000/apiv2/tasks/status/{0}/"
CAPE_REPORT_URL = "http://localhost:8000/apiv2/tasks/get/report/{0}/json/"
SAWTOOTH_API = "http://localhost:8008/"

def make_address(addr):
	return IOC_NAMESPACE + addr

def compare_reports(user_report,compare_report):

	similarity_rate = []
	for k in user_report:

		if(len(user_report[k]) == 0 or len(compare_report[k]) == 0):
			LOGGER.debug("Ignoring field: " + k)
			continue
			
		r = compare_field(user_report[k],compare_report[k])
		LOGGER.debug("Comparison result of field: " + k + " = " + str(r))
		similarity_rate.append(r)

	if min(similarity_rate) > 0.8 : return True, similarity_rate
	else: return False, similarity_rate

def compare_field(user_field, compare_field):
	user_length = len(user_field)
	cape_length = len(compare_field)

	base = min(user_length,cape_length)

	match = 0
	for i in user_field:
		if i in user_field:
			match +=1

	return match/base


class IocTransactionHandler(TransactionHandler):

	@property
	def family_name(self):
		return 'ioc'

	@property
	def family_versions(self):
		return ['1.0']

	@property
	def namespaces(self):
		return [IOC_NAMESPACE]

	def apply(self, transaction, context):

		LOGGER.debug("Transaction recieved")
		payload = transaction.payload
		#LOGGER.debug("The end")

		#Get the file hash to retrieve the complete program from the tmp folder
		user_report = json.loads(payload)
		file_name = user_report["target"]["file"]["sha256"]
		addr = make_address(file_name)
		state_content = context.get_state([addr])
		LOGGER.debug("File hash: " + file_name)


		# Check whether the incoming behavioural report is a root one of just an
		# addition over a previous one

		#ADDITION
		if len(state_content) > 0:

			LOGGER.info("Addition detected")

			LOGGER.info("Checking if all the information is new")

			raw_content = state_content[0].data
			prev_transactions = raw_content.decode().split(",")
			for tx_id in prev_transactions:
				r = requests.get(SAWTOOTH_API + "transactions/" + tx_id)
				if r.status_code != 200:	
					raise InternalError("Unable to obtain previous transactions")
	
				raw_report = json.loads(r.text)["data"]["payload"]
				report = json.loads(base64.b64decode(raw_report))
				_, scores = compare_reports(user_report["behavior"],report["behavior"])

				if(max(scores) > 0):
					raise InvalidTransaction("Report Contains Duplicated Information")


		# ROOT BEHAVIOURAL REPORT
		else:

			LOGGER.info("Root behavioural report detected")


		if not os.path.exists("/tmp/" + file_name):
			raise InternalError("File not uploaded to the server")

		#Generate a CAPE task with the executable
		files = {'file': open('/tmp/' + file_name,'rb')}
		r = requests.post(CAPE_UPLOAD_URL, files=files)

		if r.status_code != 200:
			raise InternalError("Unable to generate CAPE task")
		
		r = json.loads(r.text)
		if r["error"] == True:
			raise InternalError("Unable to generate CAPE task: " + r["error_value"])

		LOGGER.debug("CAPE task generated succesfully")

		task_id = r["data"]["task_ids"][0]

		#POLL the CAPE API to track execution of the task
		while(True):
			r = requests.get(CAPE_STATUS_URL.format(task_id))
			if r.status_code != 200:
				raise InternalError("Error while polling CAPE task")
			status = json.loads(r.text)["data"]
			if status == "reported":
				break
			elif status in ["completed","processing","running","pending","analyzed"]:
				LOGGER.debug("CAPE task still ongoing. Waiting...")
				time.sleep(15)
			else:
				raise InternalError("CAPE processing error")

		#Check the report generated by CAPE

		r = requests.get(CAPE_REPORT_URL.format(task_id))
		if r.status_code != 200:
			raise InternalError("Error retrieving the report")
		cape_report = json.loads(r.text)

		LOGGER.debug("CAPE report retrieved.")


		#Update the global state if the transaction is valid
		if cape_report["malscore"] > 0:

			LOGGER.debug("Sandbox detected Malware. Comparing reports")
			res,_ = compare_reports(user_report["behavior"],cape_report["behavior"]["summary"])
			if res:
				
				LOGGER.info("Reports comparison successful adding report to the blockchain")
				if len(state_content) == 0:
					context.set_state({addr : transaction.signature.encode()})
				else:
					context.set_state({addr:\
					state_content[0].data + ",".encode() + transaction.signature.encode()})
			else:
				raise InvalidTransaction("Reports comparison does not satisfy the threshold")
		else:
			raise InvalidTransaction("Sample doesn't seem to be malware")


