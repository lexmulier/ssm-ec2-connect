# SSM EC2 CONNECT UTILITY

This tool...
- ...has a convenient command line menu interface
- ...orders EC2 instances into regions & environments
- ...retrieves all new EC2 instance ID's every time
- ...connects through SSM for you 

## Installation
Create a virtualenv in the root dir of `ssm-ec2-connect`, activate it and install the requirements.txt
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

If you're using multiple AWS accounts and/or if you have AWS credential profiles you can create a `config.json` at root. If you don't use profiles (and use `default`) and just one AWS account this file is not needed.

```json
[
  {
    "account_name": "Main",
    "profile_name": "main-aws-account"
  },
  {
    "account_name": "DEV",
    "profile_name": "dev-aws-account"
  }
]
```

## Credit

This tool has been developed for (and while working for) [visualfabriq](https://github.com/visualfabriq).

