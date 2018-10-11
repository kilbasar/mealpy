# mealpy 
Reserve your meals on MealPal automatically, as soon as the kitchen opens.
Never miss your favourite MealPal meals again!

## Description
*[MealPal](https://www.mealpal.com/edmundmok) offers lunch and dinner subscriptions giving you access to the best restaurants for less than $6 per meal.*

This script automates the ordering process by allowing you to specify your desired restaurant and pickup timing in advance.

By default it will sleep until the clock minute is 00, so generally you should run it between 4:01pm and 4:59pm, and it will sleep until 5:00pm. It will then make 5 successive attempts to reserve the meal.

Command line options let you specify the restaurant or meal to reserve. Other options are available, with sane defaults.

```
Options:
  -h, --help            show this help message and exit
  -r RESTAURANT, --restaurant=RESTAURANT
                        The name of the restaurant. This or meal name is
                        required.
  -m MEAL, --meal=MEAL  The name of the meal. This or restaurnt name is
                        required.
  -t TIME, --time=TIME  Reservation pickup time. Default is '12:15pm-12:30pm'
  -s SLEEP, --sleep=SLEEP
                        Sleep until this clock minute. Default is 00, ie run
                        at the next hour (XX:00)
  -c CITY, --city=CITY  City name. Default is New York City.
  -d, --dump            Dump the schedule to a JSON file
  ```

## Notes
This is a personal fork/mod of https://github.com/edmundmok/mealpy

It adds command line options, and in general does things a little differently


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
