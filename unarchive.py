import BeautifulSoup as bs4
import urllib2
import re
import urllib
import webbrowser
import sys

def unarchive(url, custom_domain=None):
    match = re.match(r"http:\/\/([^.]+)\.42pag\.es(\/.*)?", url or url)
    subdomain = match.group(1)
    path = (match.group(2) or '/')[1:]
    print 'Site:', subdomain
    print 'Page:', path
    archived_url = 'https://web.archive.org/web/' + (custom_domain or url)
    content = urllib2.urlopen(archived_url).read()
    soup = bs4.BeautifulSoup(content)
    
    link_fields = ['href', 'src']
    for field in link_fields:
        for tag in soup.findAll(lambda tag: tag.has_key(field)):
            match = re.match(r"^\/web\/[a-zA-Z0-9_]+\/(.*)$", tag[field])
            if match:
                tag[field] = match.group(1)
    
    source = soup.find('div', {'id': '__content'}).renderContents()
    css = soup.findAll('style')[1].text
    
    params = {
        # "page": path,
        "source": source,
        "css": css # can't currently update js
    }
    req_url = "http://{0}.42pag.es/__meta/code?page={1}".format(subdomain, urllib.quote(path))
    
    data = urllib.urlencode(params)
    req = urllib2.Request(req_url, data)
    response = urllib2.urlopen(req)
    print response.read()
    webbrowser.open(url)

if __name__ == '__main__':
    # get_content('http://test.42pag.es')
    
    # get_content('http://nate.42pag.es/abc')
    
    # unarchive('http://gerbil.42pag.es/')
    if len(sys.argv) < 2: print "usage: python unarchive.py http://mysite.42pag.es [http://mycustomdomain.com]"
    custom = sys.argv[2] if len(sys.argv) > 2 else None
    unarchive(sys.argv[1], custom_domain=custom)

