import os

from pyairtable import Api, Table
from pyairtable.formulas import match
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

AIRTABLE_TOKEN = 'patNEKm0aXuQ8djrb.0444341226d0539c89e8d55e0ab4a181410446dd1d2bf4b5b2d9131ace6061e2'
BASE_ID = 'appjnZkgUkiB12Dq3'

api = Api(AIRTABLE_TOKEN)
table = api.table(BASE_ID, 'tbl92uPxxsNE8PHUA')

val = table.all()
print(val)

table.create({'ticker': 'John','timestamp': 'Doe','52_week_high': 25, '52_week_low': 10, '6_month_high': 20, '6_month_low': 15, '1_month_high': 18, '1_month_low': 12})