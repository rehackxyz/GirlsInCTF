# Nyum Nyum PDF Generator

Challenge Creator: benkyou

This is the "patched" version of Nyeow Nyeow :P

Based on the description, the path that you need to access is /nyan-nyan which is restricted to localhost.
You need to use the SSRF but localhost addresses are being filtered.

## Solution

The technique to use is HTTP redirects to make the server fetch localhost addresses.
However, we do not know what port is the application is listening on.

There are a couple of methods you can use to figure this out:
1. If you redirect to a port that is open, you get a valid PDF response, else it fails.
2. If you look at the server response headers, you'll learn that this is a Python web application. Common Python web frameworks like Flask serve on port 5000 by default. You can test this using the home page first.
3. You can also use a wordlist of common HTTP ports to fuzz.

Payload:

```
https://httpbin.org/redirect-to?url=http://127.0.0.1:5000/nyan-nyan
```