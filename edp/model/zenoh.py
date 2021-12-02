from eagle_zenoh.zenoh_lib.zenoh_net_publisher import ZenohNetPublisher


class ZenohDataPublisher(object):
	def __init__(self, args):
		self.args = args
		self.peer = args.peer
		if self.peer is not None:
			self.peer = ",".join(args.peer)

		self.path = None
		self.z_svc = None
		self.z_pub = None
		self.pub = None

	def initialize(self):
		# configure zenoh service
		self.path = self.args.path
		self.z_svc = ZenohNetPublisher(
			_path=self.path, _session_type="PUBLISHER", _peer=self.peer
		)
		self.z_svc.init_connection()

		# register and collect publisher object
		self.z_svc.register()
		self.z_pub = self.z_svc.get_publisher()

	def publish(self, itype, val):
		# publish data
		self.z_svc.publish(
			_val=val,
			_itype=itype,
		)

	def close(self):
		# closing Zenoh publisher & session
		self.z_svc.close_connection(self.z_pub)
