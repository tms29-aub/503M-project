#!/bin/sh
python admin.py &
python customer.py &
python frontend.py &
python inventory.py &
python order.py &
python db/db_service.py &
