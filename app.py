from parsers import parse
from datahandler import dataHandler
from commander import Commander

def main():
    data = dataHandler()
    parser = parse(data)
    parser.run()
    commander = Commander(data)


if __name__ == "__main__":
    main()