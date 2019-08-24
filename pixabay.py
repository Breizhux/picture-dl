# coding: utf-8

import urllib2
import re
#import message_box
#from ast import literal_eval

class InfoExtractor():
    """ Extractor Information class for Pixabay

    Pixabay InfoExtractor that, given url, extract information about the
    image (or images) the URL refers to. This information includes the real
    image URL, the image title, author and others. The information is stored
    in a list of dictionary."""

    def __init__(self, url, verbose) :
        self.url = url
#        self.print_ = message_box.print_(verbose)
        self.hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        self.result_list = []
        self.raw_informations = None
        self.info_dictionary = {
            'username' : None,
            'author' : None,
            'profile_url' : None,
            'is_several_images' : False,
            'id' : None,
            'title' : None,
            'format' : None,
            'description' : None,
            'comments' : None,
            'date' : None,
            'localization' : None,
            'real_urls_and_dimensions' : [], # list of urls and dimensions(W-H),
            'like_nb' : None,}               # ex : [["url1", 1080, 1080],["url2", 640, 640]]

    def get_informations(self) :
        self.raw_informations = self.download_webpage_informations(self.url)
        if self.get_type_link(self.raw_informations) == "post" :
            self.get_information_single_image(self.raw_informations)
            return self.result_list

    def download_webpage_informations(self, url) :
        """ Return the string of image(s) and account informations. """
        request = urllib2.Request(url, headers=self.hdr)
        fh = urllib2.urlopen(request)
        source_code = fh.read()
        return source_code

    def get_type_link(self, url) :
        """ Return if is url of image / account / search """
        type_link_re = re.search(
            r"(https|http)://pixabay.com/fr/(?P<type_link>[a-zA-Z0-9_-]+)*", url)
        if type_link_re.group('type_link') == "photos" :
            return "post"
        elif type_link_re.group('type_link') == "users" :
            return "account"
        elif type_link_re.group('type_link') == "images" :
            return "search"

    def get_information_single_image(self, informations) :
        """ Complete the dictionary with information of code source webpage.
        The result is locate in a list of result (result list) in the form
        of dictionary."""
        user_informations = informations[
            informations.index('    <div class="right">\n        <div style="margin:0 0 20px">\n            <div class="clearfix">'):
            informations.index('</a>\n                <br>')]
        self.info_dictionary['username'] = user_informations[user_informations.index('alt="') + 5:
            user_informations.index('" srcset="')]
        self.info_dictionary['author'] = self.info_dictionary['username'] #there is no real name of author
        self.info_dictionary['profile_url'] = 'https://pixabay.com' + user_informations[
            user_informations.index('               <a href="') + 24 :
            user_informations.index('"><img class="')]
        self.info_dictionary['title'] = informations[informations.index('    <title>')+11:informations.index('</title>')]
        if "Image gratuite sur Pixabay - " in self.info_dictionary['title'] :
            self.info_dictionary['title'] = self.info_dictionary['title'][29:]
        self.info_dictionary['description'] = informations[informations.index('    <meta name="description" content="')+38:
            informations.index('">\n    <meta property="og:image" content="')]
        if "Téléchargez cette image gratuite à propos de " in self.info_dictionary['description'] :
            self.info_dictionary['description'] = self.info_dictionary['description'][49:]
        self.info_dictionary['comments'] = None
        self.info_dictionary['localization'] = None
        url = informations[informations.index('    <meta name="twitter:image" content="')+40:
            informations.index('">\n    <meta name="twitter:image:width"')]
        self.info_dictionary['real_urls_and_dimensions'], image_id, extension = self.get_urls(url, informations)
        self.info_dictionary['id'] = image_id
        self.info_dictionary['format'] = extension
        self.info_dictionary['like_nb'] = None
        self.complete_result_list()

    def get_urls(self, url_type, informations) :
        """ Find all the direct url and size of image in source
            code of webpage with an url type : all url of image
            start by the same structure
            Return the id and the extension of image !!!"""
        extension = url_type[url_type.rfind('.'):]
        image_id = url_type[-15:-8]

        url_type = url_type[:url_type.rfind('_')+1]
        width = int(informations[informations.index('<meta name="twitter:image:width" content="')+42:
            informations.index('">\n    <meta name="twitter:image:height" content="')])
        height = int(informations[informations.index('">\n    <meta name="twitter:image:height" content="')+50:
            informations.index('">\n    <style>')])
        ratio = float(width)/float(height)

        last_url_position = 0
        List_url_found = list()
        List_direct_url_info = list()
        while True :
            try :
                url_start = informations.index(url_type, last_url_position)
                last_url_position = url_start+1
            except ValueError : break #if arrived at end of research
            url_end = informations.index(extension, url_start)+len(extension)
            url = informations[url_start:url_end]
            if not url in List_url_found :
                width = url[len(url_type):url.rfind('.')]
                width = int(width[:width.index('_')]) if "_" in width else int(width)
                height = int(width/ratio)
                List_url_found.append(url)
                List_direct_url_info.append([url, width, height])
        return List_direct_url_info, image_id, extension

    def complete_result_list(self) :
        """ Copy dictionary to result list, the list of dictionary.
        There is one dictionary per image. After append dictionary
        in list, clear it. """
        self.result_list.append(self.info_dictionary)
        self.info_dictionary = {
            'username' : None,
            'author' : None,
            'profile_url' : None,
            'is_several_images' : False,
            'id' : None,
            'title' : None,
            'format' : ".jpg",
            'description' : None,
            'comments' : None,
            'date' : None,
            'localization' : None,
            'real_urls_and_dimensions' : [],
            'like_nb' : None,}
