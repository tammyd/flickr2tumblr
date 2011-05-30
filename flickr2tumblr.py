#!/usr/bin/python

import flickrapi
import sys
import ConfigParser
from optparse import OptionParser
from tumblr import Api

## Setup the command line options. Note that the command line
## takes precedence over anything in the config file

usage = """Usage: %prog [options] flickr_photo_id

All required options (except for the flickr_photo_id) can be specified either
via the command line or config file."""
  
## Because we are also using a config file but want command line args
## to take precendemce, we can't use optionParsers default value functions,
## as there's no way to tell if the resulting object is populated with user or
## default values.
defaults = {'photo_size': 'Medium',
            'post_state': 'draft'}
required = ['api_key','blog','email','password','photo_size','post_state','post_type']
  
parser = OptionParser(usage=usage)
parser.add_option('-c', '--config', action='store', type='string', dest="config_file",
                  help="Config file. Use to store tumblr and flickr options. Default = %default. Required.", default='flickr2tumblr.ini')
parser.add_option('-z', '--size', dest="photo_size", help="Flickr photo size. Default = %s. Required." % defaults['photo_size'])
parser.add_option('-k', '--key', dest="api_key", help="Flickr api key. Required. ")
parser.add_option('-b', '--blog', dest="blog", help="Tumblr blog name; the @tumblr.com is not necessary. Required.")
parser.add_option('-e', '--email', dest="email",help="Tumblr email login. Required.")
parser.add_option('-p', '--password', dest="password", help="Tumblr password. Required ")
parser.add_option('-s', '--state', dest='post_state', help='Tumblr post state. Default = %s. Required.' % defaults['post_state'])
parser.add_option('-g', '--tags', dest='tags', help='Tumblr post tags. Optional.')
parser.add_option('-n', '--caption', dest='caption', help='Tumblr post caption. Optional.')
parser.add_option('-d', '--date', dest='date', help="Tumblr post date. Optional.")
parser.add_option('-u', '--group', dest='group', help="Tumblr post group (ie secondary tumblr blog) to post to as well. Optional.")
parser.add_option('-w', '--twitter', dest='twitter', help='Custom mesage to post to predefined twitter account with post. Optional')
parser.add_option('-l', '--slug', dest='slug', help="Custom string to appear in the tumblr post's url. Optional")
parser.add_option('-r', '--private', action='store_true', dest='private', help='Make tumblr post private if set. Optional.');


(options, args) = parser.parse_args()

## only required command line arg is photo_id
try:
    options.__dict__['photo_id'] = args[0]
except:
    print "ERROR: photo_id must be specified\n"
    parser.print_help()
    sys.exit(-1)
    

## Read the config file. Note that no error is thrown if the file doesn't
## exist; the parser just behaves as if the config file is empty.
cfgOptions = {}
if options.config_file is not None:
    cfgParser = ConfigParser.ConfigParser()
    cfgParser.read(options.config_file)
    # we really don't care what section an option is defined under in the config
    # file, it's more for human organization than anything. 
    for option,value in options.__dict__.iteritems():
        if value is None:
            try:
                # option not defined yet, check config file
                value = cfgParser.get('flickr2tumblr', option)
            except:
                # option not in config file either, do we have a default?
                if option in defaults:
                    value = defaults[option]
                else:
                    value = None
                   
            if value is not None:
                # we either found the value in the config file, or it has a default
                # save the config to be added to options object later
                cfgOptions[option] = value
                
## add the config/default options to the options object so everything is in
## one place
for option,value in cfgOptions.iteritems():
    options.__dict__[option] = value
    
## ensure all required elements exist
die = False
for option,value in options.__dict__.iteritems():
    if option in required:
        if value is None:
            print "ERROR: %s is required and must either be specified as an argument or in the config file" % option
            die = True
if die:
    print "";
    parser.print_help()
    sys.exit(-1)

## Use flickr api to get photo info. API Key required - see http://www.flickr.com/services/apps/create/apply/    
flickr = flickrapi.FlickrAPI(options.api_key)
infoElem = flickr.photos_getInfo(photo_id=options.photo_id)
if infoElem.attrib['stat']!='ok':
    print "Unable to get info from photo_id", photo_id
    sys.exit(-1)

## this is the photo's main url, use as click-through link of post    
url = infoElem.find('photo').find('urls').findall('url')[0].text

## look for the actual image file in the specified size
sizesElem = flickr.photos_getSizes(photo_id=options.photo_id)
if sizesElem.attrib['stat']!='ok':
    print "Unable to get sizes for photo_id", photo_id
    sys.exit(-1)

sizes = sizesElem.find('sizes').findall('size')
source = None
for size in sizes:
    if size.attrib['label'] == options.photo_size:
        source = size.attrib['source']
  
if source is None:
    print "ERROR: %s is a not defined size for %s" % (options.photo_size, options.photo_id)
    sys.exit(-1)
    
## Build up the arguments to post to the Tumblr api
tumblrArgs = {}
tumblrArgs['state'] = options.post_state
tumblrArgs['type'] = 'photo'
tumblrArgs['source'] = source
tumblrArgs['click-through-url'] = url
if options.tags is not None:
    tumblrArgs['tags'] = options.tags
if options.group is not None:
    tumblrArgs['group'] = options.group
if options.twitter is not None:
    tumblrArgs['send-to-twitter'] = options.twitter
if options.slug is not None:
    tumblrArgs['slug'] = options.slug
if options.date is not None:
    if options.post_state == 'queue':
        tumblrArgs['publish-on'] = options.date
    else:
        tumblrArgs['date'] = options.date
if options.private == True:
    tumblrArgs['private'] = 1

## send the arguments tp tumblr via the write api    
api = Api(options.blog,options.email,options.password)
try:
    post = api._write(tumblrArgs)
    print "Photo post saved as %s!" % (options.post_state)
except:
    print "Error saving post"
    
    
