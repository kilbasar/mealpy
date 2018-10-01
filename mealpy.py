import getpass
import json
import requests
from datetime import datetime
from time import sleep
import base64
import sys
from optparse import OptionParser

# E-mail and password can be hard-coded here, otherwise prompt for them
# Password should be base64 encoded, ie: base64.b64encode('password')
# This is not even slightly secure and you probably shouldn't use it!
MP_EMAIL = ''
MP_PASS = ''

cli_opts = None

BASE_DOMAIN = 'secure.mealpal.com'
BASE_URL = 'https://' + BASE_DOMAIN
LOGIN_URL = BASE_URL + '/1/login'
CITIES_URL = BASE_URL + '/1/functions/getCitiesWithNeighborhoods'
MENU_URL = BASE_URL + '/api/v1/cities/%s/product_offerings/lunch/menu'
RESERVATION_URL = BASE_URL + '/api/v2/reservations'
KITCHEN_URL = BASE_URL + '/1/functions/checkKitchen3'

LOGGED_IN_COOKIE = 'isLoggedIn'

HEADERS = {
    'Host': BASE_DOMAIN,
    'Origin': BASE_URL,
    'Referer': BASE_URL + '/login',
    'Content-Type': 'application/json',
}


def parse_opt(args=sys.argv[1:]):
    '''
    Parse the provided options, return an options object
    '''
    global cli_opts
    # Usage message
    usage = """%prog [options]
Script to make MealPal reservations
"""
    parser = OptionParser(usage=usage)
    # supported options
    parser.add_option("-r", "--restaurant", default=None, help="The name of the restaurant. This or meal name is required.")
    parser.add_option("-m", "--meal", default=None, help="The name of the meal. This or restaurnt name is required.")
    parser.add_option("-t", "--time", default="12:15pm-12:30pm", help="Reservation pickup time. Default is '12:15pm-12:30pm'")
    parser.add_option("-s", "--sleep", default="00", help="Sleep until this clock minute. Default is 00")
    parser.add_option("-c", "--city", default="New York City", help="City name. Default is New York City.")
    parser.add_option("-d", "--dump", action="store_true", default=False, help="Dump the schedule to a JSON file")
    (options, args) = parser.parse_args(args)
    if not options.restaurant and not options.meal:
        print "One of --restaurant or --meal is required"
        parser.print_help()
        sys.exit(5)
    cli_opts = options


class MealPal(object):

    def __init__(self):
        self.headers = HEADERS
        self.cookies = None
        self.cities = None
        self.schedules = None

    def login(self, username, password):
        data = {'username': username, 'password': password}
        r = requests.post(
            LOGIN_URL, data=json.dumps(data), headers=self.headers)
        self.cookies = r.cookies
        self.cookies.set(LOGGED_IN_COOKIE, 'true', domain=BASE_URL)
        return r.status_code

    def get_cities(self):
        if not self.cities:
            r = requests.post(CITIES_URL, headers=self.headers)
            self.cities = r.json()['result']
        return self.cities

    def get_city(self, city_name):
        if not self.cities:
            self.get_cities()
        return filter(lambda x: x['name'] == city_name, self.cities)[0]

    def get_schedules(self, city_name, city_id=None):
        if not city_id:
            city_id = self.get_city(city_name)['objectId']
        r = requests.get(
            MENU_URL % city_id, headers=self.headers, cookies=self.cookies)
        self.schedules = r.json()['schedules']
        # Write schedule to file if --dump
        if cli_opts.dump:
            dt_now = datetime.now()
            y, m, d = dt_now.year, dt_now.month, dt_now.day
            sched_filename = "schedules_{y}_{m}_{d}.json".format(y=y,m=m,d=d)
            print("Writing schedules to " + sched_filename)
            with open(sched_filename, 'w') as sched_file:
                json.dump(self.schedules, sched_file)
        return self.schedules

    def get_schedule_by_restaurant_name(
            self, restaurant_name, city_name=None, city_id=None):
        if not self.schedules:
            self.get_schedules(city_name, city_id)
        return filter(lambda x: x['restaurant']['name'] == restaurant_name,
                      self.schedules)[0]

    def get_schedule_by_meal_name(
            self, meal_name, city_name=None, city_id=None):
        if not self.schedules:
            self.get_schedules(city_name, city_id)
        return filter(lambda x: x['meal']['name'] == meal_name,
                      self.schedules)[0]

    def reserve_meal(
            self, timing, restaurant_name=None, meal_name=None, city_name=None,
            city_id=None, cancel_current_meal=False):
        assert restaurant_name or meal_name
        if cancel_current_meal:
            self.cancel_current_meal()

        if meal_name:
            try:
                schedule_id = self.get_schedule_by_meal_name(
                    meal_name, city_name, city_id)['id']
            except IndexError:
                schedule_id = None
        else:
            try:
                schedule_id = self.get_schedule_by_restaurant_name(
                    restaurant_name, city_name, city_id)['id']
            except IndexError:
                schedule_id = None

        if not schedule_id:
            print("Error, could not find a schedule for this meal or restaurant. Check your spelling?")
            sys.exit(7)

        reserve_data = {
            'quantity': 1,
            'schedule_id': schedule_id,
            'pickup_time': timing,
            'source': 'Web'
        }

        # return 200
        r = requests.post(
            RESERVATION_URL, data=json.dumps(reserve_data),
            headers=self.headers, cookies=self.cookies)
        return r.status_code

    def get_current_meal(self):
        r = requests.post(
            KITCHEN_URL, headers=self.headers, cookies=self.cookies)
        return r.json()

    def cancel_current_meal(self):
        pass


def execute_reserve_meal(email, password):
    mp = MealPal()

    # Try to login
    status_code = mp.login(email, password)
    if status_code == 200:
        print('Successful login to MealPal')
    else:
        print('Failed to login to MealPal. Check user/pass and try again.')
        sys.exit(6)

    # Sleep until the correct time
    sleep_minute = int(cli_opts.sleep)
    now_minute = datetime.now().minute
    print('Sleeping until minute {s}, current minute is {n}...'.format(s=sleep_minute, n=now_minute))
    while now_minute != sleep_minute:
        sleep(0.01)
        now_minute = datetime.now().minute
    print('Waking up to make reservation...')

    # Try to reserve meal
    count = 0
    while count <= 5:
        try:
            status_code = mp.reserve_meal(
                cli_opts.time,
                restaurant_name=cli_opts.restaurant,
                meal_name=cli_opts.meal,
                city_name=cli_opts.city)
            if status_code == 200:
                print('Reservation success!')
                sys.exit(0)
        except IndexError:
            pass
        print('Reservation error, retry #{n}/5!'.format(n=count))
        count += 1
        sleep(0.1)


def main(args):
    # Parse the options/arguments from the CLI, store them in cli_opts
    parse_opt(args)
    # Do we need a user/pass?
    if not MP_EMAIL or not MP_PASS:
        print "Enter email: "
        email = raw_input()
        print "Enter password: "
        password = getpass.getpass()
    else:
        email = MP_EMAIL
        password = base64.b64decode(MP_PASS)
    # Start our meal reservation
    execute_reserve_meal(email, password)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main(sys.argv[1:])
