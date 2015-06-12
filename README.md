# picmp
a package to ping

based on https://github.com/samuel/python-ping/blob/master/ping.py

## Usage
``` python

import picmp

p = picmp.PICMP("www.google.com", timeout=1)
result = p.send(10, interval=0.2)	# integer return

```