import cv2
import time
import imagezmq
import logging
from datetime import datetime
import uuid

###

L = logging.getLogger(__name__)


###


class ImageZMQDataPublisher(object):
	def __init__(self, args):
		self.path = args.peer  # path to target the listened IP

		# Encoding parameter
		self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(args.quality)]  # The default value is 95

		self.image_hub = None
		self.sender = None

	def initialize(self):
		# peer value is stored as an array, e.g. `['tcp://*:5548']`
		#  so it will be converted into a string first
		uri = self.path[0]

		# Setup ZMQ Sender
		L.warning("ImageZMQ is listening to: {}".format(uri))
		self.sender = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)

	def publish(self, itype, val):
		self.sender.send_image(str(uuid.uuid4()), val)

	def close(self):
		# NOTHING TO DO HERE
		pass
