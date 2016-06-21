import requests
import json
import argparse
from operator import itemgetter

concerts_url = 'http://concerts.livenation.com/json/search/microsite/event/national?site_templ=STYLE_C&page_id=721'

def group_by(lst, group_by):
	nf = {}
	for item in [x[group_by] for x in lst]:
		nf[item] = [x for x in lst if x[group_by] == item]
	return nf


try:
	with open('concerts.json', 'r') as f:
		concerts = json.load(f)
except FileNotFoundError:
	r = requests.get(concerts_url)
	with open('concerts.json', 'w') as f:
		concerts = r.json()['response']['docs']
		json.dump(concerts, f)

cities = sorted(set([x['VenueCity'] for x in concerts]))
states = sorted(set([x['VenueState'] for x in concerts]))
group_bys = ['city', 'state']
sort_bys = ['date', 'eventname']

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--search', type=str, nargs='+', help='tags to search for, including band name')
parser.add_argument('-c', '--city', action='append', dest='city', help='filter by city')
parser.add_argument('-s', '--state', action='append', dest='state', help='filter by state')
parser.add_argument('-g', '--group_by', choices=group_bys)
parser.add_argument('-x', '--sort_by', choices=sort_bys, default='date')
parser.add_argument('-j', '--json', action='store_const', const=True, help='print full json output')

args = parser.parse_args()

filtered = concerts

if args.search is not None:
	nf = []
	for con in filtered:
		for term in args.search:
			if term in con['search-en'] and con not in nf:
				nf.append(con)
	filtered = nf

if args.city is not None:
	filtered = [x for x in filtered if x['VenueCity'] in args.city]
if args.state is not None:
	filtered = [x for x in filtered if x['VenueState'] in args.state]

if args.sort_by == 'date':
	filtered = sorted(filtered, key=itemgetter('EventDate'))
elif args.sort_by == 'eventname':
	filtered = sorted(filtered, key=itemgetter('EventName'))

if args.group_by == 'city':
	filtered = group_by(filtered, 'VenueCity')

if args.group_by == 'state':
	filtered = group_by(filtered, 'VenueState')

if (args.json == True):
	print(json.dumps(filtered))
else:
	if args.group_by is not None:
		for group in filtered:
			print ('{0} concerts:'.format(group))
			for con in filtered[group]:
				print('\t{0}: {1} in {2}'.format(con['LocalEventDateDisplay'], con['EventName'], con['VenueCityState']))
	else:
		for con in filtered:
			print('{0}: {1} in {2}'.format(con['LocalEventDateDisplay'], con['EventName'], con['VenueCityState']))