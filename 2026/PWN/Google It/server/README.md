# Native Starlight server

Organizer-only build and deployment bundle. It exposes only TCP `1338`; the
Chrome page server remains on the target container's loopback interface.

```sh
docker compose -f compose.yml up --build -d
nc 127.0.0.1 1338
```

The default `flag.txt` is mounted read-only into `target`; it is never copied
into the image and `gate` has no flag mount. For production, keep the flag
outside this directory
