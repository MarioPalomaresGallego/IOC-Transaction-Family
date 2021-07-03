import requests
import os
import json
import time
import hashlib

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

import logging

LOGGER = logging.getLogger(__name__)

IOC_NAMESPACE = hashlib.sha512('ioc'.encode("utf-8")).hexdigest()[0:6]
CAPE_UPLOAD_URL = "http://localhost:8000/apiv2/tasks/create/file/"
CAPE_STATUS_URL = "http://localhost:8000/apiv2/tasks/status/{0}/"
CAPE_REPORT_URL = "http://localhost:8000/apiv2/tasks/get/report/{0}/json/"

def make_address(addr):
	return IOC_NAMESPACE + addr

def compare_reports(user_report,cape_report):
	#TODO
	return True

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
		#return

		#Get the file hash to retrieve the complete program from the tmp folder
		user_report = json.loads(payload)
		file_name = user_report["target"]["file"]["sha256"]
		addr = make_address(file_name)
		state_dict = context.get_state([addr])
		LOGGER.debug("File hash: " + file_name)

		# Check whether the incoming behavioural report is a root one of just an
		# addition over a previous one

		#ADDITION
		if len(state_dict) > 0:

			LOGGER.info("Addition detected")
			context.set_state({addr:\
				state_dict[addr]+ "," + transaction.header_signature})

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
				if status == "analyzed" or status == "reported" or status=="completed":
					break
				elif status == "processing" or status=="running" or status=="pending":
					LOGGER.debug("CAPE task still ongoing. Waiting...")
					time.sleep(15)
				else:
					raise InternalError("CAPE processing error")

			#Check the report generated by CAPE
			r = requests.get(CAPE_REPORT_URL.format(task_id))
			if r.status_code != 200:
				raise InternalError("Error retrieving the report")
			cape_report = json.loads(r.text)

			LOGGER.debug("CAPE report retrieved. Starting comparison.")
			res = compare_reports(user_report,cape_report)

			#Update the global state if the transaction is valid
			if res:
				LOGGER.info("Reports comparison successful adding report to the blockchain")
				context.set_state({addr : transaction.signature.encode()})
			else:
				raise InvalidTransaction("Sample doesn't seem to be malware")


