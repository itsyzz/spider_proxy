"""Proxy info crawled from web

Crawil proxy form web, simpled infomation(with ip&port only)
"""

import re

import cPickle

import os

import time

import urllib2

from utils import openurlex, pause, cprint


class WebSpider(object):
    """Base spider
    """
    
    def __init__(self):
        self.cont = ''
        self.link = ''
        cprint(self, 'Web spider initial:%r' % self)

    def view(self, link):
        """Get link content
        """
        self.link = link
        cprint(self, 'Start viewing at %r' % link)
        self.cont = openurlex(link).read()

    def crawl(self):
        """Collect specific info from viewing
        different spider has different crawl way
        """
        cprint(self, 'Start crawling at %r' % self.link)


class ProxySpider(WebSpider):
    """Proxy spider
    """
    
    def __init__(self):
        """Suport store proxy info data
        """
        WebSpider.__init__(self)
        self.proxyinfo = {}

    def view(self, link):
        WebSpider.view(self, link)

    def crawl(self):
        WebSpider.crawl(self)

    def save_collected(self, ips, ports):
        """Save collected info with ips, ports in memory - type: list
        """
        for i in range(len(ips)):
            self.proxyinfo.update({ips[i]: {}})
            self.proxyinfo[ips[i]].update({'ip': ips[i]})
            self.proxyinfo[ips[i]].update({'port': ports[i]})

    def store(self, filename_keyword):
        """Store collected data in (hard) disk:
        Dump data to \data\proxy\%filename_keyword%_%time%.pkl
        Save data as txt to \data\proxy\%filename_keyword%_%time%.pxy
        """
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists('data\proxy'):
            os.mkdir('data\proxy')

        tag = time.strftime('%Y%m%d%H%M%S')
        
        filename_pkl = '%s_%s.pkl' % (filename_keyword, tag)
        try:
            output_pkl = open('data\proxy\%s' % filename_pkl, 'wb')
        except IOError as errinfo:
            cprint(self, 'Proxy data dump failed: %s' % errinfo)
            return
        with output_pkl:
            cPickle.dump(self.proxyinfo, output_pkl , cPickle.HIGHEST_PROTOCOL)
            cprint(self, 'Proxy data save to data\proxy\%s' % filename_pkl)

        filename_pxy = '%s_%s.pxy' % (filename_keyword, tag)
        try:
            output_pxy = open('data\proxy\%s' % filename_pxy, 'w')
        except IOError as errinfo:
            cprint(self, 'Proxy data save failed: %s' % errinfo)
            return
        with output_pxy:
            for i in range(len(self.proxyinfo.values())):
                output_pxy.write("%s:%s\n" %
                                 (self.proxyinfo.values()[i]['ip'],
                                  self.proxyinfo.values()[i]['port']))
            cprint(self, 'Proxy data save to data\proxy\%s' % filename_pxy)


class nntimeSpider(ProxySpider):
    """Proxy spider at http://nntime.com
    """
    
    def __init__(self):
        """Add links which spider must view&crawl:
            http://nntime.com/proxy-list-%02d.htm.
        Recommend set range from 1 to 50
        """
        ProxySpider.__init__(self)
        self.links = ('http://nntime.com/proxy-list-%02d.htm'
                      % i for i in range(1, 2))

    def view(self, link):
        ProxySpider.view(self, link)

    def crawl(self, save = True):
        """Crawl necessary info from nntime.com
        Regular expression pattern and decrypt encrypted-port code
        maybe change depend on url source

        - if param save set to False, collected info will not be saved in memory

        Here's a simply explanation for decrypt encrypted-port:
            Ports at nntime are encrypted as fake random-string,
            as it random - String is really random
            as it fake - same number at per page is same random string
            So we can find regular pattern at those string
            Key:
                1.Per ip:port slot has specific string, and that string has
                port value at bottom.
                2.Each single number at port itself is encrypted as '+alpha'
                3.So that we can get len of encrypted port and capture the
                real port by Key.1
        """
        ProxySpider.crawl(self)
        p_port1 = re.compile(r'value="([0-9.]{0,36})" onclick', re.DOTALL)
        p_port2 = re.compile(r'\(":"([a-zA-Z+]{0,8})\)', re.DOTALL)
        p_ip = re.compile(r'</td><td>([0-9.]{0,16})<script', re.DOTALL)
        for link in self.links:
            self.view(link)
            #get decrypt port
            encrypt_ports1 = [
                port1.group(1) for port1 in re.finditer(p_port1, self.cont)]
            encrypt_ports2 = [
                port2.group(1) for port2 in re.finditer(p_port2, self.cont)]
            ports = []
            for i in range(len(encrypt_ports1)):
                if len(encrypt_ports2) != len(encrypt_ports1):
                    cprint(self, 'Port crawled odd,')
                    cprint(self, 'may occur some issues')
                    pause()
                ports.append(encrypt_ports1[i][-len(encrypt_ports2[i])/2:])
            #get ip    
            ips = [ip.group(1) for ip in re.finditer(p_ip, self.cont)]
            #exception tick
            if len(ips) != len(ports):
                cprint(self, 'Port&IP collected amount is different,')
                cprint(self, 'may occur some issues')
                pause()

            if not save is False:
                self.save_collected(ips, ports)
            
    def save_collected(self, ips, ports):
        ProxySpider.save_collected(self, ips, ports)

    def store(self):
        ProxySpider.store(self, 'nntime')
        

class spysruSpider(ProxySpider):
    """Proxy spider at http://www.spys.ru
    """

    def __init__(self):
        """Add links which spider must view&crawl:
            http://nntime.com/proxy-list-%02d.htm.
        Recommend set range from 0 to 8
        """
        ProxySpider.__init__(self)
        self.links = ('http://spys.ru/proxylist%d/' % i for i in range(0, 1))

    def view(self, link):
        ProxySpider.view(self, link)

    def crawl(self, save = True):
        """Crawl necessary info from spysru.com
        Regular expression pattern and decrypt encrypted-port code
        maybe change depend on url source

        - if param save set to False, collected info will not be saved in memory
        
        Here's a simply explanation for decrypt encrypted-port:
            Ports at spysru are encrypted as fake random-string,
            as it random - String is really random
            as it fake - same number at per page is same random string
            So we can find regular pattern at those string
            eg. 8080 has same number with position 1&3, 2&4
        """
        ProxySpider.crawl(self)
        p_port = re.compile(r'font>"\+(.*?)\)</script>', re.DOTALL)
        p_ip = re.compile((r'class=spy14>([0-9.]{0,20})<script'), re.DOTALL)
        
        for link in self.links:
            self.view(link)
            
            x_ports = re.finditer(p_port, self.cont)
            encrypt_ports = [x_port.group(1) for x_port in x_ports]
            #decrypt number
            cout_3128 = 0
            realnum = {3128: None, 8080: None, 80: None, 8909: None}
            for encrypt_port in encrypt_ports:
                num = encrypt_port.split('+')
                num_cout = encrypt_port.count('+') + 1
                
                if num_cout == 4:
                    #Detect 8080
                    if num[0] == num[2] and num[1] == num[3] and \
                       num[0] != num[1]:
                        realnum[num[0]], realnum[8] = 8, num[0]
                        realnum[num[1]], realnum[0] = 0, num[1]
                    #Detect 8909
                    elif num[1] == num[3] and num[0] != num[1] and \
                         num[0] != num[2] and num[1] != num[2]:
                        realnum[num[0]], realnum[8] = 8, num[0]
                        realnum[num[1]], realnum[9] = 9, num[1]
                        realnum[num[2]], realnum[0] = 0, num[2]
                    #Detect 3128
                    elif num[0] != num[1] and num[0] != num[2] and \
                         num[0] != num[3] and num[1] != num[2] and \
                         num[1] != num[3] and num[2] != num[3]:
                        if realnum[3128] is None:
                            realnum[3128] = num
                        else:
                            if num == realnum[3128]:
                                cout_3128 += 1
                        #Recognize as 3128 if True
                        if cout_3128 >= 3:
                            realnum[num[0]], realnum[3] = 3, num[0]
                            realnum[num[1]], realnum[1] = 1, num[1]
                            realnum[num[2]], realnum[2] = 2, num[2]
                            realnum[num[3]], realnum[8] = 8, num[3]
                elif num_cout == 2:
                    #Detect as 80 - only detect as 80 after 8080 found
                    if realnum.has_key(8) is True and realnum[8] == num[0] and \
                       realnum.has_key(0) is True and realnum[0] == num[1]:
                        realnum[num[0]], realnum[8] = 8, num[0]
                        realnum[num[1]], realnum[0] = 0, num[1]
            #decrypt port
            try:
                for i in range(len(encrypt_ports)):
                    encrypt_ports[i] = encrypt_ports[i].replace('+', '')
                    for n in range(0, 10):
                        if realnum.has_key(n):
                            encrypt_ports[i] = encrypt_ports[i].replace(
                                realnum[n], str(n))
            except KeyError:
                cprint(self, 'Cannot detect some number, may bugged.')
                pause()
            ports = encrypt_ports

            ips = [x_ip.group(1) for x_ip in re.finditer(p_ip, self.cont)]

            if not save is False:
                self.save_collected(ips, ports)

    def save_collected(self, ips, ports):
        ProxySpider.save_collected(self, ips, ports)

    def store(self):
        ProxySpider.store(self, 'spysru')

            
            
if __name__ == '__main__':
    spysru_spider = spysruSpider()
    spysru_spider.crawl()
    spysru_spider.store()
    nntime_spider = nntimeSpider()
    nntime_spider.crawl()
    nntime_spider.store()
    import crawl_proxy
    help(crawl_proxy)
    print ''
