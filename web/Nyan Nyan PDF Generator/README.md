# Nyan Nyan PDF Generator

The hint in the description suggests /secret, but this path is protected.
The goal is to exploit the SSRF vulnerability to read the flag, since the request made by the server will originate from localhost.

## Solution

```
http://127.0.0.1/secret
```