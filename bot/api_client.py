import aiohttp


class BackendClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def get_state(self) -> dict:
        return await self._get("/api/state")

    async def get_room(self, room: str) -> dict:
        return await self._get(f"/api/rooms/{room}")

    async def get_usage(self) -> dict:
        return await self._get("/api/usage")

    async def get_alerts(self) -> dict:
        return await self._get("/api/alerts")

    async def _get(self, path: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{path}", timeout=10) as response:
                if response.status == 404:
                    raise ValueError("not_found")
                if response.status >= 400:
                    raise RuntimeError(f"Backend returned HTTP {response.status}")
                return await response.json()
