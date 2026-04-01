import sys
from listverse.listverse import Listverse

def main_app():
    while True:
        option = input("[1]Random Article from Listverse\nSelect: ")
        if option == "q": sys.exit(0)
        if option == "1":
            listverse = Listverse()
            listverse.choose_subheader_and_read_content_from_a_rand_article()
        else:
            continue

if __name__ == "__main__":
    main_app()