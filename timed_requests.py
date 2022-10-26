import argparse
import requests
import logging as log
import time
from multiprocessing import Pool
import datetime
from random import randrange
log.basicConfig(level=log.INFO)

API_URL = "http://ifconfig.co?"


def request_at_time(target_time):
    '''Retrieve current time and update until equal to target time.
    Make GET request at target time. Log status of request
    and return time of request.'''
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S:%f")

    if (target_time <= current_time):
        raise ValueError("Error: Target time must be after current time.")

    # Update current time to the starting decisecond (1/10 second)
    # of the next second to ensure accuracy when executed near the end
    # of a second or with long wait times. Sleeping in second intervals
    # would result in overflow into next second due to latency of processes.
    # sleep for (1-(digit in deciseconds place)/10)
    while current_time != target_time:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S:%f")
        sleep_time = 1 - int(current_time[9])/10
        time.sleep(sleep_time)
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

    response = requests.get(API_URL)
    # re-retrieve timestamp immediately after request to verify accuracy later
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    log.info("Request sent at {} with status code {}.".format(
        current_time, response.status_code))
    return (current_time)


def generate_test_times(n_tests, range_seconds):
    '''Return list of n randomly generated test times within
    range_seconds after execution.'''
    now = datetime.datetime.now()
    # create arbitrary seconds values to add to current time
    rand_seconds = []
    for i in range(n_tests):
        # allow 3 seconds after execution to generate test cases
        rand_num_seconds = randrange(3, range_seconds)
        rand_seconds.append(rand_num_seconds)
    rand_seconds.sort()

    test_times = []
    for i in range(len(rand_seconds)):
        new_time = now + datetime.timedelta(seconds=rand_seconds[i])
        new_time_str = new_time.strftime("%H:%M:%S")
        test_times.append(new_time_str)
    return test_times


def verify_results(send_times, target_times):
    '''Verify that send times match target times. Log missed requests if any.'''
    log.info("Send times: {}".format(send_times))
    if (send_times == target_times):
        log.info("Success.")
    else:
        log.info("Error.")
        missed_requests = []
        missed_requests_verbose = []
        for i in range(len(target_times)):
            if (target_times[i] != send_times[i]):
                missed_requests.append(target_times[i])
                missed_requests_verbose.append("Target: {}. Sent: {}.".format(
                    target_times[i], send_times[i]))
        log.info("Missed requests: {}".format(missed_requests))
        log.debug("Missed requests: {}".format(missed_requests_verbose))


def cmdargs():
    '''Process command line arguments.'''
    parser = argparse.ArgumentParser(
        description='Send GET requests to API at specified times.')

    parser.add_argument('--str', nargs=1, metavar='times_str', type=str,
                        help='Input string of request times separated by commas. \
                            Eg. 09:15:25,11:58:23,13:45:09,13:45:09,13:45:09')

    parser.add_argument('--test', nargs=2, metavar=('n_tests', 'range_seconds'),
                        help='Test on randomly generated request times. \
                            n_tests = number of test times to generate. \
                            range_seconds = range of seconds after execution \
                            in which to generate times (>2). Eg. "--test 10 20" \
                            sends 10 requests within 20 seconds of execution.')

    parser.add_argument('--debug', action='store_true',
                        help='Be verbose (DEBUG logging).')

    return parser.parse_args()


def main():
    '''Retrieve target times. Run concurrent instances of request_at_time
    for each target time, so that multiple requests can be sent at the
    same time. Log success if all send times match targets.'''
    args = cmdargs()
    if args.debug:
        log.getLogger().setLevel(log.DEBUG) 
    if args.str:
        times_str = args.str[0]
        target_times = times_str.split(',')
    elif args.test:
        target_times = generate_test_times(
            int(args.test[0]), int(args.test[1]))

    log.info("Target times: {}".format(target_times))
    print("Waiting...")

    num_processes = len(target_times)
    log.debug("Number of processes = {}".format(num_processes))
    with Pool(num_processes) as p:  # multiprocessing
        # distribute targets over num_processes concurrent processes
        # of request_at_time
        send_times = p.map(request_at_time, target_times)

    verify_results(send_times, target_times)
    return


if __name__ == "__main__":
    main()