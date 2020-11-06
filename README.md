# Wiki Revision Auditing -tool

This tool is used to gather insights per Wikipedia article edits through the MediaWiki API used throughly by all Wikipedia instances worldwide.

## Capabilities

Extracting the revision history and essential data from a single Wikipedia article worldwide. Output automatically stored as a CSV.

## Usage & Deploy

Clone & execute, install requirements by:

```pip3 install -r requirements.txt```

Remember to set your contact information to your settings to be compliant with MediaWiki API! Sample 'settings-sample.ini' has been provided for you.

Set the required information to: settings.ini.

More about this practice at: https://meta.wikimedia.org/wiki/User-Agent_policy

### Usage 

```
Wikipedia revision history auditor!
---
GeoIP2 City+ASN support enabled!
================
usage: wrevdit.py [-h] initial_url

Audits Wikipedia articles. Example: ./wrevdit.py https://en.wikipedia.org/wiki/Gomenasai_(t.A.T.u_song)

positional arguments:
  initial_url  Article's URL.

optional arguments:
  -h, --help   show this help message and exit

  
```

## How to enable the GeoIP2 support?

Note: this data gets less trustworthy the older it is due to the possibility of the IPv4/IPv6 blocks being re-assigned to some other organization / individual. Someone could work around this by owning multiple sets of GeoIP databases for different years...

Aquiring these databases happens as specified in MaxMind's own website:
https://dev.maxmind.com/geoip/geoip2/geolite2/

And supported type is: GeoLite2 City 

To enable support, add the 'GeoLite2-City.mmdb' to this directory AND:

add the 'GeoLite2-ASN.mmdb' to this directory.

If not enabled, data related to GeoIP2 is not gathered.

## Analyzing the output

The resulting output will be a CSV file after a successful execution which you can import e.g. to Excel, Libreoffice Calc, Google Sheets or any software supporting comma separated values input.

Expected output values:
- Username /IP of the editor
- Reverse IP record
- AS Organization
- Timestamp
- Editor type, false if registered, true if not
- Country
- City
- Postalcode
- Editor info link
- Comment of the edit

### Notes about results

- As said in section 'How to enable the GeoIP2 support?', the reliability of geolocation data declines with time, and is generally inaccurate
- Reverse DNS result references to current status of the records
- Geolocation data is just as accurate as the database

## MediaWiki API reference

The essential knowledge of the Wikipedia API usage, which is based on Mediawiki can be obtained here

https://www.mediawiki.org/wiki/API:Main_page

Specific page about how revisions are aquired with API:

https://www.mediawiki.org/wiki/API:Revisions


## Support
Limited and paid support might be available if asked.

## Donations

Voluntary donations are appreciated at the following Bitcoin address:

```bc1qxewvslk2k0ejzdd3ez746syqkheljp6qk7jw2r```