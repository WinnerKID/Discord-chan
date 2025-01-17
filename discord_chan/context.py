from datetime import datetime

from discord import HTTPException, Message
from discord.ext.commands import Context

from .menus import ConfirmationMenu, DCMenuPages, NormalPageSource, PartitionPaginator


class SubContext(Context):
    async def send(self, content=None, **kwargs) -> Message:
        if content:
            content = str(content)

        # TODO: handle more args than just content
        # If there was more than just content ex: embeds they don't get sent
        # but this should never really be used, so this is ok?
        if content and len(str(content)) > 2000:
            paginator = PartitionPaginator(prefix=None, suffix=None, max_size=1985)
            paginator.add_line(content)

            source = NormalPageSource(paginator.pages)

            menu = DCMenuPages(source)

            await menu.start(self, wait=True)
            assert menu.message is not None
            return menu.message

        return await super().send(content=content, **kwargs)

    @property
    def created_at(self) -> datetime:
        """
        :return: When ctx.message was created
        """
        return self.message.created_at

    async def confirm(self, message: str | None = None) -> Message | None:
        """
        Adds a checkmark to ctx.message.
        If unable to sends <message>
        """
        try:
            await self.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        except HTTPException:
            message = message or "\N{WHITE HEAVY CHECK MARK}"
            return await self.send(message)

    async def deny(self, message: str | None = None) -> Message | None:
        """
        Adds a cross to ctx.message.
        If unable to sends <message>
        """
        try:
            await self.message.add_reaction("\N{CROSS MARK}")
        except HTTPException:
            message = message or "\N{CROSS MARK}"
            return await self.send(message)

    async def prompt(
        self, message: str | None = None, *, owner_id: int | None = None, **send_kwargs
    ) -> bool:
        """
        Prompt for <message> and return True or False
        """
        message = message or "confirm?"
        owner_id = owner_id or self.author.id
        menu = ConfirmationMenu(message, owner_id=owner_id, send_kwargs=send_kwargs)
        return await menu.get_response(self)
