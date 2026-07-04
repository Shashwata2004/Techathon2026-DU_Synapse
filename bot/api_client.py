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

    async def toggle_device(self, device_id: str) -> dict:
        return await self._post(f"/api/demo/toggle/{device_id}")

    async def set_room_all_on(self, room_id: str) -> dict:
        return await self._post(f"/api/demo/set-room-all-on/{room_id}")

    async def set_room_all_off(self, room_id: str) -> dict:
        return await self._post(f"/api/demo/set-room-all-off/{room_id}")

    async def reset_demo(self) -> dict:
        return await self._post("/api/demo/reset")

    async def _get(self, path: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{path}", timeout=10) as response:
                if response.status == 404:
                    raise ValueError("not_found")
                if response.status >= 400:
                    raise RuntimeError(f"Backend returned HTTP {response.status}")
                return await response.json()

    async def _post(self, path: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}{path}", timeout=10) as response:
                if response.status == 404:
                    raise ValueError("not_found")
                if response.status >= 400:
                    detail = await response.text()
                    raise RuntimeError(f"Backend returned HTTP {response.status}: {detail}")
                return await response.json()
