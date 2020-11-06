import re
import requests
import urllib.parse
import json
import csv
import configparser
import socket
import os.path
import geoip2.database


if os.path.isfile("GeoLite2-City.mmdb") == True:
    if os.path.isfile("GeoLite2-ASN.mmdb") == True:
        geoip2_support = True
        print("================")
        print("Wikipedia revision history auditor!")
        print("---")
        print("GeoIP2 City+ASN support enabled!")
        print("================")
else:
    geoip2_support = False
    print("================")
    print("Wikipedia revision history auditor!")
    print("---")
    print("GeoIP2 City+ASN support disabled!")
    print("================")

config = configparser.ConfigParser()
config.read('settings.ini')
agentname = config['useragent']['agentname']
email =  config['useragent']['agentname']
headers = {
    'User-agent': agentname + " " + email
}
def parse_url(url):
    regex = r'https://([a-z0-9A-Z]{0,3}.[a-z0-9]+.+)\/wiki/([%a-zA-Z_\d\(\.)]+)'
    rs = re.search(regex, url)
    title = rs.group(2)
    base = rs.group(1)
    return base, title

def check_ipv6_ipv4(user):
    regex = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9]{1,3}\.){3}[0-9]{1,3})'
    if re.match(regex, user):
        #If IPv4 or IPv6, return True!
        return True
    else:
        return False


def get_json(urldata):
    #Assemble the API request, rvlimit at 50 as it's the max value Wikipedia supports unlike Mediawiki claims
    baseurl = 'https://{}/w/api.php?action=query&prop=revisions&titles={}&rvslots=*&rvprop=timestamp|user|comment|content&format=json&rvlimit=50'.format(urldata[0], urldata[1])
    #User agent compliant requst 
    r = requests.get(baseurl, headers=headers)
    urldata = r.json()
    storage = []
    if "batchcomplete" in urldata:
        #Max 50 edit pages go like this
        storage.append(r.json())
        return storage
    else:
        storage.append(r.json())
        nextpage = urldata['continue']['rvcontinue']
        #Prepare for the loop..get the continuum URL
        continuing = True
        print("Detected more than 50 edits. Gathering information can take some time...")
        while continuing == True:
            nextpage = urldata['continue']['rvcontinue']
            url = baseurl + '&rvcontinue=' + nextpage
            r = requests.get(url, headers=headers)
            urldata = r.json()
            storage.append(urldata)
            #When the history has been stored to the storage list...
            if "batchcomplete" in urldata:
                continuing = False
        return storage


def parse_edit(pagejson, urldata):
    editlist = [['Username/IP', 'ReverseIP', 'ASOrganization', 'Timestamp', 'UserOrAnonymousEditor', 'Country', 'City', 'Postalcode', 'EditorInfo, EditComment']]
    #Takes the edits 
    for pages in pagejson:
        #Get page id...
        for key in pages['query']['pages'].keys():
            pageid = key
        #Actual edits
        edits = pages['query']['pages'][pageid]['revisions']
        for i in edits:
            username = i['user']
            #UTC timestamp
            timestamp = i['timestamp']
            comment = i['comment']
            is_anonymous = check_ipv6_ipv4(username)
            if is_anonymous == True:
                reverse_ip = get_reverse_ip(username)
            else:
                reverse_ip = "NotAvailable"
            if geoip2_support == True:
                if is_anonymous == True:
                    #Acquire city data!
                    with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
                        try:
                            response = reader.city(username)
                            country = response.country.iso_code
                            city = response.city.name
                            postalcode = response.postal.code
                        except:
                            country = city = postalcode = "NotAvailable"
                else:
                    country = city = postalcode = "NotAvailable"
            else:
                country = city = postalcode = "NotAvailable"
            if geoip2_support == True:
                if is_anonymous == True:
                    #AS Organization data
                    with geoip2.database.Reader('GeoLite2-ASN.mmdb') as reader:
                        try:
                            response = reader.asn(username)
                            as_org = response.autonomous_system_organization
                        except:
                            as_org = "NotAvailable"
                else:
                    as_org = "NotAvailable"
            else:
                as_org = "NotAvailable"
            editor_info_link = "https://xtools.wmflabs.org/ec/" + urldata[0] + "/" + username
            editlist.append([username, reverse_ip, as_org, timestamp, str(is_anonymous), country, city, postalcode, editor_info_link, comment])
    filename = urldata[0] + "_" + urldata[1] + "_edits.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter='|', quotechar='"')
        writer.writerows(editlist)
    return "Completed and results writed to: " + filename


def get_reverse_ip(ipaddress):
    try:
        reversed_dns = socket.gethostbyaddr(ipaddress)
    except:
        reversed_dns = "NotAvailable"
    return reversed_dns[0]