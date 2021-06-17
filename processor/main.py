
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging
from processor import IocTransactionHandler

try:

	#init_console_logging(verbose_level=)
	processor = TransactionProcessor(url="tcp://127.0.0.1:4004")
	handler = IocTransactionHandler()
	processor.add_handler(handler)
	processor.start()

except KeyboardInterrupt:
	pass
except Exception as e:  # pylint: disable=broad-except
	print("Error: {}".format(e))
finally:
	if processor is not None:
		processor.stop()

