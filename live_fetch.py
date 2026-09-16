"""Optional, bounded HTTP adapter. Never invoked by the required lab exercises."""
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import math
import time
import requests


class PoliteHtmlFetcher:
    """Callable fetcher restricted to one HTTPS origin; redirects are rejected.

    The robots policy is fetched once per adapter instance. For this teaching
    adapter, an unavailable robots file causes a conservative stop, even when a
    production crawler might use a different documented policy.
    """
    def __init__(self, user_agent, delay=2.0, max_bytes=5_000_000,
                 host="www.nbcnews.com", timeout=(5, 20)):
        if not isinstance(user_agent, str) or not user_agent.strip():
            raise ValueError("Supply a descriptive user agent with a real course contact.")
        if not math.isfinite(delay) or delay < 1:
            raise ValueError("Use a finite request delay of at least one second.")
        if type(max_bytes) is not int or max_bytes < 1:
            raise ValueError("max_bytes must be a positive integer.")
        self.host = host
        self.user_agent = user_agent
        self.delay = delay
        self.max_bytes = max_bytes
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self._robots = None
        self._robots_checked = False
        self._last_request = None

    def _wait(self):
        if self._last_request is not None:
            time.sleep(max(0, self.delay - (time.monotonic() - self._last_request)))
        self._last_request = time.monotonic()

    def _read(self, url, html_only):
        self._wait()
        try:
            with self.session.get(url, timeout=self.timeout,
                                  allow_redirects=False, stream=True) as response:
                if response.status_code != 200:
                    print(f"Skip HTTP {response.status_code}: {url}")
                    return None
                content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                if html_only and content_type not in {"text/html", "application/xhtml+xml"}:
                    print(f"Skip non-HTML content: {url}")
                    return None
                chunks, size = [], 0
                for chunk in response.iter_content(chunk_size=65536):
                    size += len(chunk)
                    if size > self.max_bytes:
                        print(f"Skip response larger than {self.max_bytes} bytes: {url}")
                        return None
                    chunks.append(chunk)
                return b"".join(chunks)
        except requests.RequestException as exc:
            print(f"Skip request failure ({type(exc).__name__}): {url}")
            return None

    def _load_robots(self):
        self._robots_checked = True
        url = f"https://{self.host}/robots.txt"
        content = self._read(url, html_only=False)
        if content is None:
            print("Live crawl stopped: robots policy could not be retrieved.")
            return
        policy = RobotFileParser(url)
        policy.parse(content.decode("utf-8", errors="replace").splitlines())
        crawl_delay = policy.crawl_delay(self.user_agent)
        if crawl_delay is not None:
            self.delay = max(self.delay, float(crawl_delay))
        request_rate = policy.request_rate(self.user_agent)
        if request_rate and request_rate.requests > 0:
            self.delay = max(self.delay, request_rate.seconds / request_rate.requests)
        self._robots = policy

    def __call__(self, url):
        try:
            parts = urlsplit(url)
            allowed = (parts.scheme == "https" and parts.hostname == self.host
                       and parts.port in (None, 443)
                       and parts.username is None and parts.password is None)
        except (ValueError, TypeError):
            return None
        if not allowed:
            return None
        if not self._robots_checked:
            self._load_robots()
        if self._robots is None or not self._robots.can_fetch(self.user_agent, url):
            print(f"Skip robots-disallowed or unverified URL: {url}")
            return None
        return self._read(url, html_only=True)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
