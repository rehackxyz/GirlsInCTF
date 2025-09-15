# My Favourite Reporting Engine V3

Challenge Author: benkyou

For My Favourite Reporting Engine V3 TLDR intended solution without source code:

- You notice that commands are being filtered. You should build a wordlist for commands that you want to use then fuzz.
- Still getting blocked. You can try unicode hex encoding in Latex to represent different characters.
- You cannot use shell commands like previous challenges to just cat the flag on the server. This suggests that the latex engine is using `-no-shell-escape`. This disables system commands. [Documentation here.](https://www.overleaf.com/learn/latex/TeX_engine_command_line_options_for_pdfTeX%2C_XeTeX_and_LuaTeX)
- With `-no-shell-escape` you can still use `\input` but you won't get a valid PDF because this throws a parser error as the flag has invalid characters (_$!?). In previous challenges, you were able to read the flag using it because we printed stdout to output so the flag will be leaked in the error, but this is not applicable here.
- Use the unicode hex encoding trick to use verbatiminput and `\def` to build /flag.txt string.

```
\documentclass{article}
\def\foo{/fla}
\def\bar{g.txt}
\def\verb{verb}
\def\atim{atim}
\^^75sepackage{\verb\atim}
\begin{document}
  \verbat^^69m^^69^^6e^^70^^75^^74{\foo\bar}
\end{document}
```