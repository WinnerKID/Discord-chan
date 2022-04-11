#  Copyright © 2022 SirOlaf
#
#  Discord Chan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Discord Chan is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Discord Chan.  If not, see <https://www.gnu.org/licenses/>.

import re
import random
import urllib.parse
import xml.etree.ElementTree as ElementTree
from typing import Optional, List
from dataclasses import dataclass

import aiohttp


SAFEBOORU_BASE_URL = "https://safebooru.org/index.php?page=dapi&s=post&q=index"
# SUBTRACTIVE_NSFW_TAGS = ["-panties", "-underwear", "-bra", "-bikini", "-ass", "-exercise", "-sweat",
#                          "-topless", "-bare_back", "-mind_control", "-clothes_lift", "-squatting",
#                          "-bodysuit", "-micro_bra", "-bdsm", "-sexually_suggestive", "-suggestive_fluid",
#                          "-blood", "-poop", "-large_breasts", "-spread_legs", "-gigantic_breasts", "-crossdressing",
#                          "-nude", "-convenient_censoring", "-latex", "-topless_male", "-crop_top", "-skirt_pull",
#                          "-no_panties", "-stomach_cutout", "-undersized_clothing", "-nipples", "-skin_tight",
#                          "-groin", "-yuri", "-yaoi", "-french_kiss", "-swimsuit", "-convenient_leg", "-tagme"]

SUBTRACTIVE_NSFW_TAGS = ["-blood", "-poop", "-tagme"]


@dataclass
class SafebooruPost:
    url: str
    post_index: int
    tag_post_count: int


def prepare_safebooru_tags(tags: List[str], *, replace_spaces: bool = True, ) -> str:
    if replace_spaces:
        tags = [re.sub(r"\s+", "_", tag) for tag in tags]

    tags += SUBTRACTIVE_NSFW_TAGS

    return "+".join([urllib.parse.quote(x) for x in tags])


async def request_safebooru(**params) -> ElementTree:
    if "tags" in params:
        params["tags"] = prepare_safebooru_tags(params["tags"])

    async with aiohttp.ClientSession() as session:
        async with session.get(SAFEBOORU_BASE_URL + "&".join(params)) as resp:
            if resp.status == 200:
                return ElementTree.fromstring(await resp.content.read())


async def get_safebooru_post_count(tags: List[str]) -> Optional[int]:
    tree = await request_safebooru(tags=tags, limit=0)
    if amount := tree.get("count"):
        return int(amount)


async def get_safebooru_posts(tags: List[str], page: int=0) -> List[str]:
    result = []
    tree = await request_safebooru(tags=tags, pid=page)

    for post in tree:
        if post_url := post.get("file_url"):
            result.append(post_url)

    return result


async def get_random_safebooru_post(tags: List[str]) -> Optional[SafebooruPost]:
    if total_post_count := await get_safebooru_post_count(tags):
        page = random.randint(0, int(total_post_count / 100))

        posts = await get_safebooru_posts(tags, page)
        post_count = len(posts)
        if post_count > 0:
            post_index = random.randint(0, post_count-1)
            return SafebooruPost(
              url=posts[post_index],
              post_index=post_index + (page * 100),
              tag_post_count=total_post_count
            )