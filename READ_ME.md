# Timed Requests - Austin Weideman

timed_requests.py makes a GET request to ifconfig.co at the specified timestamps.
Requests are sent at the same time for identical timestamps.

timed_requests.py can take 2 different arguments for testing:

    1. --str times_str 
    
    where 'times_str' is a string of request times separated by commas.
    Eg. "09:15:25,11:58:23,13:45:09,13:45:09,13:45:09".

    2. --test n_tests range_seconds 

    where 'n_tests' = number of test times to randomly generate, and
    'range_seconds' = range of seconds after execution in which to generate times (>3 by default
    to allow time to generate tests). Eg. '--test 8 20' sends 8 requests at random times
    within 20 seconds of execution.
    Note: ifconfig.co will give code 429 (too many requests) with >6 requests in one second.

Execute the code:

`python3 timed_requests.py -h` for help.

`python3 timed_requests.py --str times_str` for user-inputted string of times.

`python3 timed_requests.py --test n_tests range_seconds` for automatically generated test times.

`python3 timed_requests.py --debug --str times_str` for verbose logs on string times.

`python3 timed_requests.py --debug --test n_tests range_seconds` for verbose logs on test times.

Review logs in console.

Note also:
For ease of execution, requests module (non-native) is used to bypass 403 error given to urllib
request where several user credentials are required to make successful request. So you may have to run:

`pip install requests`

before executing.