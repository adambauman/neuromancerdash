#!/usr/bin/env python

import sys, getopt

from sseclient import SSEClient

class AIDA64SSEData:

    # TODO: (Adam) 2020-11-14 Very simple static class right now, could definitely tighten things up, use
    #       user-specified callbacks to send out data, etc.

    @staticmethod
    def __extract_single_item_data__(data):
        assert(0 != len(data))

        # Data is initially combined with the gauge type like so: Simple1|cpu_util 6
        split_type_and_item_data = data.split("|")
        assert(2 == len(split_type_and_item_data))
        assert(-1 != split_type_and_item_data[0].find("Simple")) # Derp check that we setup AIDA64 fields correctly

        # Second index will contain the actual data which is space delimited
        split_item_data = split_type_and_item_data[1].split()

        item_value = ""
        if 2 < len(split_item_data):
            # Desktop resultion reporting is inconsistant. Sometimes it's split into width, "x", and height,
            # other times it's a single string, glom it together in case other fields do this as well.
            first_run = True
            for single_item_data in split_item_data:
                if first_run:
                    first_run = False
                    continue

                item_value += single_item_data
        else:
            # Should be key, value
            assert(2 == len(split_item_data))
            item_value = split_item_data[1]

        assert(0 != len(split_item_data[0]) and 0 !=len(item_value))

        # Return key, value
        return split_item_data[0], item_value

    @staticmethod
    def connect(server_address):
        assert(0 != len(server_address))

        print("Connecting to SSEClient \'" + server_address + "\'...")
        messages = SSEClient(server_address, timeout=1)
        print("Connected!")

        return messages

    @staticmethod
    def parse_data(message_data):
        assert(0 != len(message_data))

        #if __debug__:
            #print("Message data: " + message_data)

        split_message_data = message_data.split("{|}")
        assert(0 != len(split_message_data))

        # TODO: (Adam) 2020-11-14 Multi-page handling? Right now one page can fit a ton of data but it
        #       could be split into multiple pages to decrease the size of the stream packet.

        # First item should be the page name, process it seperatly
        page_name = split_message_data.pop(0)
        assert('|' == page_name[-1])
        assert(-1 != page_name.find("Page"))

        #if __debug__:
            #print("Page name: " + page_name)

        # The last item should be empty after the split, pop it
        last_item = split_message_data.pop(-1)
        assert(0 == len(last_item))

        parsed_datas = {}
        for data in split_message_data:
            try:
                key, value = AIDA64SSEData.__extract_single_item_data__(data)
            except:
                # Skip any fields that failed to parse
                if __debug__:
                    traceback.print_exc()

                assert(False)
                continue

            # Don't add incomplete data
            if 0 == len(key) or 0 == len(value):
                assert(False)
                continue

            parsed_datas[key] = value

        return parsed_datas


def print_usage():
    print("\nUsage: aida64_sse_data.py --server <full http address to sse stream>\n")


def get_command_args(argv):
    server_address = None
    try:
        opts, args = getopt.getopt(argv,"server:",["server="])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("--server"):
            server_address = arg

    if (None == server_address):
        print_usage()
        sys.exit()

    return server_address


def main(argv):
	server_address = get_command_args(argv)
	assert(None != server_address)

	# Example usage
	messages = AIDA64SSEData.connect(server_address)
	for message in messages:
	
		# Example data response: 'Page0 | {|}Simple1|cpu_util 6 {|} Simple2|cpu_temp 32 {|}'
		# NOTE: (Adam) 2020-11-14 Message data isn't always in sync with the message? Continue looping
		#		if it wasn't receieved.
		if 0 == len(message.data) or None == message.data:
			continue

		parsed_datas = AIDA64SSEData.parse_data(message.data)

		# Draw your dashboard, process the message data, etc. 
		for key in parsed_datas:
			print(key + ": " + parsed_datas[key])

		print("\n")

	
if __name__ == "__main__":
	main(sys.argv[1:])
	
