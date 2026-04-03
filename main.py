import sys
from listverse.listverse import Listverse
from sbs_news import sbs_news

def main_app():
    listverse = Listverse()
    sbs = sbs_news.Sbs_News()
    while True:
        option = input("[1]Random Article from Listverse [2]Latest New from SBS\nSelect: ")
        if option == "q": sys.exit(0)
        if option == "1":
            listverse.choose_subheader_and_read_content_from_a_rand_article()
        elif option == "2":
            sbs.read_a_news_article()
        else:
            continue

if __name__ == "__main__":
    main_app()