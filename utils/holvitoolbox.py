from datetime import datetime
import logging
import pprint
#import functools

from django.core.files.uploadedfile import InMemoryUploadedFile

import xlrd

class ParseError(Exception):
    """Raised when the data has invalid value"""

    pass

logger = logging.getLogger(__name__)
class HolviToolbox:
    """
    Contains various helper methods to handle Holvi data
    """

    @staticmethod
    def parse_account_statement(filename: InMemoryUploadedFile):
        """
        Parses Holvi account statement Excel in new or old header format

        Expected fields:
        "Date"/"Payment date", "Amount", "Currency", "Counterparty", "Description", "Reference",
        "Message", "Filing ID"
5
        Unused fields:
        "Execution date" after "Payment date"
        """
        sheet = xlrd.open_workbook(file_contents=filename.read()).sheet_by_index(0)

        # program logic uses the following format of headers
        fields_keys_english_to_use = ["Payment date", "Execution date", "Amount", "Currency", "Counterparty", "Description", "Reference", "Message","Filing ID"]
        legacy_fields_keys_english_to_use = ["Payment date", "Amount", "Currency", "Counterparty", "Description", "Reference", "Message","Filing ID"]
        # they might be given as one of the following holvi xls
        fields_keys_english = [["Payment date", "Date"], ["Execution date", ""], ["Amount"], ["Currency"], ["Counterparty"], ["Description"], ["Reference"], ["Message"], ["Filing ID"]]
        fields_keys_finnish = [["Maksupvm"], ["Kirjauspäivä"], ["Summa"], ["Valuutta"], ["Vastapuoli"], ["Kuvaus"], ["Viite"], ["Viesti"], ["Arkistointitunnus"]]
        legacy_fields_keys_english = [["Payment date", "Date"], ["Amount"], ["Currency"], ["Counterparty"], ["Description"], ["Reference"], ["Message"], ["Filing ID"]]
        date_fields_english = fields_keys_english[0]
        date_fields_finnish = fields_keys_finnish[0]

        # initilizing values
        headers = []
        items = []
        rowIterator = enumerate(sheet.get_rows())
        row = None

        def removeheaders():

            try:
                row = (row_index, row) = rowIterator.__next__()
            except (StopIteration):
                raise ParseError("Did not find payment data header line beginning. searched for: " + (date_fields_finnish + date_fields_english))

            return row

        # remove summary rows from rowIterator as a side effect
        row = removeheaders()

        while (row[0].value not in (date_fields_english + date_fields_finnish)):
            row = removeheaders()

        def checkHeaders(headers, localizedPossibleHeaders):
         for (header, possibleHeaders) in zip(headers, localizedPossibleHeaders):
                if header in possibleHeaders:
                    pass
                else:
                     raise ParseError("Holvi xls headers did not match expected. \n Expected: " + str(possibleHeaders) + "\n Got: " + str(header))


        # read headers from header line
        headers = [field.value for field in row]
        # mutate
        # check language
        if headers[0] in date_fields_finnish:
            checkHeaders(headers, fields_keys_finnish)


            headers = fields_keys_english_to_use
        else:
            checkHeaders(headers, fields_keys_english)


        # Extract row data as dictionary with headers as keys

        # rest should be the datalines to parse as information
        for row_index, row in rowIterator:
            item = dict(zip(headers, [field.value for field in row]))
            # Parse payment date
            try:
                # Try new field name first, present since around 2021-03-21
                date_parsed = datetime.strptime(
                    item["Payment date"], "%d %b %Y"  # "9 Mar 2021"
                )
                # Set time to noon as new format has no payment time
                item["Date_parsed"] = date_parsed.replace(hour=12, minute=00)
            except KeyError:
                # Fallback: try old field name, preset in 2020-06-10
                # If we get second KeyError, file header format is invalid and we let import crash out
                item["Date_parsed"] = datetime.strptime(
                    item["Payment date"], "%d %b %Y, %H:%M:%S"  # "8 Jan 2020, 09:35:43"
                )
            except ValueError:
                date_parsed = datetime.strptime(
                    item["Payment date"], "%d.%m.%Y"  # 1.2.2022
                )
                item["Date_parsed"] = date_parsed.replace(hour=12, minute=00)

            # Force reference field to be strings
            item["Reference"] = str(item["Reference"])
            item["Message"] = str(item["Message"])

            # Add meta fields
            item["source_file"] = filename
            item["source_row"] = row_index + 1

            items.append(item)

        return items
