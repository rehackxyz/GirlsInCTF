# Vibe Coded Web Application

Challenge Author: yappare

## Solution

1. After identifying the SQL injection, you need to enumerate the database to learn that it's PostgreSQL
2. Determine column count and types by using `ORDER BY` or `UNION SELECT NULL ...` tests.
3. Match the three columns `(id INT, name TEXT, price NUMERIC)` when unioning. Cast as needed.
4. Dump the flag via a UNION like:

```
q=' UNION SELECT 9999, flag::text, 0::numeric FROM flags--
```