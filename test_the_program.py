# coding: utf-8

import downloader

## INSTAGRAM TEST URL ##
#url = "https://www.instagram.com/kevin/"
#url = "https://www.instagram.com/p/BoN5jqiArf9/"
#url = "https://www.instagram.com/explore/tags/linux/"

## FLICKR TEST URL ##
#url = "https://www.flickr.com/photos/16441477@N05"
#url = "https://www.flickr.com/photos/16441477@N05/41901107914/"

## PIXELFED TEST URL ##
#url = "https://pixelfed.social/naki"
#url = "https://pixelfed.social/p/Naki/11995037755904000"

## AMALGRAM TEST URL ##
#url = "https://amalgram.com/7924/papillons-jb-montreal#/albums/7924"
#url = "https://amalgram.com/7924/papillons-jb-montreal#/albums/7924/202742"

## OTHER TEST ##
url = "https://www.instagram.com/kevin/"


x = downloader.Downloader(url, dirs="/home/user/Images")#, only_extract_informations=True)#, id_in_name=False, verbose=False)
#x = downloader.Downloader(url, None, False)
y = x.download()


if y != False and y != "download successfuly" :
    for i in y : print i['title'] if i['title'] != "No title found ;(" else "\n" + i['title'] + " : " + i['description'] + "\n"

