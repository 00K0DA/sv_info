from typing import Dict, List, Tuple
import json
from SoupMaker import SoupMaker
import dataclasses
import bs4
import re
import time
from MyLogger3 import MyLogger
from pathlib import Path
import urllib.request

pokemon_list_url = "https://yakkun.com/sv/zukan/"
zukan_url_template = "https://yakkun.com{}"
logger = MyLogger("Poke Scrape")
image_dir_path = Path(Path(__file__).parent, "images")


@dataclasses.dataclass(frozen=True)
class PokemonSv:
    pokemon_id: str
    name: str
    type_1: int
    type_2: int | None
    ability_1: int
    ability_2: int | None
    hidden_ability: int
    h: int
    a: int
    b: int
    c: int
    d: int
    s: int
    levelMoves: List[int]
    machineMoves: List[int]
    eggMoves: List[int]
    imageUrl: str

    def toDict(self) -> dict[str,]:
        return {
            "pokemon_id": self.pokemon_id,
            "name": self.name,
            "type_1": self.type_1,
            "type_2": self.type_2,
            "ability_1": self.ability_1,
            "ability_2": self.ability_2,
            "hidden_ability": self.hidden_ability,
            "h": self.h,
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d,
            "s": self.s,
            "levelMoves": self.levelMoves,
            "machineMoves": self.machineMoves,
            "eggMoves": self.eggMoves,
        }

    def saveImage(self, path: Path):
        headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"}
        request = urllib.request.Request(self.imageUrl, headers=headers)
        with urllib.request.urlopen(request) as web_file:
            data = web_file.read()
            with open(Path(path, "{}.gif".format(self.pokemon_id)), mode='wb') as local_file:
                local_file.write(data)


def main():
    soup_maker = SoupMaker()
    pokemon_url_list = get_pokemon_url_list(soup_maker)

    all_pokemon_count = len(pokemon_url_list)
    now_pokemon_count = 0
    poke_list = []
    for pokemon_url in pokemon_url_list:
        poke = get_pokemon_info(soup_maker, pokemon_url)
        poke.saveImage(image_dir_path)
        time.sleep(1)
        poke_list.append(poke)
        now_pokemon_count += 1
        logger.info("{}/{}".format(now_pokemon_count, all_pokemon_count))

    poke_dict_list = [poke.toDict() for poke in poke_list]

    with open('./pokemon.json', "w", encoding="utf-8") as f:
        json.dump(poke_dict_list, f, indent=4)


def get_pokemon_url_list(soup_maker: SoupMaker) -> List[str]:
    """
        SVで使えるポケモンの一覧を(URL)を取得する。
        Args:
            :param soup_maker: 自作クラスであるsoup_makerを指定する
    """
    soup = soup_maker.makeSoup(pokemon_list_url)
    table_body = soup.select_one("#contents > div.pokemon_list_box > ul.pokemon_list")
    poke_url_list = [zukan_url_template.format(li.select_one("a")["href"]) for li in
                     table_body.find_all("li", class_="haszukan")]
    return poke_url_list


def get_pokemon_info(soup_maker: SoupMaker, url: str) -> PokemonSv:
    soup = soup_maker.makeSoup(url)
    name = soup.select_one("head > meta:nth-child(5)")["content"].split("｜")[0]
    logger.info("name is {}".format(name))
    poke_id = url.split("/")[-1]
    type1, type2 = getType(soup)

    table_soup = soup.select_one("#stats_anchor > table")
    td_list = table_soup.select("tr > td.left")
    h = int(td_list[0].text.lstrip().split("(")[0])
    a = int(td_list[1].text.lstrip().split("(")[0])
    b = int(td_list[2].text.lstrip().split("(")[0])
    c = int(td_list[3].text.lstrip().split("(")[0])
    d = int(td_list[4].text.lstrip().split("(")[0])
    s = int(td_list[5].text.lstrip().split("(")[0])
    ability_list = [int(td["href"].split("=")[1]) for td in soup.select("tr > td.c1 > a")]
    if len(ability_list) == 1:
        ability_1 = ability_list[0]
        ability_2 = None
        hidden_ability = None
    elif len(ability_list) == 2:
        ability_1 = ability_list[0]
        ability_2 = None
        hidden_ability = ability_list[1]
    else:
        ability_1 = ability_list[0]
        ability_2 = ability_list[1]
        hidden_ability = ability_list[2]

    move_tr_list = [tr for tr in soup.select("#move_list > tr") if
                    "class" in tr.attrs and ("move_main_row" in tr["class"] or "move_head" in tr["class"])][1:]
    move_list_list = []
    move_list = []
    for move_tr in move_tr_list:
        if "move_head" in move_tr["class"]:
            move_list_list.append(sorted(move_list))
            move_list = []
        else:
            move_id = int(move_tr.select_one("a")["href"].split("=")[1])
            move_list.append(move_id)

    imageUrl = "https:" + soup.select_one("#base_anchor > table > tr:nth-child(2) > td > img")["src"]
    return PokemonSv(
        name=name,
        pokemon_id=poke_id,
        type_1=type1,
        type_2=type2,
        ability_1=ability_1,
        ability_2=ability_2,
        hidden_ability=hidden_ability,
        h=h,
        a=a,
        b=b,
        c=c,
        d=d,
        s=s,
        levelMoves=move_list_list[0],
        machineMoves=move_list_list[1],
        eggMoves=move_list_list[2],
        imageUrl=imageUrl
    )


def getType(soup: bs4.BeautifulSoup) -> tuple[int, int | None]:
    type_elements = soup.select("#base_anchor > table > tr:nth-child(8) > td:nth-child(2) > ul > li > a")
    type_1 = int(type_elements[0]["href"].split("=")[1])
    if len(type_elements) == 2:
        type_2 = int(type_elements[1]["href"].split("=")[1])
    else:
        type_2 = None
    return type_1, type_2


if __name__ == "__main__":
    main()
