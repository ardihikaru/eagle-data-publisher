# cp bandwidth_usage.csv ~/Documents/PAPER_DDP/bandwidth_usage_Q=32.csv
# cp mbits_per_second.csv ~/Documents/PAPER_DDP/mbits_per_second_Q=32.csv
# Import PYTHONPATH first
import sys
import os
from dotenv import load_dotenv, find_dotenv
# load `.env` file first!
load_dotenv(find_dotenv())
PYTHONPATH = os.getenv("PYTHONPATH")  # load PYTHONPATH
# add to PYTHONPATH only if the provided folder exist
if os.path.isdir(PYTHONPATH):
	sys.path.append(PYTHONPATH)

import sys
import time
from datetime import datetime
import numpy as np
import cv2
import simplejson as json
import logging
import argparse
# from hurry.filesize import size as fsizeb
from eagle_zenoh.extras.functions import humanbytes as fsize
from eagle_zenoh.zenoh_lib.functions import encrypt_str, get_img_fsize_in_float
import os
from edp.utils import data_transmission_mode, csv_writer
from edp.publisher import Publisher
import requests

# PATH TO Save CSV File
CSV_FILE_PATH = "./bandwidth_usage.csv"
CSV_FILE_PATH_MBITS = "./mbits_per_second.csv"

# FullHD Format; fixed value, as per required in 5G-DIVE Project
FULLHD_WIDTH = 1920
FULLHD_HEIGHT = 1080

# --- [START] Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
	description='Zenoh Publisher example')
# Note: ImageZMQ and other publisher will use this argument as the URL Path
# e.g. for ImageZMQ, peer=`tcp://*:5548`
parser.add_argument('--peer', '-e', dest='peer',  # e.g. `-e tcp/192.168.1.10:7446` (to LittleBoy)
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Peer locators used to initiate the zenoh session.')
parser.add_argument('--path', '-p', dest='path',
                    default='/eagle/svc/zenoh-python-pub',
                    type=str,
                    help='The name of the resource to publish.')
parser.add_argument('--video', '-v', dest='video',
                    default="0",
                    type=str,
                    help='The name of the resource to publish.')
parser.add_argument('--pwidth', '-w', dest='pwidth', default=1280, type=int, help='Target width to publish')
parser.add_argument('--pheight', '-t', dest='pheight', default=720, type=int, help='Target height to publish')
# parser.add_argument('--pwidth', dest='pwidth', default=640, type=int, help='Target width to publish')
# parser.add_argument('--pheight', dest='pheight', default=480, type=int, help='Target height to publish')
parser.add_argument('--droneid', '-d', dest='droneid', default="1", type=str, help='Drone ID')
parser.add_argument('--cvout', dest='cvout', action='store_true', help="Use CV Out")
parser.add_argument('--resize', dest='resize', action='store_true', help="Force resize to FullHD")
parser.set_defaults(cvout=False)
parser.set_defaults(resize=False)
# default
parser.add_argument('--maxframe', dest='maxframe', default=9999999999, type=int, help='Target max frame to publish')
parser.add_argument('--quality', '-q', dest='quality', default=70, type=int, help='Encoding quality')
parser.add_argument('--tmode', dest='tmode', default="ZENOH", type=str, help='Data transmission mode')

# optional arguments
# these args are important params for Dynamic Data Publisher project
parser.add_argument('--puburl', '-u', dest='puburl', default="http://localhost:8888/api", type=str, help='Publisher URL')
parser.add_argument('--autoupdate', dest='autoupdate', action='store_true', help="Enable updating publisher last update")
parser.set_defaults(autoupdate=False)

args = parser.parse_args()
print(args)
# --- [END] Command line argument parsing --- --- --- --- --- ---

###

L = logging.getLogger(__name__)


###

def validate_transmission_mode(tmode):
	if tmode not in data_transmission_mode:
		return False

	return True


def auto_update_pub_status(root_api="http://localhost:8888/api"):
	try:
		post_uri = root_api + "/publisher"

		now = datetime.now()  # current date and time
		payload = {
			"last_update": now.strftime("%Y-%m-%d %H:%M:%S")
		}

		# defining a params dict for the parameters to be sent to the API
		headers = {"Content-Type": "application/json"}

		# sending get request and saving the response as response object
		req = requests.post(url=post_uri, json=payload, headers=headers)

		# extracting data in json format
		resp = req.json()

	except Exception as err:
		L.warning("[auto_update_pub_status] Sending to API `{}` Failed: {}".format(root_api, err))


# Encoding parameter
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), args.quality]  # The default value for IMWRITE_JPEG_QUALITY is 95

# validate data tranmission mode
if not validate_transmission_mode(args.tmode):
	L.error("Invalid data transmission mode (={})".format(args.tmode))
	exit(0)

# build publisher instance
publisher = Publisher(args)

video_path = args.video
if video_path == "0":
	video_path = int(video_path)

# Enable / disable cvout
_enable_cv_out = args.cvout

# Initialize publisher configuration setup
try:
	publisher.initialize()
except AttributeError as err:
	L.error("Unable to configure Zenoh publisher. Exiting ...")
	exit(0)

window_title = "img-data-publisher"

published_height, published_weight = args.pheight, args.pwidth  # target width and height
cam_weight, cam_height = None, None  # default detected width and height

cap = cv2.VideoCapture(video_path)

# Source: https://stackoverflow.com/questions/61202978/how-to-explicitly-access-mjpeg-backend-for-videocapture-in-opencv
# availableBackends = [cv2.videoio_registry.getBackendName(b) for b in cv2.videoio_registry.getBackends()]
# print(availableBackends)
#
# print('cv2.CAP_OPENCV_MJPEG = ' + str(cv2.CAP_OPENCV_MJPEG))

# change the image property
# use `$ v4l2-ctl --list-formats-ext` to check the available format!
# install first (if not yet): `$ sudo apt install v4l-utils`
cap.set(cv2.CAP_PROP_FRAME_WIDTH, published_weight)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, published_height)

if _enable_cv_out:
	cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
	# cv2.resizeWindow("Image", 1920, 1080)  # Enter your size
	cv2.resizeWindow(window_title, 800, 550)  # Enter your size
_frame_id = 0

# Extra information (to be tagged into the frame)
int_drone_id = encrypt_str(args.droneid)  # contains 1 extra slot
extra_len = 8  # contains 1 extra slot; another one slot is from `tagged_data_len` variable

# create an empty array
bw_usage_header = ['FrameID', 'Uncompressed', 'Compressed_Mbytes', 'Compressed_Mbits_q={}'.format(args.quality)]
bw_usage = []

mbits_per_sec_header = ['Time_t', 'FPS', 'AVG_Mbits_per_second_q={}'.format(args.quality),
						'SUM_Mbits_per_second_q={}'.format(args.quality)]
mbits_per_sec = []

try:
	tmp_mbits = 0  # will reset after modulus
	time_t = 1  # start from time-t = 1
	total_frames = 1
	while cap.isOpened():
		_frame_id += 1

		# generate encrypted frame_id
		eframe_id = encrypt_str(str(_frame_id))

		# ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
		try:
			ret, frame = cap.read()

			# do it ONCE
			# detect width and height
			if cam_weight is None:
				cam_height, cam_weight, _ = frame.shape

			img_size, ext = get_img_fsize_in_float(frame.nbytes)
			L.warning("[frame-{}] ## Image Size: {} {}".format(_frame_id, img_size, ext))
			# print(" ## Image Size Bytes:", fsizeb(frame.nbytes))
			L.warning("[frame-{}] ## Initial image SHAPE: {}".format(_frame_id, frame.shape))

			t0_decoding = time.time()
			# resize the frame; Default VGA (640 x 480) for Laptop camera
			t0_img_resizer = time.time()
			if cam_weight != FULLHD_WIDTH and args.resize:
				frame = cv2.resize(frame, (FULLHD_WIDTH, FULLHD_HEIGHT))
			t1_img_resizer = (time.time() - t0_img_resizer) * 1000
			t1_img_resizer = round(t1_img_resizer, 3)
			L.warning(('[frame-{}][%s] Latency Image Resizing to FullHD (%.3f ms) '.format(_frame_id) % (
				datetime.now().strftime("%H:%M:%S"), t1_img_resizer)))

			L.warning("[frame-{}] ## Final image SHAPE: {}".format(_frame_id, frame.shape))
			# compress image
			# NEW encoding method
			encoder_format = None  # disable custom encoder
			itype = 4  # new type specially for compressed image
			t0_img_compression = time.time()
			_, compressed_img = cv2.imencode('.jpg', frame, encode_param)
			compressed_img_len, _ = compressed_img.shape
			t1_img_compression = (time.time() - t0_img_compression) * 1000
			t1_img_compression = round(t1_img_compression, 3)
			L.warning(('[frame-{}][%s] Latency Image Compression (%.3f ms) '.format(_frame_id) % (
				datetime.now().strftime("%H:%M:%S"), t1_img_compression)))
			tagged_data_len = compressed_img_len + extra_len  # `tagged_data_len` itself contains 1 extra slot

			# create t0
			t0_array = str(time.time()).split(".")  # contains 2 extra slots

			# generate img compression latency
			img_compr_lat_arr = str(t1_img_compression).split(".")  # contains 2 extra slots

			# generate encrypted frame_id
			eframe_id = encrypt_str(str(_frame_id))

			# vertically tag this frame with an extra inforamtion
			t0_tag_extraction = time.time()
			tagged_info = [
				[int_drone_id],
				[int(t0_array[0])],
				[int(t0_array[1])],
				[eframe_id],
				[int(img_compr_lat_arr[0])],
				[int(img_compr_lat_arr[1])],
				[extra_len],
				[tagged_data_len],
			]
			val = np.vstack([compressed_img, tagged_info])
			t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
			L.warning(('[frame-{}][%s] Latency Image Taging (%.3f ms) '.format(_frame_id) % (datetime.now().strftime("%H:%M:%S"), t1_tag_extraction)))

			img_size_compressed, ext = get_img_fsize_in_float(val.nbytes)
			# FYI: 1 MB = 8 Mbit
			img_size_compressed = round(img_size_compressed, 2)
			img_size_compressed_mbit = round((img_size_compressed * 8), 2)
			L.warning("[frame-{}] ## Image Size COMPRESSED + TAGGED: {} {} ({} Mbits)".format(_frame_id, img_size_compressed, ext, img_size_compressed_mbit))
			bw_usage.append([_frame_id, img_size, img_size_compressed, img_size_compressed_mbit])

			# accumulate and append Mbits
			if _frame_id % 30 == 0:
				avg_mbits = round((tmp_mbits / 30), 2)
				mbits_per_sec.append([time_t, total_frames, avg_mbits, tmp_mbits])
				time_t += 1
				tmp_mbits = 0  # reset to Zero again
				total_frames = 1  # reset to One again
			else:
				tmp_mbits += img_size_compressed_mbit
				tmp_mbits = round(tmp_mbits, 2)
				total_frames += 1

			# publish data
			publisher.publish(itype, val)

			# update
			if args.autoupdate:
				auto_update_pub_status(args.puburl)

			if _enable_cv_out:
				cv2.imshow(window_title, frame)
			print()

			if _frame_id == args.maxframe:
				L.warning("[STOPPED by MAX_FRAME] Start storing CSV Files")
				# if file exist, delete it first!
				if os.path.isfile(CSV_FILE_PATH):
					os.remove(CSV_FILE_PATH)
				if os.path.isfile(CSV_FILE_PATH_MBITS):
					os.remove(CSV_FILE_PATH_MBITS)

				# special case, if frame extraction is stopped before mod 30, summary any accumulated data
				if _frame_id % 30 != 0:
					avg_mbits = round((tmp_mbits / 30), 2)
					mbits_per_sec.append([time_t, total_frames, avg_mbits, tmp_mbits])

				# write to csv file: bandwidth usage
				csv_writer(CSV_FILE_PATH, bw_usage_header, bw_usage)

				# write to csv file: mbits per seconds
				csv_writer(CSV_FILE_PATH_MBITS, mbits_per_sec_header, mbits_per_sec)
				exit(0)

		except Exception as e:
			print("No more frame to show: `{}`".format(e))
			break

		if _enable_cv_out:
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

# when stopped, start saving the CSV files
except KeyboardInterrupt:
	L.warning("[STOPPING] Start storing CSV Files")
	# if file exist, delete it first!
	if os.path.isfile(CSV_FILE_PATH):
		os.remove(CSV_FILE_PATH)

	# write to csv file: bandwidth usage
	csv_writer(CSV_FILE_PATH, bw_usage_header, bw_usage)

	# write to csv file: mbits per seconds
	csv_writer(CSV_FILE_PATH_MBITS, mbits_per_sec_header, mbits_per_sec)

if _enable_cv_out:
	# The following frees up resources and closes all windows
	cap.release()
	cv2.destroyAllWindows()
#########################

# closing publisher
publisher.close()
