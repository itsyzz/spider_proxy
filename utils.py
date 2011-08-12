import urllib2


def openurlex(link, retry = 3, timeout = -1, retry_times = 0):
    """Advantced openurl"""
    try:
        if timeout != -1:
            return urllib2.urlopen(link, timeout = timeout)
        else:
            return urllib2.urlopen(link)
    except urllib2.URLError:
        retry_times += 1
        if retry_times > retry:
            raise urlexError("Request url:%s failed, please check your network condition, or comfirm the input url." % link)
        else:
            print "Re-requesting on url:%s - (%d/%d)" % (link, retry_times, retry)
            openurlex(link, retry, timeout, retry_times)


class urlexError(urllib2.URLError):
    """Raised when openurlex failed to request."""
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason

    def __str__(self):
        return '<urlopenex error %s>' % self.reason

def pause():
    while raw_input('Press Enter to continue...'):
        pass

def cprint(cls, string):
    print '[%r]%s' % (cls.__class__, string)

    
if __name__ == '__main__':
    pass
