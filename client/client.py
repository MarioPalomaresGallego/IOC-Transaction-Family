#from sawtooth_signing import create_context
#from sawtooth_signing import CryptoFactory
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from hashlib import sha512
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
import requests

KEY_DIR = "/home/mario/.sawtooth/"
URL = "http://localhost:8008/batches"

signer = None

def obtain_keys():

	global signer

	try:
		with open(KEY_DIR + "mykey.priv") as fd:
			private_key_str = fd.read().strip()
	except OSError as err:
		raise XoException('Failed to read private key {}: {}'.format(keyfile, str(err))) from err
	try:
		private_key = Secp256k1PrivateKey.from_hex(private_key_str)
	except ParseError as e:
		raise XoException('Unable to load private key: {}'.format(str(e))) from e

	signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

def send_transaction(payload_bytes):

	global signer

	txn_header_bytes = TransactionHeader(
		family_name='ioc',
		family_version='1.0',
		inputs=[],
		outputs=[],
		signer_public_key=signer.get_public_key().as_hex(),
		batcher_public_key=signer.get_public_key().as_hex(),
		dependencies=[],
		payload_sha512=sha512(payload_bytes).hexdigest()
		nonce=hex(random.randint(0, 2**64))
	).SerializeToString()

	signature = signer.sign(txn_header_bytes)

	txn = Transaction(
		header=txn_header_bytes,
		header_signature=signature,
		payload=payload_bytes
	)

	txn_list_bytes = TransactionList(
		transactions=[txn1, txn2]
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
