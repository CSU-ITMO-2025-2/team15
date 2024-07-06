#!/bin/bash

python ./cli/cli.py create-user --login demo-client --password qwerty123 --email demo-client@demo.ru --role client
python ./cli/cli.py create-user --login demo-admin --password qwerty123 --email demo-demo@demo.ru --role admin

python ./cli/cli.py increase-balance --login demo-client --amount 600
python ./cli/cli.py check-balance --login demo-client

python ./cli/cli.py add-task -l demo-client