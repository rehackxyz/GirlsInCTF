# Nyeow Nyeow PDF Generator

The description mentions about /nyan-nyan which is the path that you want to visit using the SSRF.
However, we made a mistake in the source code as the endpoint doesn't actually have any protection so you can read the flag directly... Oops 😬

```py
@app.route('/nyan-nyan')
def secret():
    try:
        with open(FLAG_PATH, 'r') as f:
            data = f.read()
        return make_response(data, 200)
    except Exception:
        return ('Not found', 404)
```