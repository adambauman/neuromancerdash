#!/usr/bin/env python

from time import sleep
from sseclient import SSEClient

print("Connecting...")
messages = SSEClient("http://localhost:8080/sse")
print("Connected")


def extract_single_item_data(data):
	assert(None != data and 0 != len(data))

	# Data is initially combined with the gauge type like so: Simple1|cpu_util 6
	split_type_and_item_data = data.split("|")
	assert(2 == len(split_type_and_item_data))
	assert(-1 != split_type_and_item_data[0].find("Simple")) # Derp check that we setup AIDA64 fields correctly

	# Second index will contain the actual data which is space delimited
	split_item_data = split_type_and_item_data[1].split()
	assert(2 == len(split_item_data)) # Should be key, value
	assert(0 != len(split_item_data[0]) and 0 != len(split_item_data[1]))
	
	# Return key, value
	return split_item_data[0], split_item_data[1]


def parse_data(message_data):
	assert(None != message_data and 0 != len(message_data))

	if __debug__:
		print("Message data: " + message_data)

	split_message_data = message_data.split("{|}")
	assert(0 != len(split_message_data))

	# TODO: (Adam) 2020-11-14 Multi-page handling? Right now one page can fit a ton of data but it
	#		could be split into multiple pages to decrease the size of the stream packet.

	# First item should be the page name, process it seperatly
	page_name = split_message_data.pop(0)
	assert('|' == page_name[-1])
	assert(-1 != page_name.find("Page"))

	if __debug__:
		print("Page name: " + page_name)

	# The last item should be empty after the split, pop it
	last_item = split_message_data.pop(-1)
	assert(0 == len(last_item))

	parsed_datas = {}
	for data in split_message_data:
		key, value = extract_single_item_data(data)

		# Don't add incomplete data
		if 0 != len(key) and 0 != len(value):
			parsed_datas[key] = value
		else:
			assert(False)
			continue;

	return parsed_datas


for message in messages:
	
	# Example data response: 'Page0 | {|}Simple1|cpu_util 6 {|} Simple2|cpu_temp 32 {|}'
	# NOTE: (Adam) 2020-11-14 Message data isn't always in sync with the message? Continue looping
	#		if it wasn't receieved.
	if 0 == len(message.data) or None == message.data:
		continue

	parsed_datas = parse_data(message.data)

	if __debug__:
		print("CPU Temperature: " + parsed_datas.get("cpu_temp"))
		print("CPU Utilization: " + parsed_datas.get("cpu_util"))
