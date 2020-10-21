import aiohttp
from typing import Sequence, Union, Dict, Optional
import json

Number = Union[int, float]
JSONType = Union[Number, str, None, dict, list]


class Session:
    base_url = "https://minebattle.ru/api/"
    raise_on_error = False

    def __init__(self, token: str):
        self.token = token
        self.session = None

    async def request(self, method: str, **params: JSONType) -> "Response":
        params["access_token"] = self.token
        async with self.session.post(
            self.base_url + method, 
            json=params,
            headers={'Content-Type': 'application/json'},
        ) as req:
            data = await req.json()
            success = ("response" in data)
            return Response(
                data=data,
                success=success,
                request_info={
                    "method": method,
                    "params": params
                }
            )

    def __call__(self, *args, **kwargs) -> "Response":
        return self.request(*args, **kwargs)

    async def __aenter__(self) -> "Session":
        return self.open()

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close()

    def open(self) -> "Session":
        self.session = aiohttp.ClientSession()
        return self

    async def close(self) -> None:
        await self.session.close()

    def __getattr__(self, attr) -> "FancyProxy":
        return FancyProxy(self, [attr])


class FancyProxy:
    def __init__(self, session: Session, method: Sequence[str]):
        self.session = session
        self.method = method

    def __getattr__(self, attr: str) -> "FancyProxy":
        return FancyProxy(self.session, [*self.method, attr])

    def __call__(self, **params: JSONType) -> "Response":
        return self.session.request(
            method=".".join(self.method),
            **params
        )


class Response:
    show_data = False
    def __init__(self, data: Dict[str, JSONType], success: bool, request_info: Dict):
        self.data = data
        self.success = success
        self.request_info = request_info

    @property
    def msg(self) -> Optional[JSONType]:
        return self.data.get("response", {}).get("msg")

    @property
    def error_code(self) -> Optional[JSONType]:
        return self.data.get("error", {}).get("error_code")

    @property
    def error_msg(self) -> Optional[JSONType]:
        return self.data.get("error", {}).get("error_msg")
    
    def __str__(self) -> str:
        return "pydomosed Response object: {method} request{data}".format(
            method=self.request_info["method"],
            data="" if not self.show_data else (":\n%s" % json.dumps(self.data, indent=4))
        )

