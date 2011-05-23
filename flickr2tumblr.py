#!/usr/bin/python

import flickrapi
from tumblr import Api
import sys
import ConfigParser

cfgParser = ConfigParser.ConfigParser()
cfgParser.read('config.ini')
cfgSettings = {'flickr':['api_key'], 'tumblr':['blog','email','password']}
config = {}
for cat,key in cfgSettings.iteritems():
    for value in key:
        try:
            config["%s_%s" % (cat,value)] = cfgParser.get(cat,value)
        except:
            print "Error in config file - missing or invalid %s %s" % (cat,value)
            sys.exit(-1)

if len(sys.argv) < 3:
    print "Usage: flickr2tumblr <photo_id> <photo_size> [tags]"
    sys.exit(-1) 

photo_id = sys.argv[1]
photo_size = sys.argv[2]

flickr = flickrapi.FlickrAPI(config['flickr_api_key'])

infoElem = flickr.photos_getInfo(photo_id=photo_id)
if infoElem.attrib['stat']!='ok':
    print "Unable to get info from photo_id", photo_id
    sys.exit(-1)
    
url = infoElem.find('photo').find('urls').findall('url')[0].text

sizesElem = flickr.photos_getSizes(photo_id=photo_id)
if sizesElem.attrib['stat']!='ok':
    print "Unable to get sizes for photo_id", photo_id
    sys.exit(-1)

sizes = sizesElem.find('sizes').findall('size')
source = None
for size in sizes:
    if size.attrib['label'] == photo_size:
        source = size.attrib['source']
  
if source is None:
    print photo_size,"is a not defined size for photo",photo_id
    die(-1)
    

tumblrArgs = {}
tumblrArgs['state'] = 'queue'
tumblrArgs['type'] = 'photo'
tumblrArgs['source'] = source
tumblrArgs['click-through-url'] = url
tumblrArgs['tags'] = 'cat,"black cat"'
try:
    tags = sys.argv[3]
    tumblrArgs['tags'] = tumblrArgs['tags'] + "," + tags
except:
    #do nothing
    tumblrArgs['tags'] = tumblrArgs['tags']
    
api = Api(config['tumblr_blog'],config['tumblr_email'],config['tumblr_password'])
try:
    post = api._write(tumblrArgs)
    print "Post Queued!"
except:
    print "Error queuing post"
    
    
