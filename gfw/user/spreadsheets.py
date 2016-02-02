# Global Forest Watch API
# Copyright (C) 2015 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import webapp2

import gspread
import string
from oauth2client.client import SignedJwtAssertionCredentials

from appengine_config import runtime_config

ATTRIBUTE_MAP = {
    'Last': 'name',
    'Email': 'email',
    'Position': 'job',
    'Address': 'country'
}

def character_for_number(number):
    return string.ascii_uppercase[number-1]

class TesterSpreadsheet:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds']
        config = runtime_config['google_sheets_service_account']
        credentials = SignedJwtAssertionCredentials(config['client_email'],
            config['private_key'].encode(), scope)
        gc = gspread.authorize(credentials)

        self.spreadsheet = gc.open_by_key(
            '1VD-1lf256tZXOmu8Q0HmQx7G4jg1fDvHhDHQeluNPz4')
        self.worksheet = self.spreadsheet.get_worksheet(0)

    def create_or_update(self, profile):
        values = self.worksheet.get_all_values()

        number_of_columns = len(values[0])
        last_column_index = character_for_number(number_of_columns)

        try:
            cell = self.worksheet.find(profile.key.id())
            new_row_index = cell.row
        except Exception:
            number_of_rows = len(values)
            new_row_index = number_of_rows+1

        cell_range = 'A{0}:{1}{2}'.format(new_row_index, last_column_index, new_row_index)
        cell_list = self.worksheet.range(cell_range)

        for cell in cell_list:
            cell_name = self.worksheet.cell(1, cell.col).value

            if (not hasattr(profile, 'sign_up')) or (profile.sign_up != 'yes'):
                cell.value = ''
                continue

            if cell_name == 'user_key':
                cell.value = profile.key.id()
                continue

            if cell_name in ATTRIBUTE_MAP:
                attribute_name = ATTRIBUTE_MAP[cell_name]

                if hasattr(profile, attribute_name):
                    cell.value = getattr(profile, attribute_name)

        self.worksheet.update_cells(cell_list)
