import sys
from crawl import crawl_page

def main():

    if len(sys.argv)<2:
        print("no website provided")
        exit(1)
    elif len(sys.argv)>2:
        print("too many arguments provided")
        exit(1)
    else:
        print(f"starting crawl of {sys.argv[1]}")

    data = crawl_page(sys.argv[1])
    print(f"crawled through {len(data.keys())} sites")
    
    print(data.values())

if __name__ == "__main__":
    main()
