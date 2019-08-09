# coding: utf-8

import urllib2
import message_box
from ast import literal_eval

class InfoExtractor():
    """ Extractor Information class for Flickr

    Flickr InfoExtractor that, given url, extract information about the
    image (or images) the URL refers to. This information includes the real
    image URL, the image title, author and others. The informations are
    stored in a list of dictionary."""

    def __init__(self, url, verbose) :
        self.url = url
#        self.print_ = message_box.print_(verbose)
        self.result_list = []
        self.raw_informations = None
        self.info_dictionary = {
            'username' : None,
            'author' : None,
            'profile_url' : None,
            'is_several_images' : False,
            'id' : None,
            'title' : None,
            'format' : ".jpg", #all images from flickr are jpg
            'description' : None,
            'comments' : None,
            'date' : None,
            'localization' : None,
            'real_urls_and_dimensions' : [], # list of urls and dimensions(W-H),
            'like_nb' : None,}               # ex : [["url1", 1080, 1080],["url2", 640, 640]]

    def get_informations(self) :
        self.raw_informations = self.download_webpage_informations(self.url) #type dictionary
        if self.get_type_link(self.raw_informations) == "post" :
            self.get_information_single_image(self.raw_informations)
        elif self.get_type_link(self.raw_informations) == "account" :
            self.get_information_many_images(self.raw_informations)
        else : return "Invalid url"
        return self.result_list

    def download_webpage_informations(self, url) :
        """ Return the dictionary of image(s) and account informations. """
        request = urllib2.Request(url)
        fh = urllib2.urlopen(request)
        source_code = fh.read()
        source_code = source_code[
            source_code.index('\t\t\t\t},\n\t\t\t\tmodelExport: {')+24:
            source_code.index('},\n\t\t\t\tauth:')+1]
        source_code = source_code.replace("false", "False")
        source_code = source_code.replace("true", "True")
        source_code = source_code.replace("null", "None")
        dict_of_information = literal_eval(source_code)
        return dict_of_information

    def get_type_link(self, raw_information) :
        """ Return type url from Instagram : many images (acount) or single image
        or undeterminate. The determination find if the dictionary [main][photo-models][0]
        of code source of page is dict type (post) or str type (account)"""
        webpage_info = raw_information['main']['photo-models'][0]
        if type(webpage_info) == dict :
            return "post"
        elif type(webpage_info) == str :
            self.info_dictionary['is_several_images'] = True
            return "account"
        else :
            return "undeterminate"

    def get_information_single_image(self, raw_informations) :
        """ Complete the dictionary with information of code source webpage.
        The result is locate in a list of result (result list) in the form
        of dictionary."""
        webpage_info = raw_informations['main']
        self.info_dictionary['username'] = webpage_info['photo-models'][0]['owner']['username']
        self.info_dictionary['author'] = webpage_info['photo-models'][0]['owner']['realname']
        self.info_dictionary['profile_url'] = webpage_info['photo-models'][0]['owner']['buddyicon']['retina']
        self.info_dictionary['profile_url'] = "https://" + self.info_dictionary['profile_url'].replace("\/","/")[2:]
        self.info_dictionary['id'] = webpage_info['photo-models'][0]['id']
        self.info_dictionary['title'] = webpage_info['photo-models'][0]['title']
        self.info_dictionary['description'] = webpage_info['photo-head-meta-models'][0]['og:description']
#        self.info_dictionary['comments'] = webpage_info[' ???
        self.info_dictionary['date'] = webpage_info['photo-stats-models'][0]['dateTaken']
        self.info_dictionary['localization'] = webpage_info['photo-models'][0]['owner']['localization']
        for i in webpage_info['photo-models'][0]['sizes'].values() :
            self.info_dictionary['real_urls_and_dimensions'].append([
                i['displayUrl'].replace("\/", "/"), # flickr url have escape caracter, replace it for '/'
                i['width'],
                i['height']])
        self.info_dictionary['real_urls_and_dimensions'] = self.sort_images_size(
            self.info_dictionary['real_urls_and_dimensions'])
        self.info_dictionary['like_nb'] = webpage_info['photo-models'][0]['engagement']['faveCount']
        self.complete_result_list()

    def get_information_many_images(self, raw_informations) :
        """ Complete dictionary and put this in result list at the rate of
        one dictionary per image. The dictionary is reset at each loop of
        research information for one image. """
        webpage_info = raw_informations['main']
        for i in webpage_info['photostream-models'][0]['photoPageList']['_data'] :
            self.info_dictionary['username'] = webpage_info['photostream-models'][0]['owner']['username']
            self.info_dictionary['author'] = webpage_info['photostream-models'][0]['owner']['realname']
            self.info_dictionary['profile_url'] = webpage_info['photostream-models'][0]['owner']['buddyicon']['retina']
            self.info_dictionary['profile_url'] = "https://" + self.info_dictionary['profile_url'].replace("\/","/")[2:]
            self.info_dictionary['id'] = i['id']
            self.info_dictionary['title'] = i['title']
            #self.info_dictionary['description'] = i[' ???
            #self.info_dictionary['comments'] = i[' ???
            self.info_dictionary['date'] = i['stats']['dateTaken']
            #self.info_dictionary['localization'] = i[' ???
            for j in i['sizes'].values() :
                self.info_dictionary['real_urls_and_dimensions'].append([
                    j['displayUrl'].replace("\/", "/"), # flickr url have escape caracter, replace it for '/'
                    j['width'],
                    j['height']])
            self.info_dictionary['real_urls_and_dimensions'] =self. sort_images_size(
                self.info_dictionary['real_urls_and_dimensions'])
            self.info_dictionary['like_nb'] = i['engagement']['faveCount']
            self.complete_result_list()

    def sort_images_size(self, list_of_size) :
        """ Sort the list of real url and dimensions. The url are sort by
        dimensions of images from the little to the bigger. """
        result_sorted_size = []
        list_sorted_width = list()
        list_sorted_height = list()
        for i in list_of_size :
            list_sorted_width.append(i[1])
            list_sorted_height.append(i[2])
        list_sorted_width.sort()
        list_sorted_height.sort()

        for i in range(len(list_sorted_width)) :
            for j in list_of_size :
                if j[1] == list_sorted_width[i] and j[2] == list_sorted_height[i] :
                    result_sorted_size.append(j)
        return result_sorted_size

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
