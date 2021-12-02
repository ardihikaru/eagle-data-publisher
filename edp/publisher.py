from edp.utils import DataTransmissionMode
from .model.zenoh import ZenohDataPublisher
from .model.imgzeromq import ImageZMQDataPublisher


class Publisher(object):
	def __init__(self, args):
		# initiate publisher object instance
		if args.tmode == DataTransmissionMode.ZENOH.value:
			self.pub = ZenohDataPublisher(args)

		elif args.tmode == DataTransmissionMode.IMAGEZMQ.value:
			self.pub = ImageZMQDataPublisher(args)

		else:
			self.pub = ZenohDataPublisher(args)

	def initialize(self):
		self.pub.initialize()

	def publish(self, itype, val):
		self.pub.publish(itype, val)

	def close(self):
		self.pub.close()
