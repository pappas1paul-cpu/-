import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html,\
get_urls_from_html, get_images_from_html, extract_page_data


class TestCrawl(unittest.TestCase):
    def test_normalize_url_https(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http1(self):
        input_url = "http://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http2(self):
                input_url = "http://ww.boot.dev/blog/path"
                actual = normalize_url(input_url)
                expected = "www.boot.dev/blog/path"
                self.assertEqual(actual, expected)

    def test_normalize_url_http3(self):
                input_url = "/www.boot.dev/blog/path"
                actual = normalize_url(input_url)
                expected = "www.boot.dev/blog/path"
                self.assertEqual(actual, expected)

    def  test_get_heading_from_html_with_h1_headers(self):
            input_html = "html><body><h1>Welcome to Boot.dev</h1><main><p>Learn to code by building real projects.</p><p>This is the second paragraph.</p></main></body></html>"
            actual = get_heading_from_html(input_html)
            expected = "Welcome to Boot.dev"
            self.assertEqual(actual, expected)

    def test_get_heading_from_html_with_h2_headers(self):
        input_html = "html><body><h2>Welcome to Boot.dev</h2><main><p>Learn to code by building real projects.</p><p>This is the second paragraph.</p></main></body></html>"
        actual = get_heading_from_html(input_html)
        expected = "Welcome to Boot.dev"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_with_no_headers(self):
            input_html = """<html><body><main><p>Learn to code by building real projects.</p><p>This is the second paragraph.</p></main></body></html>"""
            actual = get_heading_from_html(input_html)
            expected = ""
            self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_single_tag(self):
            input_body = """<html><body>
                <p>Outside paragraph.</p>
                </body></html>"""
            actual = get_first_paragraph_from_html(input_body)
            expected = "Outside paragraph."
            self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_multiple_tags(self):
            input_body = """<html><body>
                <p>Outside paragraph.</p>
                <p>Main paragraph.</p>
            </body></html>"""
            actual = get_first_paragraph_from_html(input_body)
            expected = "Outside paragraph."
            self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_tag(self):
            input_body = """<html><body>
                <main>    
                </main>
            </body></html>"""
            actual = get_first_paragraph_from_html(input_body)
            expected = ""
            self.assertEqual(actual, expected)   

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com/about"><span>About</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/about"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/contact"><span>Contact</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/contact"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_missing_href(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a>No Link</a><a href="/blog">Blog</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/blog"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler-test.com/logo.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/assets/hero.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/assets/hero.jpg"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_missing_src(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img><img src="/footer.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/footer.png"]
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)
    
    def test_extract_page_data_no_heading(self):
            input_url = "https://crawler-test.com"
            input_body = """<html><body>
                <h1></h1>
                <p>This is the first paragraph.</p>
                <a href="/link1">Link 1</a>
                <img src="/image1.jpg" alt="Image 1">
            </body></html>"""
            actual = extract_page_data(input_body, input_url)
            expected = {
                "url": "https://crawler-test.com",
                "heading": "",
                "first_paragraph": "This is the first paragraph.",
                "outgoing_links": ["https://crawler-test.com/link1"],
                "image_urls": ["https://crawler-test.com/image1.jpg"],
            }
            self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_img_links(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1></h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
            <img src="/image1.jpg" alt="Image 1">
            <img src="/image2.jpg" alt="Image 2">
            </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
           "url": "https://crawler-test.com",
           "heading": "",
           "first_paragraph": "This is the first paragraph.",
           "outgoing_links": ["https://crawler-test.com/link1",
                              "https://crawler-test.com/link2"],
           "image_urls": ["https://crawler-test.com/image1.jpg",
                          "https://crawler-test.com/image2.jpg"],
            }
        self.assertEqual(actual, expected)

    def test_extract_page_data_no_img_links(self):
            input_url = "https://crawler-test.com"
            input_body = """<html><body>
                <h1></h1>
                <p>This is the first paragraph.</p>
                </body></html>"""
            actual = extract_page_data(input_body, input_url)
            expected = {
               "url": "https://crawler-test.com",
               "heading": "",
               "first_paragraph": "This is the first paragraph.",
               "outgoing_links": [],
               "image_urls": [],
                }
            self.assertEqual(actual, expected)   
if __name__ == "__main__":
    unittest.main()