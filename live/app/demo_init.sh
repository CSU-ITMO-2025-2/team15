#!/bin/bash

echo "Create demo client"
python ./cli/cli.py create-user --login demo-client --password qwerty123 --email demo-client@demo.ru --role client
echo "Create demo admin"
python ./cli/cli.py create-user --login demo-admin --password qwerty123 --email demo-demo@demo.ru --role admin

echo "Add some mone to client"
python ./cli/cli.py increase-balance --login demo-client --amount 600
echo "Add check client balance"
python ./cli/cli.py check-balance --login demo-client

echo "Add tasks for demo-user"
python ./cli/cli.py add-task -l demo-client