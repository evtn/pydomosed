from aiohttp import web
from typing import Callable, Any
import ssl

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_default_certs()


class Hook:
    def __init__(self, session, url: str, port: int):
        if not url.startswith("http"):
            url = "http://%s" % url
        self.url = url
        self.port = port
        self.session = session
        self.runner = None

    def get_url(self) -> str:
        return "%s:%s/transfer" % (self.url, self.port)

    async def start(self, callback: Callable[[dict], None]) -> None:
        set_url = await self.session.request(
            method="merchants.webhook.set",
            url=self.get_url()
        )
        if not set_url.success:
            raise ValueError(set_url.data["error"])

        routes = web.RouteTableDef()

        @routes.post('/transfer')
        async def transfer(request):
            response = await request.json()
            hash_ = md5.new(
                "{token}{amount}{from_id}".format(
                    token=self.session.params["access_token"],
                    amount=response.get("amount"),
                    from_id=response.get("fromId")
                )
            ).digest()
            if response.get("hash") != hash_:
                raise ValueError("Invalid hash")
            callback(response)
            return web.Response(text="ok")
        
        app = web.Application()
        app.add_routes(routes)

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host=self.url.split("/")[-1], port=self.port, ssl_context=ssl_context)
        await site.start()

    async def stop(self) -> None:
        await self.runner.cleanup()
