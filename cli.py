from cpst.utils import PathFinder


def main():
    pf = PathFinder("resources")
    fp = pf.get_single_file("cpf2013.txt")
    print(fp)

if __name__ == "__main__":
    main()
