import asyncio
import re
import os
import praw
from rq import get_current_job

from .strategy import AbstractParsingStrategy, NosleepParser


class LinkProcessor:
    def __init__(self, data: dict, model_uuid):
        self.data = data
        self.stories_by_link = {}
        self.conn = None
        self.model_uuid = model_uuid
        self.praw = None

    def start(self, **kwargs):
        """
        takes care of starting the asyncio loop
        and orchestrating the work
        """
        # let's create the async loop and run the actual start method

        job = get_current_job()
        if job:
            self.conn = job.connection

        # also, setup the praw instance
        self.praw = praw.Reddit(
            client_id=os.environ.get("reddit_client_id", ""),
            client_secret=os.environ.get("reddit_secret", ""),
            user_agent= f'<web>:<{os.environ.get("reddit_client_id", "")}>:<0.1> (by u/<{os.environ.get("reddit_name")}>)'
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._start())

    async def _start(self):
        await self._notify_user("EMPIRE_DID_NOTHING_WRONG")
        await self._notify_user("BEGIN_LINK_PROCESSING")
        await self._process_links()

        await self._notify_user("PROCESSING_COVER_DATA")
        await self._process_cover()

        await self._notify_user("STICHING_THE_BOOK")
        await self._stich_the_book()
        await self._notify_user("BOOK_READY_FOR_DOWNLOAD")

    async def _process_links(self):
        """ Takes care of the processing of the links """
        for index, link in enumerate(self.data["data"]):
            await self._notify_user(f"PROCESSING_LINK_NR_{index}")

            strategy = await self._determine_strategy(link["link"])
            processor = strategy(link_data=link, reddit_praw=self.praw)

            self.stories_by_link[link["link"]] = await processor.parse_data()

    async def _notify_user(self, status: str):
        self.conn.publish(self.model_uuid, status)

    async def _process_cover(self) -> dict:
        """
        Takes care of processing the cover of the book

        Return a dictionary containing both title and cover image.
        In case the title wasn't provided, it takes it from the very first
        processed link and sets it as such

        And for the cover image, it's either the image or nothing
        """

        if "cover_title" in self.data["cover"]:
            title = self.data["cover"]["cover_title"]
        else:
            title = self.stories_by_link[self.data["data"][0]["link"]]["title"]

        return {
            "title": title,
            "cover_base64": self.data["cover"].get("cover_image", None),
        }

    async def _determine_strategy(self, link: str) -> AbstractParsingStrategy:
        """
        Depending on the link provided
        chooses the parsing strategy to use
        """

        # matches anything that's /r/anything_up_to/
        subreddit_regex = r"\/r\/.+\/"
        strategies = {
            "/r/nosleep/": NosleepParser,
        }

        return strategies.get(
            re.search(subreddit_regex, link).group(0), "HERE will be a default strategy"
        )

    async def _stich_the_book(self):
        pass
