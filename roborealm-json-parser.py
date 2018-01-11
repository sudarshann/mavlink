import rr
import json
import jsonpickle
import requests
import collections
import urllib2
import sys

response = urllib2.urlopen('http://localhost/autoPilotDataTest')
data = response.read()
rr.SetVariable("data", data )

data = json.loads(data)

rr.SetVariable("data_params", json.dumps(data["params"]) )
rr.SetVariable("data_messages", json.dumps(data["messages"]) )




def flatten(d, parent_key='', sep='_'):
	items = []
	for k, v in d.items():
		new_key = parent_key + sep + k if parent_key else k
		if isinstance(v, collections.MutableMapping):
			items.extend(flatten(v, new_key, sep=sep).items())
		else:
			items.append((new_key, v))
	return dict(items)

flattend_data = flatten(data)

try:
    print len(flattend_data)
    i = 1;
    
    for attr, value in flattend_data.iteritems():
        if not value:
            value = 0
        value = str(value)
        #print "data_" + attr,  value
        rr.SetVariable( "data_" + attr, value )
	#print attr,value
	i = i + 1
    print i
except:
	pass
finally:
    print("Unexpected error:", sys.exc_info())
