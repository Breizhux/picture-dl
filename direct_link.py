# coding: utf-8

import re

class InfoExtractor():
    """ Extractor Information class for direct link

    Direct link InfoExtractor that, given url, extract the name
    of image name file with re lib."""

    def __init__(self, url, verbose) :
        self.url = url
#        self.print_ = message_box.print_(verbose)
        self.result_list = []
        self.info_dictionary = {
            'username' : "direct_link",
            'author' : "direct_link",
            'profile_url' : None,
            'is_several_images' : False,
            'id' : "direct_link",
            'title' : None,
            'format' : ".jpg", #Default value
            'description' : None,
            'comments' : None,
            'date' : None,
            'localization' : None,
            'real_urls_and_dimensions' : [[self.url, "none", "none"]],
            'like_nb' : None,}

    def get_informations(self) :
        information_re = re.search(
            r"([a-zA-Z0-9\/\.-]+)\/(?P<file_name>[a-zA-Z0-9_-]+)\.(?P<extension>(jpg|jpeg|png|tiff|bmp|ico))*",
            self.url)
        self.info_dictionary['title'] = information_re.group('file_name')
        self.info_dictionary['format'] = ".{0}".format(information_re.group('extension'))
        self.result_list.append(self.info_dictionary)
        return self.result_list
