# Collision Resistant Hash Function

> Someone in my class designed a collision-resistant hash function. He bet that
> no one can break his hash function. Prove him wrong.

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

The service listens on port `1337` and uses a fresh 512-bit key for each TCP
connection.

## Solve

```sh
python3 -m pip install pwntools
python3 release/sol/solve.py HOST=127.0.0.1 PORT=1337
```