import abc
import datetime
from pathlib import Path
import pandas as pd

if __name__ == "__main__":
    import utils
else:
    from cpst import utils

APP_NAME = "cpst"
lg = utils.init_logger(APP_NAME)


class CPFStatement(metaclass=abc.ABCMeta):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.init_data()

    def init_data(self) -> None:
        self.statement_date = datetime.datetime(year=1, month=1, day=1)
        self.df = pd.DataFrame()

    @abc.abstractmethod
    def parse_statement(self) -> pd.DataFrame:
        raise NotImplementedError


class CPF2014AndBefore(CPFStatement):
    def __init__(self, filepath: Path):
        super().__init__(filepath=filepath)

    def parse_statement(self):
        self.parse_text_file()

    def parse_text_file(self):
        datarows = []
        with open(self.filepath, "r") as reader:
            for i, line in enumerate(reader.readlines()):
                line = line.strip("\n")
                match i:
                    case 0:
                        continue
                    case 1:
                        self.statement_date = datetime.datetime(
                            year=int(line.split(" ")[-1]), month=12, day=31
                        )
                    case _:
                        datarows.append(line)

        self.algorithm_find_left_alignment(datarows)
        return

    def algorithm_find_left_alignment(
        self, rows: list[str], until_column_keyword: str = "ref"
    ):
        ## Double pointer algorithm
        indices = []
        headers = []
        datarows = []
        for i, row in enumerate(rows):
            if not row:
                break
            n = len(row)
            if i == 0:
                found_double_space = False
                ptr0 = 0

                while ptr0 < n - 1:
                    char_first_index = ptr0
                    word = []
                    c0 = row[ptr0]
                    word.append(c0)

                    found_double_space = False
                    ptr1 = ptr0 + 1
                    while ptr1 < n - 1:
                        c1 = row[ptr1]
                        c2 = row[ptr1 + 1]

                        if c1 == " " and c2 == " ":
                            found_double_space = True

                        elif found_double_space and c1 != " ":
                            ptr0 = ptr1 - 1
                            ptr1 = ptr0
                            word = "".join(word)
                            headers.append(word)
                            word = []
                            found_double_space = False
                            indices.append((char_first_index, ptr0 + 1))
                            break
                        else:
                            word.append(c1)

                        ptr1 += 1

                    ptr0 += 1

                    if ptr1 == n - 1:
                        # Handles the last case, where there are not double spaces behind
                        word.append(row[ptr1])
                        word = "".join(word)
                        headers.append(word)
                        indices.append((char_first_index, ptr1 + 1))
                        break

                    if headers[-1].strip().lower() == until_column_keyword:
                        break

            elif i == 1:
                # 2nd row of column, throw away
                continue

            else:
                if not indices:
                    raise RuntimeError("no indices detected from headers")
                data = {}
                for header, (x, y) in zip(headers, indices):
                    data[header.strip().lower()] = row[x:y].strip()
                datarows.append(data)

        df = pd.DataFrame(datarows)
        return df

    def detect_column_indices(self, row: str) -> tuple[int, ...]:
        return (1, 1)


def main():
    fp = utils.PathFinder("resources").get_single_file("cpf2013.txt")
    lg.info(f"{fp=}")
    s = CPF2014AndBefore(fp)
    s.parse_statement()


if __name__ == "__main__":
    main()
