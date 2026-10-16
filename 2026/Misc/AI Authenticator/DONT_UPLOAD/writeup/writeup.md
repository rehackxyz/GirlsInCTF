# AI Authenticator
- The solution is to create an adversarial image that score more than 80% based on the face embedding numpy file given, generated from insightface model.
- There are many algorithm to generate adversarial image for high score, I using CMA-ES algorithm for high efficiency.
- Run the `generate.py` script multiple times (each time require several minutes) for the same face until it reached 90% score.
- Once got the final image you can just send to the server by the following bashcommand:
```bash
echo "data:image/png;base64,$(cat final_cma.png| base64 -w 0)" > base64.txt
curl http://localhost:1337/check --data-binary "@base64.txt"
```
- You will get the flag in the output:
```json
{
  "access": "granted",
  "score": 85.85182428359985,
  "text": "Welcome X! Here is your flag: gctf26{4dv3rs4rial_1m4G3_a7t@cK}"
}
```
