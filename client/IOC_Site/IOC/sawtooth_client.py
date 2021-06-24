import hashlib
import random
from hashlib import sha512
import requests
import os

from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
import sawtooth_signing

from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing import create_context

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.propagate = False
LOGGER.setLevel(logging.DEBUG)
if not LOGGER.handlers:    
    LOGGER.addHandler(logging.StreamHandler())


IOC_NAMESPACE = hashlib.sha512('ioc'.encode("utf-8")).hexdigest()[0:6]
KEY_DIR = os.path.expanduser("~") + "/.sawtooth"

URL = "http://localhost:8008/batches"

signer = None

def make_address(payload_bytes):
	return IOC_NAMESPACE + hashlib.sha512(payload_bytes).hexdigest()[:64]

def generate_keys():
	
	global signer
	try:
		os.mkdir(KEY_DIR)
	except:
		pass
	
	context = sawtooth_signing.create_context("secp256k1")
	private_key = context.new_random_private_key()
	signer = CryptoFactory(context).new_signer(private_key)
	public_key = signer.get_public_key()

	with open(KEY_DIR + "mykey.priv") as file:
		file.write(private_key)
		
	with open(KEY_DIR + "mykey.pub") as file:
		file.write(public_key)

def obtain_keys():

	if len(os.listdir(KEY_DIR)) == 0:
		LOGGER.warn("Keys were deleted this could genreate some problems \
			it the network has a permissioned desing")
		LOGGER.info("Regenerating keys...")
		generate_keys()
	
	global signer

	try:
		with open(KEY_DIR + "mykey.priv") as fd:
			private_key_str = fd.read().strip()
	except OSError as err:
		raise Exception('Failed to read private key {}: {}'.format(KEY_DIR, str(err))) from err
	try:	
		private_key = Secp256k1PrivateKey.from_hex(private_key_str)
	except ParseError as e:
		raise Exception('Unable to load private key: {}'.format(str(e))) from e

	signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

def send_transaction(payload_bytes):

	global signer

	global_state_addr = make_address(payload_bytes)
	txn_header_bytes = TransactionHeader(
		family_name='ioc',
		family_version='1.0',
		inputs=[global_state_addr],
		outputs=[global_state_addr],
		signer_public_key=signer.get_public_key().as_hex(),
		batcher_public_key=signer.get_public_key().as_hex(),
		dependencies=[],
		payload_sha512=sha512(payload_bytes).hexdigest(),
		nonce=hex(random.randint(0, 2**64))
	).SerializeToString()

	signature = signer.sign(txn_header_bytes)

	txn = Transaction(
		header=txn_header_bytes,
		header_signature=signature,
		payload=payload_bytes
	)

	txn_list_bytes = TransactionList(
		transactions=[txn]
	).SerializeToString()

	txn_bytes = txn.SerializeToString()

	txns = [txn]

	batch_header_bytes = BatchHeader(
		signer_public_key=signer.get_public_key().as_hex(),
		transaction_ids=[txn.header_signature for txn in txns],
	).SerializeToString()

	signature = signer.sign(batch_header_bytes)

	batch = Batch(
		header=batch_header_bytes,
		header_signature=signature,
		transactions=txns
	)

	batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

	headers={'Content-Type': 'application/octet-stream'}

	result = requests.post(URL, headers=headers, data=payload_bytes)
	if(result.status_code != 200):
		print("Error sending the transaction")

	
