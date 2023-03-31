import xlsxwriter as xl


class ExcelDoc:
    def __init__(
        self, name: str, sheets: list[str], overridename=False, in_memory=False
    ):
        if overridename:
            self.name = name
        else:
            self.name = name + ".xlsx"

        self.formats = {}
        self.workbook = xl.Workbook(self.name, {"in_memory": in_memory})
        self.sheets = []

        for string in sheets:
            self.sheets.append(self.workbook.add_worksheet(string))

    @staticmethod
    def convert_position(position: tuple[int, int]):
        return xl.utility.xl_col_to_name(position[0] - 1) + str(position[1])

    def write(
        self, sheet: int, value: str, position: tuple[int, int], formater: str = None
    ):
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
        for rowIDX, row in enumerate(data):
            for colIDX, val in enumerate(row):
                if rowIDX == 0 and firstrowformmater is not None:
                    self.sheets[sheet].write(
                        self.convert_position(
                            (startposition[0] + colIDX, startposition[1] + rowIDX)
                        ),
                        val,
                        self.formats[firstrowformmater],
                    )
                else:
                    self.sheets[sheet].write(
                        self.convert_position(
                            (startposition[0] + colIDX, startposition[1] + rowIDX)
                        ),
                        val,
                    )

    def close(self):
        self.workbook.close()

    def freeze_cells(self, sheet: int, to: tuple[int, int]):
        self.sheets[sheet].freeze_panes(*to)

    def add_format(self, name: str, formatting: dict[str]):
        self.formats[name] = self.workbook.add_format(formatting)
