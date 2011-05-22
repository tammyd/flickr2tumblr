#!/usr/bin/python

import flickrapi
import sys

api_key = "b5357a20f386908fa7a51f382a744bc2"
photo_id = sys.argv[1]
photo_size = sys.argv[2]

#photo_id = 5645771097;
#size = 'Medium';

flickr = flickrapi.FlickrAPI(api_key)

infoElem = flickr.photos_getInfo(photo_id=photo_id)
if infoElem.attrib['stat']!='ok':
    sys.exit(-1)
url = infoElem.find('photo').find('urls').findall('url')[0].text

sizesElem = flickr.photos_getSizes(photo_id=photo_id)
if sizesElem.attrib['stat']!='ok':
    sys.exit(-1)

sizes = sizesElem.find('sizes').findall('size')
for size in sizes:
    if size.attrib['label'] == photo_size:
        source = size.attrib['source']
        
print photo_id,url,photo_size,source