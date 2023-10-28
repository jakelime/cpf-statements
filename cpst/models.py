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
        headers = []
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
                    # case 2 | 3:
                    #     headers.append(line)
                    case _:
                        datarows.append(line)

        self.algorithm_find_left_alignment(datarows)
        return

    def algorithm_find_left_alignment(
        self, rows: list[str], until_column_keyword: str = "ref"
    ):
        row = rows[0]
        ## Double pointer
        indices = []
        words = []
        print(f"{row=}")
        found_space = False
        ptr1, ptr2 = 0, 1
        while ptr1 < len(row) and ptr2 < len(row):
            word = []
            char_first_index = ptr1
            word.append(row[ptr1])
            while ptr2 < len(row):
                char_next = row[ptr2]
                if not found_space and char_next != " ":
                    word.append(char_next)
                elif not found_space and char_next == " ":
                    word.append(char_next)
                    found_space = True
                elif found_space and char_next == " ":
                    word.append(char_next)
                elif found_space and char_next != " ":
                    ptr1 = ptr2
                    ptr2 += 1
                    found_space = False
                    break
                ptr2 += 1
            word = "".join(word)
            words.append(word)
            indices.append((char_first_index, ptr2))
            if word.strip().lower() == until_column_keyword:
                break

        print(f"{words=}")
        [print(x) for x in indices]
        # [print(row) for row in rows]

    def algorithm_text_table_data1(self, rows: list[str]):
        indices = []
        words = []
        for row in rows:
            print(f"{row=}")
            iterchar = iter(row)

            word = []
            counter = 0
            number_of_spaces = 0

            c = next(iterchar)
            counter += 1
            while True:
                try:
                    if c != " ":
                        word.append(c)
                        c = next(iterchar)
                        counter += 1
                        continue
                    elif c == " " and number_of_spaces <= 0:
                        number_of_spaces += 1
                        c_next = next(iterchar)
                        counter += 1
                        if c_next == " ":
                            number_of_spaces += 1
                            continue
                        else:
                            c = c_next
                            number_of_spaces = 0

                    else:
                        words.append("".join(word))
                        word = []
                        indices.append(counter - 2)
                        number_of_spaces = 0

                        try:
                            c = next(iterchar)
                            counter += 1
                            while c == " ":
                                c = next(iterchar)
                                counter += 1
                                continue
                        except StopIteration:
                            break

                except StopIteration:
                    break

            print(f"{indices=}")
            print(f"{words=}")
            for i in range(len(indices)):
                if i == 0:
                    start = 0
                    # end = indices[i]
                    # print(f"[{start=},{end=}] {row[start:end]=}")
                else:
                    start = indices[i - 1]
                end = indices[i]
                print(f"[{start=},{end=}] {row[start:end]=}")

            break
        # [print(x) for x in rows]

    def detect_column_indices(self, row: str) -> tuple[int, ...]:
        return (1, 1)


def main():
    fp = utils.PathFinder("resources").get_single_file("cpf2013.txt")
    lg.info(f"{fp=}")
    s = CPF2014AndBefore(fp)
    s.parse_statement()


if __name__ == "__main__":
    main()
