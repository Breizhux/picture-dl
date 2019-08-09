# coding: utf-8

class print_ :
    """ print the message in static or dynamic mode.
    the settings is the message by a list type :
    [0] the message type (ex: 'download', webpage_name, etc)
    [1] the id of picture/username, or action (ex: "Destiantion")
    [2] the message (ex: title, description of action)
    [3] (for dynamic) : the advancement (% or x/y)
    if you don't complete a setting, let a None value."""

    def __init__(self, verbose=True) :
        self.verbose = verbose

    def static(self, message) :
        """ print a simple message if verbose.
        order : [type_message] id: message"""
        if self.verbose :
            display_message = str()
            if message[0] is not None : display_message += "[{0}] ".format(message[0])
            if message[1] is not None : display_message += "{0}: ".format(message[1])
            if message[2] is not None : display_message += "{0}".format(message[2])
            print display_message

    def dynamic(self, message) :
        """ print an avancement in a same line if verbose.
        order : [type_message] id: message | advancement
        It's not a dynamic printer, but i don't found an other name..."""
        if self.verbose :
            display_message = str()
            if message[0] is not None : display_message += "[{0}] ".format(message[0])
            if message[3] is not None : display_message += " {0} ".format(message[3])
            if message[1] is not None : display_message += "| {0}: ".format(message[1])
            if message[2] is not None : display_message += "{0} ".format(message[2])
            print display_message
