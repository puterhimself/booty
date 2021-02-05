
from processor import processor
from data.databox import databox


def main():
    theBox = databox()
    pro = processor(theBox)
    pro.run()

if __name__ == "__main__":
    main()