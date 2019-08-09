# coding: utf-8

import os
import re
import urllib2
import message_box

class Downloader :
    """ Downloader class work in 3 times :
    - Recognition of original website (UrlDetection class)
    - Extract informations picture(s) (extractor directory)
    - Downloading of the picture or pictures with ursers options
    only if user want to downloading it. """

    def __init__(self, url,
            dirs=None,
            only_extract_informations=False,
            quality="maximum",
            id_in_name=True,
            verbose=True) :

        self.url = self.clear_link(url)
        self.directory = dirs if dirs else os.getcwd()
        self.only_extract_informations = only_extract_informations
        self.quality = quality
        self.id_in_name = id_in_name
        self.verbose = verbose
        self.print_ = message_box.print_(verbose)
        self.extractor = None
        self.informations = None
        # For pixelfed (and other)...
        self.hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

    def download(self) :
        self.import_extractor(self.url_detection(self.url), self.url)
        self.informations = self.extract_info(self.url)
        if type(self.informations) != list :
            self.print_.static([None, "ERROR", self.informations])
            return False
        if not self.only_extract_informations :
            self.save_pictures(self.directory, self.informations, self.quality)
            return "download successfuly"
        else :
            return self.informations

    def clear_link(self, url) :
        """ Return a url without the option :
        - language : "/?hl=", 
        - other in future... """
        if "/?hl=" in url :
            url = url[:url.index('/?hl=')]
        return url

    def extract_id(self, url) :
        """ Extract the last element of url. It's probably the id of picture
        or of author. But it's not sure."""
        return url[url.rfind('/')+1:] if url[len(url)-1] != "/" else url[url[:-1].rfind('/')+1:-1]

    def url_detection(self, url) :
        """ Return the name of original website with the domain name
        of the url. Return a simple str value or "direct_link" if url
        is a direct link to an image. """
        if re.match(r"([a-zA-Z0-9\/\._-]+)(.jpg|.jpeg|.png|.tiff|.bmp|.ico)*",url) :
            return "direct_link"
        website_name_re = re.search(
            r"(https|http):\/\/(\w+\.|)(?P<domain_name>[a-zA-Z0-9_-]+)\.(bzh|org|social|fr|com|net|ru|cc)*", url)
        return website_name_re.group('domain_name')

    def import_extractor(self, website_name, url) :
        """ import the good extractor and create the object """
        self.print_.static([website_name,
            self.extract_id(url) if website_name != "direct_link" else "",
            "Downloading picture info webpage" if website_name != "pixelfed" else "Downloading webpage"])
        if website_name == "instagram" :
            import instagram
            self.extractor = instagram
        elif website_name == "flickr" or website_name == "staticflickr" :
            import flickr
            self.extractor = flickr
        elif website_name == "direct_link" :
            import direct_link
            self.extractor = direct_link
            self.id_in_name = False
        else :
            import pixelfed
            self.extractor = pixelfed

    def extract_info(self, url) :
        """ Get importants informations from webpage by the good extractor."""
        information = self.extractor.InfoExtractor(url, self.verbose)
        return information.get_informations()

    def save_pictures(self, directory, informations, quality) :
        """ Execute the write function after find name and format of picture."""
        if informations[0]['is_several_images'] : directory += "/%s" %informations[0]['author']
        if not os.path.exists(directory) : os.makedirs(directory)
        for i, info in enumerate(informations) :
            picture_name = "{0}{1}{2}".format(info['title'], "-"+info['id'] if self.id_in_name else "", info['format'])
            if len(informations) > 1 :
                if i == 0 : self.print_.static(["download", info['author'], "Downloading pictures"])
                self.print_.dynamic(["download", "Destination", picture_name, "{0} of {1}".format(i+1,len(informations))])
            else :
                self.print_.static(["download", "Destination", picture_name])
            quality_nbr = len(info['real_urls_and_dimensions'])-1 if quality == "maximum" else quality
            record_name = "{0}/{1}".format(directory, picture_name)
            real_url = info['real_urls_and_dimensions'][quality_nbr][0]
            self.write_picture_on_disk(record_name, real_url)

    def write_picture_on_disk(self, name_picture, real_url) :
        """ Write the picture on the disk."""
        request = urllib2.Request(real_url, headers=self.hdr)
        fh = urllib2.urlopen(request)
        picture = fh.read()
        with open(name_picture, 'w') as picture_file :
            picture_file.write(picture)
