
# import time
# from datetime import datetime

path = "/home/dtm-project/consumer_dump.txt"
# while True:
#     with open(path, "a") as f:
#         f.write("The current timestamp is: " + str(datetime.now()) + "\n")
#         f.close()
#     time.sleep(10)


import sys
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
from argparse import ArgumentParser, FileType
# import getting_started

# if __name__ == '__main__':
# while True:  
# Parse the command line.
parser = ArgumentParser()
# parser.add_argument('config_file', type=FileType('r'))
parser.add_argument('--reset', action='store_true')
# parser.add_argument('output_file', type=str, help='The file to save incoming records')
args = parser.parse_args()

# Parse the configuration.
config_parser = ConfigParser()
with open("./getting_started.ini", "r") as config_file:

    # config_parser.read_file(args.config_file)
    config_parser.read_file(config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['consumer'])

# Create Consumer instance
consumer = Consumer(config)

# Set up a callback to handle the '--reset' flag.
def reset_offset(consumer, partitions):
    if args.reset:
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)

# Subscribe to topic
topic = "breadcrumbs_readings"
consumer.subscribe([topic], on_assign=reset_offset)

# Open the output file for writing.
# with open(args.output_file, 'w') as output_file:
with open(path, 'w') as output_file:

    # Poll for new messages from Kafka and write them to the file.
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                key = msg.key().decode('utf-8') if msg.key() is not None else None
                value = msg.value().decode('utf-8') if msg.value() is not None else None

                print("Consumed event from topic {topic}: key = {key} value = {value}".format(
                topic=msg.topic(), key=key if key is not None else 'None', value=value if value is not None else 'None'))

                output_file.write(f"{value}\n")
    except KeyboardInterrupt:
        output_file.close() 
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()