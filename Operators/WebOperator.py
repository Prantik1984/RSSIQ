import trafilatura
class WebOperator:
    """"
    Performs various web operations
    """

    def get_webpage_text(self, url: str) -> str:
        """"
        downloads a webpage
        """
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"result": False}

        web_content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        return {"result": True, "content": web_content}