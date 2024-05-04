import xlsxwriter as xl


# Handels a XLSX Document
class ExcelDoc:
    def __init__(
        self, name: str, sheets: list[str], overridename=False, in_memory=False
    ):
        # Set name of document override with cancel the addition of .xlsx
        if overridename:
            self.name = name
        else:
            self.name = name + ".xlsx"

        self.formats = {}  # Stores format objects
        self.workbook = xl.Workbook(
            self.name, {"in_memory": in_memory}
        )  # Stores the .xlsx document
        self.sheets = []  # Stores each individual sheet

        # Create each sheet
        for string in sheets:
            self.sheets.append(self.workbook.add_worksheet(string))

    @staticmethod
    def convert_position(position: tuple[int, int]):
        """Convert a position from (int, int) form to the xlsx position form"""

        return xl.utility.xl_col_to_name(position[0] - 1) + str(position[1])

    def write(
        self, sheet: int, value: str, position: tuple[int, int], formater: str = None
    ):
        """Writes a value to a single cell"""

        if formater:
            self.sheets[sheet].write(
                self.convert_position(position), str(value), self.formats[formater]
            )
        else:
            self.sheets[sheet].write(self.convert_position(position), str(value))

    def write_block(
        self,
        sheet: int,
        data: list[list],
        startposition: tuple[int, int],
        firstrowformmater: str = None,
    ):
        """Writes a 2d array to sheet starting from top left"""

        for rowIDX, row in enumerate(data):
            if rowIDX == 0 and firstrowformmater is not None:
                self.sheets[sheet].write_row(
                    self.convert_position(startposition),
                    row,
                    self.formats[firstrowformmater],
                )
            else:
                self.sheets[sheet].write_row(
                    self.convert_position(startposition),
                    row,
                )

    def close(self):
        """Closes/Exports the document"""

        self.workbook.close()

    def freeze_cells(self, sheet: int, to: tuple[int, int]):
        """Freezes cells from top left to the specified location"""

        self.sheets[sheet].freeze_panes(*to)

    def add_format(self, name: str, formatting: dict[str]):
        """Adds a formmating object to document"""

        self.formats[name] = self.workbook.add_format(formatting)
