# coding: utf-8

import urllib2
import re
import message_box
from ast import literal_eval

class InfoExtractor():
    """ Extractor Information class for PixelFed

    PixelFed InfoExtractor that, given url, extract information about the
    image (or images) the URL refers to. This information includes the real
    image URL, the image title, author and others. The information is stored
    in a list of dictionary."""

    def __init__(self, url, verbose) :
        self.url = url
        self.print_ = message_box.print_(verbose)
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
            'format' : ".jpg", #All images from instagram are jpg
            'description' : None,
            'comments' : None,
            'date' : None,
            'localization' : None,
            'real_urls_and_dimensions' : [], # list of urls and dimensions(W-H),
            'like_nb' : None,}               # ex : [["url1", 1080, 1080],["url2", 640, 640]]

    def get_informations(self) :
        if self.get_type_link(self.url) == "post" :
            self.raw_informations = self.download_post_informations(self.url)
            self.get_information_single_image(self.raw_informations)
        elif self.get_type_link(self.url) == "account" :
            self.info_dictionary['is_several_images'] = True
            self.raw_informations, list_urls = self.download_account_informations(
                self.atom_link(self.url))
            self.get_information_many_images(self.raw_informations, list_urls)
        elif self.get_type_link(self.url) == "undeterminate" :
            return "Error : Url is not valid"
        return self.result_list

    def get_type_link(self, url) :
        """ Return type url from Instagram : many images (acount) or single image
        or undeterminate. The determination find in url."""
        url_post_re = r"(https|http):\/\/(\w+\.|)([a-zA-Z0-9_-]+)\.(bzh|org|social|fr|com|net|ru|cc)/p/([a-zA-Z0-9_-]+)/(\w+)"
        url_account_re = r"(https|http):\/\/(\w+\.|)([a-zA-Z0-9_-]+)\.(bzh|org|social|fr|com|net|ru|cc)/(\w+)$"
        if re.match(url_post_re, url) is not None :
            return "post"
        elif re.match(url_account_re, url) is not None :
            return "account"
        else : return "undeterminate"

    def atom_link(self, url) :
        return re.sub(
            r"(?P<instance>(https|http):\/\/(\w+\.|)([a-zA-Z0-9_-]+)\.(bzh|org|social|fr|com|net|ru|cc)/)(?P<username>([a-zA-Z0-9_-]+))",
            r"\g<instance>users/\g<username>.atom",
            url)

    def download_post_informations(self, url) :
        """ Download the source code of webpage from a post-url.
        Return all webpage source code."""
        request = urllib2.Request(url, headers=self.hdr)
        fh = urllib2.urlopen(request)
        source_code = fh.read()
        return source_code

    def download_account_informations(self, url) :
        """ Download the source code of webpage from an account-url.
        Return a list of source post-url pages."""
        # Download feed webpage
        request = urllib2.Request(url, headers=self.hdr)
        fh = urllib2.urlopen(request)
        source_code = fh.read()
        # List the url of post
        List_of_posts_urls = []
        end = 0
        for i in range(source_code.count('<link rel="alternate" href="')) :
            start = source_code.index('<link rel="alternate" href="', end)+28
            end = source_code.index('" />\n', start)
            List_of_posts_urls.append(source_code[start:end])
        # Download the post informations page
        List_informations = []
        for i, url in enumerate(List_of_posts_urls) :
            self.print_.dynamic(["pixelfed",
                url[url.rfind('/')+1:] if url[len(url)-1] != "/" else url[url[:-1].rfind('/')+1:-1],
                "Downloading picture info webpage",
                "{0} of {1}".format(i+1, len(List_of_posts_urls))])
            List_informations.append(self.download_post_informations(url))

        return List_informations, List_of_posts_urls

    def get_information_single_image(self, webpage_info) :
        """ Complete the dictionary with information of code source webpage.
        The result is locate in a list of result (result list) in the form
        of dictionary."""
        self.info_dictionary['username'] = self.find_info(webpage_info, 'status-username=')
        self.info_dictionary['author'] = self.find_info(webpage_info, 'status-username=')
        self.info_dictionary['profile_url'] = self.find_info(webpage_info, 'status-avatar=')
        self.info_dictionary['id'] = self.find_info(webpage_info, 'status-id=')
        title, description = self.get_title_and_description(webpage_info)
        self.info_dictionary['title'] = title
        self.info_dictionary['description'] = description
        #self.info_dictionary['comments'] = 
        #self.info_dictionary['localization'] = 
        self.info_dictionary['real_urls_and_dimensions'].append(
            [self.find_info(webpage_info, '<meta property="og:image" content='),0,0])
        #self.info_dictionary['like_nb'] = 
        self.complete_result_list()

    def get_information_many_images(self, raw_informations, list_urls) :
        """ Complete dictionary with the get_information_single_image function."""
        for i in raw_informations :
            self.get_information_single_image(i)

    def find_info(self, info, value) :
        """ Find the value of an informations in a line of a source code."""
        return info[info.index(value)+len(value)+1:info.index('"', info.index(value)+len(value)+2)]

    def get_title_and_description(self, webpage_info) :
        """ Return a title for image with description of image.
        if description don't exists, it can't found title.
        The title is crop to the first caracter found : [#,.,!,?,\n]"""
        description = self.find_info(webpage_info, '<meta property="og:description" content=')
        end_title = ["#", ".", "!", "?", "\n"]
        i = 1
        while description[i] not in end_title and i < len(description)-1 : i+=1
        title = description[:i] if i < len(description) else "No title found ;("
        return title.strip().replace("/","-"), description

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
