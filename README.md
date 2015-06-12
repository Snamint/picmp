# picmp
a package to ping

## Usage
``` python

import picmp

p = picmp.PICMP("www.google.com", timeout=1)
result = p.send(10)	# integer return

```