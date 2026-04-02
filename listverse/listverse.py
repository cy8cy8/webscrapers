import random, requests, pydoc, textwrap, sys
from bs4 import BeautifulSoup
from lxml import html
from constants import HEADERS

class Listverse:
    """
    A class to retrieve the a random article from Listverse
    """
    def __init__(self):
        self.sitemap_url = "https://listverse.com/category-sitemap.xml"
        self.urls_excluded = ("https://listverse.com/shopping/", "https://listverse.com/podcast", "https://listverse.com/site-news/")

    def _get_rand_url_from_category_sitemap(self) -> str:
        """
        Fetches the Listverse category sitemap and selects a random category URL.
        """
        try:
            response = requests.get(self.sitemap_url, HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, features='xml')

            # XML sitemaps use <loc> tags for URLs
            links = [
                loc.text.strip()
                for loc in soup.find_all('loc')
                if not loc.text.startswith(self.urls_excluded) # accepts a tuple of strings
            ]
            if not links: return "No links found."

            # Return a random link from the list of extracted strings
            selected_link = random.choice(links)
            print(f"Selected Category URL: {selected_link}")
            return selected_link
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _get_rand_article_url(self) -> str:
        try:
            category_url = self._get_rand_url_from_category_sitemap()
            total_pages = self._get_total_pages_for_category(category_url)
            random_page = random.randint(1, total_pages)
            print(f"Random page: {random_page}/{total_pages}")
            links = self._get_article_links_from_page(category_url, random_page)
            if not links:
                print("No articles found on selected page.")
                return None
            link = random.choice(links)
            print(f"Selected Article: {link}")
            return link
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def _get_article_subheaders(self) -> tuple:
        """
        Retrieve a list of subheaders from the Listverse article
        """
        url = self._get_rand_article_url()
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            
            # Convert HTML to an lxml tree for XPath support
            tree = html.fromstring(response.content) 
            print(f"Title: {tree.xpath("//h1")[0].text_content().strip()}")
            h2_list = []
            
            # Strategy 1: Standard H2 headers for newer
            for i in range(1, 11):
                h2_only_xpath = f"//h2[not(@*)][{i}]/text()"
                elements = tree.xpath(h2_only_xpath)
                if elements:
                    subheader = "".join(elements).strip()
                    h2_list.append(subheader)

            # Strategy 2: Fallback to div class="itemtitle" for older articles e.g. https://listverse.com/2011/04/14/top-10-national-dishes-you-should-try/
            if not h2_list:
                item_titles = tree.xpath("//div[@class='itemtitle']")
                for el in item_titles[:10]:
                    title = el.text_content().strip()
                    
                    # Look for 'itemmore' div immediately following the 'itemtitle'
                    more_info = el.xpath("./following-sibling::div[@class='itemmore']/text()")
                    
                    if more_info:
                        origin = more_info[0].strip()
                        h2_list.append(f"{title} - {origin}")
                    else:
                        h2_list.append(title)

            # Debug print
            for i, sub in enumerate(h2_list, 1):
                print(f"{i}. {sub}")

            return tree # returns a tuple

        except Exception as e:
            print(f"Content Extraction Error: {e}")
            sys.exit(1)

    def _get_article_subheader_content(self, choice: int, tree) -> str:
        """
        Retrieves content below a subheader. 
        Supports standard H2s in newer articles and the 'itemheading' div format found in older articles.
        """
        try:
            # 1. Try Standard H2 Strategy
            h2_elements = tree.xpath("//h2[not(@*)]")
            if h2_elements and choice <= len(h2_elements):
                target = h2_elements[choice-1]
                # Logic: Grab following <p> siblings until the next <h2>
                elements = target.xpath("following-sibling::p[preceding-sibling::h2[1] = $curr]", curr=target)
                if elements:
                    return "\n\n".join([e.text_content().strip() for e in elements])

            # 2. Strategy for older articles (using itemheading)
            headings = tree.xpath("//div[@class='itemheading']")
            if headings and choice <= len(headings):
                target_heading = headings[choice-1]
                content_parts = []
                
                # Look at elements immediately following the itemheading container
                for sibling in target_heading.itersiblings():
                    # Stop as soon as we hit the next <div> (as per your instructions)
                    if sibling.tag == 'div':
                        break
                    
                    # Only collect <p> tags
                    if sibling.tag == 'p':
                        # .text_content() extracts text from the <p> and any <a> tags as plaintext
                        text = sibling.text_content().strip()
                        if text:
                            content_parts.append(text)
                
                return "\n\n".join(content_parts)

        except Exception as e:
            print(f"Error extracting subheader content: {e}")
            
        return "No content found."

        # Listverse article XPath - 1st <h2> without attributes + subsequent <p> content (10 in total in a Listverse article) until the next <h2> without attributes is found
        # "Give me header #{num}, plus every paragraph whose closest previous header is that same #{num}""
        # ((//h2[not(@*)])[1] | (//h2[not(@*)])[1]/following-sibling::p[preceding-sibling::h2[not(@*)][1] = (//h2[not(@*)])[1]])

    def choose_subheader_and_read_content_from_a_rand_article(self) -> None:
        """
        Fetch the latest random Listverse article from a random category can pick a subheader to fetch and read the content beneath it. 
        """
        tree = self._get_article_subheaders()
        while True:
            try: 
                choice = input("Choose (1-10) or [q]uit: ")
                if choice == "q": break
                choice = int(choice)
                if not (1 <= choice <= 10): continue
            except ValueError:
                continue
            article = self._get_article_subheader_content(choice=choice, tree=tree)
            wrapped_article = textwrap.fill(article, width=70)
            pydoc.pager(wrapped_article)

    def _get_total_pages_for_category(self, category_url: str) -> int:
        try:
            response = requests.get(category_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            page_links = []
            for a in soup.select('li a'):
                href = a.get('href')
                if href and 'page' in href:
                    page_links.append(href)

            page_numbers = []
            for href in page_links:
                last_part = href.rstrip('/').split('/')[-1]
                if last_part.isdigit():
                    page_numbers.append(int(last_part))

            return max(page_numbers) if page_numbers else 1

        except Exception as e:
            print(f"Pagination error: {e}")
            return 1
        
    def _get_article_links_from_page(self, category_url: str, page_num: int) -> list[str]:
        try:
            if page_num == 1:
                url = category_url
            else:
                url = f"{category_url.rstrip('/')}/page/{page_num}/"

            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            articles:list = soup.find_all('h3', attrs={})[:-4] # delete: last 4 articles are "Editor's Picks" which are displayed in all pages
            # print(articles)

            return [a.find('a')['href'] for a in articles if a.find('a')]

        except Exception as e:
            print(f"Page fetch error: {e}")
            return []