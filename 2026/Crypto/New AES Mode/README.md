# New AES mode

> We think that AES-GCM is too complicated, therefore a simplified and a more
> secure version is designed by us. This is such a revolutionary encryption
> suite!


```text
release/
├── dist/                 # files released to participants
│   └── main.py
├── service/              # private deployment files
│   ├── Dockerfile
│   ├── main.py
│   └── run.sh
├── sol/
│   └── solve.py
├── README.md
└── docker-compose.yml
```

## Run

```sh
cd release
docker compose up --build
```

The service listens on port `1337`.

## Solve

```sh
python3 -m pip install pwntools
python3 release/sol/solve.py HOST=127.0.0.1 PORT=1337
```
