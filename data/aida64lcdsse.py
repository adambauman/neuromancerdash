#
# aida64lcdsse - Connects to an AIDA64 LCD SSE stream and extracts the field data
# ===============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import sys, getopt
from time import sleep

from sseclient import SSEClient

if __debug__:
    import traceback

class AIDA64LCDSSE:

    # TODO: (Adam) 2020-11-14 Very simple static class right now, could definitely tighten things up, use
    #       user-specified callbacks to send out data, etc.

    @classmethod
    def __extract_single_item_data__(class_object, data):
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

    #@staticmethod
    #def connect(aida_sse_server_address):
    #    assert(0 != len(aida_sse_server_address))

    #    print("Connecting to SSEClient \'" + aida_sse_server_address + "\'...")
    #    messages = SSEClient(aida_sse_server_address, timeout=2.0)
    #    print("Connected!")

    #    return messages

    @classmethod
    def __parse_data__(class_object, message_data):
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
                key, value = class_object.__extract_single_item_data__(data)
            except:
                # Skip any fields that failed to parse
                if __debug__:
                    print("Extract single item data failed: {}".format(data))
                    #traceback.print_exc()
                    #assert(False)

                continue

            # Don't add incomplete data
            if 0 == len(key) or 0 == len(value):
                assert(False)
                continue

            parsed_datas[key] = value

        return parsed_datas

    @classmethod
    def threadable_stream_read(class_object, data_queue, aida64_lcd_sse_address):
        assert(None != data_queue)
        assert(None != aida64_lcd_sse_address and 0 != len(aida64_lcd_sse_address))

        retry_attempts = 0
        while True:
            try:
                if __debug__:
                    print("Making SSE AIDA64 connection...")

                server_messages = SSEClient(aida64_lcd_sse_address, timeout=1.0)

                if __debug__:
                    print("Connection successful!")

                retry_attempts = 0
                for server_message in server_messages:
                    if None == server_message.data or 0 == len(server_message.data):
                        continue

                    if "reload" == server_message.data.lower():
                        if __debug__:
                            print("Encountered reload message")
                        continue

                    parsed_data = class_object.__parse_data__(server_message.data)
                    assert(0 != len(parsed_data))

                    data_queue.append(parsed_data)
            except:
                if __debug__:
                    print("Stream read excepted, will restart connection in two seconds...")
                    traceback.print_exc()

                # Back off retries after a few quick attempts
                if 50 < retry_attempts:
                    sleep(10)
                else:
                    sleep(0.1)



def print_usage():
    print("")
    print("Usage: aida64_lcd_sse.py --server <full http address:port to aida64 lcd sse stream>")
    print("Example: aida64_lcd_sse --server http://localhost:8080/sse")

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
    messages = AIDA64LCDSSE.connect(server_address)
    for message in messages:

        # Example data response: 'Page0 | {|}Simple1|cpu_util 6 {|} Simple2|cpu_temp 32 {|}'
        # NOTE: (Adam) 2020-11-14 Message data isn't always in sync with the message? Continue looping
        #       if it wasn't receieved.
        if 0 == len(message.data) or None == message.data:
            continue

        parsed_datas = AIDA64LCDSSE.parse_data(message.data)

        # Draw your dashboard, process the message data, etc. 
        for key in parsed_datas:
                print(key + ": " + parsed_datas[key])

        print("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
