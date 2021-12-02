from enum import Enum
import csv


class DataTransmissionMode(Enum):
	ZENOH = "ZENOH"
	IMAGEZMQ = "IMAGEZMQ"


data_transmission_mode = frozenset([
	DataTransmissionMode.ZENOH.value,
	DataTransmissionMode.IMAGEZMQ.value,
])


def csv_writer(csv_file_path, header, data):
	# # open the file in the write mode
	with open(csv_file_path, 'w', encoding='UTF8', newline='') as f:
		# create the csv writer
		writer = csv.writer(f)

		# write the header
		writer.writerow(header)

		# write a row to the csv file
		writer.writerows(data)
