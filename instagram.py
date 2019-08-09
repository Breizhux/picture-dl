# coding: utf-8

import urllib2
import message_box
from ast import literal_eval

class InfoExtractor():
    """ Extractor Information class for Instagram

    Instagram InfoExtractor that, given url, extract information about the
    image (or images) the URL refers to. This information includes the real
    image URL, the image title, author and others. The information is stored
    in a list of dictionary."""

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
            'format' : ".jpg", #all images from instagram are jpg
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
            return self.result_list
        elif self.get_type_link(self.raw_informations) == "account" :
            self.get_information_many_images(self.raw_informations)
            return self.result_list
        elif self.get_type_link(self.raw_informations) == "tagpage" :
            self.get_informations_tagpage_images(self.raw_informations)
            return self.result_list
        else : return "Invalid url"

    def download_webpage_informations(self, url) :
        """ Return the dictionary of image(s) and account informations. """
        request = urllib2.Request(url)
        fh = urllib2.urlopen(request)
        source_code = fh.read()
        source_code = source_code[
            source_code.index('<script type="text/javascript">window._sharedData = ')+52:
            source_code.index(';</script>\n<script type="text/javascript">window.__initialDataLoaded(window._sharedData);</script>')]
        source_code = source_code.replace("false", "False")
        source_code = source_code.replace("true", "True")
        source_code = source_code.replace("null", "None")
        dict_of_information = literal_eval(source_code)
        return dict_of_information

    def get_type_link(self, webpage_info) :
        """ Return type url from Instagram : many images (acount) or single image
        or undeterminate. The determination find if in the dictionary of source
        code of page exist the ['entry_data']['PostPage'] keys (simple post) or
        ['entry_data']['ProfilePage'] keys exists (account url)"""
        webpage_info = webpage_info['entry_data']
        if webpage_info.has_key('PostPage') :
            return "post"
        elif webpage_info.has_key('ProfilePage') :
            self.info_dictionary['is_several_images'] = True
            return "account"
        elif webpage_info.has_key('TagPage') :
            self.info_dictionary['is_several_images'] = True
            return "tagpage"
        else :
            return "undeterminate"

    def get_information_single_image(self, raw_informations) :
        """ Complete the dictionary with information of code source webpage.
        The result is locate in a list of result (result list) in the form
        of dictionary."""
        webpage_info = raw_informations['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        self.info_dictionary['username'] = webpage_info['owner']['username']
        self.info_dictionary['author'] = webpage_info['owner']['full_name']
        self.info_dictionary['profile_url'] = webpage_info['owner']['profile_pic_url']
        self.info_dictionary['id'] = webpage_info['shortcode']
        title, description = self.get_title_and_description(webpage_info)
        self.info_dictionary['title'] = title
        self.info_dictionary['description'] = description
        self.info_dictionary['comments'] = webpage_info['edge_media_to_comment']
        self.info_dictionary['localization'] = webpage_info['localization']
        for i in webpage_info['display_resources'] :
            self.info_dictionary['real_urls_and_dimensions'].append([
                i['src'],
                i['config_width'],
                i['config_height']])
                #self.info_dictionary["sizes"]
        self.info_dictionary['like_nb'] = webpage_info['edge_media_preview_like']['count']
        self.complete_result_list()

    def get_information_many_images(self, raw_informations) :
        """ Complete dictionary and put this in result list at the rate of
        one dictionary per image. The dictionary is reset at each loop of
        research information for one image. """
        webpage_info = raw_informations['entry_data']['ProfilePage'][0]['graphql']['user']
        for i in webpage_info['edge_owner_to_timeline_media']['edges'] :
            self.info_dictionary['username'] = webpage_info['username']
            self.info_dictionary['author'] = webpage_info['full_name']
            self.info_dictionary['profile_url'] = webpage_info['profile_pic_url_hd']
            self.info_dictionary['id'] = i['node']['shortcode']
            title, description = self.get_title_and_description(i['node'])
            self.info_dictionary['title'] = title
            self.info_dictionary['description'] = description
            self.info_dictionary['comments'] = i['node']['edge_media_to_comment']
            self.info_dictionary['localization'] = i['node']['localization']
            for j in i['node']['thumbnail_resources'] :
                self.info_dictionary['real_urls_and_dimensions'].append([
                    j['src'],
                    j['config_width'],
                    j['config_height']])
            self.info_dictionary['real_urls_and_dimensions'].append([
                i['node']['display_url'],
                i['node']['dimensions']['width'],
                i['node']['dimensions']['height']])
            self.info_dictionary['like_nb'] = i['node']['edge_liked_by']['count']
            self.complete_result_list()

    def get_informations_tagpage_images(self, raw_informations) :
        """ Complete dictionary and put this in result list at the rate of
        one dictionary per image. The dictionary is reset at each loop of
        research information for one image. """
        webpage_info = raw_informations['entry_data']['TagPage'][0]['graphql']['hashtag']
        for i in webpage_info['edge_hashtag_to_media']['edges'] :
            self.info_dictionary['username'] = webpage_info['name']
            self.info_dictionary['author'] = webpage_info['name']
            self.info_dictionary['id'] = i['node']['shortcode']
            title, description = self.get_title_and_description(i['node'])
            self.info_dictionary['title'] = title
            self.info_dictionary['description'] = description
            self.info_dictionary['comments'] = i['node']['edge_media_to_comment']
            for j in i['node']['thumbnail_resources'] :
                self.info_dictionary['real_urls_and_dimensions'].append([
                    j['src'],
                    j['config_width'],
                    j['config_height']])
            self.info_dictionary['real_urls_and_dimensions'].append([
                i['node']['display_url'],
                i['node']['dimensions']['width'],
                i['node']['dimensions']['height']])
            self.info_dictionary['like_nb'] = i['node']['edge_liked_by']['count']
            self.complete_result_list()

    def get_title_and_description(self, webpage_info) :
        """ Return a title for image with description of image.
        if description don't exists, it can't found title. 
        The title is crop to the first caracter found : [#,.,!,?,\n]"""
        if len(webpage_info['edge_media_to_caption']['edges']) == 0 :
            return "No title :(", "Because no description..."
        description = webpage_info['edge_media_to_caption']['edges'][0]['node']['text']
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
