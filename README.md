# ntlmSpray
Small, single-file Python 3 script for spraying credentials at NTLM-protected HTTP endpoints.

`ntlmSpray.py` automates credential spraying against NTLM-protected HTTP endpoints.  
It cycles through a small set of passwords, waits between rounds to respect lockout windows, and stops once every targeted user has a valid password.

## Quick start

```bash
# install dependencies
python3 -m pip install requests requests_ntlm colorama

# run a spray
python3 ntlmSpray.py \
  --url https://target.example.com \
  --userfile users.txt \
  --passfile passwords.txt \
  --domain CONTOSO

Note: It is strongly advised to determine the target environment’s password lockout policy before running this tool. This helps ensure accounts are not unintentionally locked out during an authorized penetration test.
