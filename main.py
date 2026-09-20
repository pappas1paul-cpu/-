import sys
from crawl import extract_page_data

def main():

    if len(sys.argv)<2:
        print("no website provided")
        exit(1)
    elif len(sys.argv)>2:
        print("too many arguments provided")
        exit(1)
    else:
        print(f"starting crawl of {sys.argv[1]}")

if __name__ == "__main__":
    main()
