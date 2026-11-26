import asyncio
import time

import httpx


class RateLimiter:
    def __init__(self, requests_per_second: float = 5.0) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        self.interval = 1.0 / requests_per_second
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            delay = max(0.0, self._next - now)
            self._next = max(now, self._next) + self.interval
        if delay:
            await asyncio.sleep(delay)


class HabrClient:
    def __init__(
        self,
        *,
        requests_per_second: float = 5.0,
        concurrency: int = 10,
        retries: int = 3,
        timeout: float = 20.0,
    ) -> None:
        self.limiter = RateLimiter(requests_per_second)
        self.semaphore = asyncio.Semaphore(concurrency)
        self.retries = retries
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"Accept-Language": "ru,en-US;q=0.7,en;q=0.3"},
            follow_redirects=True,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def request(self, url: str) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            await self.limiter.acquire()
            try:
                async with self.semaphore:
                    response = await self.client.get(url)
            except (
                httpx.TimeoutException,
                httpx.TransportError,
            ) as error:
                last_error = error
                if attempt >= self.retries:
                    raise
                await asyncio.sleep(min(1.0 * (2**attempt), 8.0))
                continue

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if attempt >= self.retries:
                    response.raise_for_status()
                if retry_after and retry_after.isdigit():
                    delay = float(retry_after)
                else:
                    delay = min(1.0 * (2**attempt), 8.0)
                await asyncio.sleep(delay)
                continue

            if response.status_code >= 500:
                last_error = httpx.HTTPStatusError(
                    f"server returned {response.status_code}",
                    request=response.request,
                    response=response,
                )
                if attempt >= self.retries:
                    response.raise_for_status()
                await asyncio.sleep(min(1.0 * (2**attempt), 8.0))
                continue

            return response

        if last_error:
            raise last_error
        raise RuntimeError("HTTP request failed")
