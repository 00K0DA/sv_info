from typing import Dict
import json
from SoupMaker import SoupMaker
import dataclasses
import bs4
import re
import time

move_list_url = "https://yakkun.com/sv/move_list.htm"
pt_domain = "https://yakkun.com/sv"


@dataclasses.dataclass(frozen=True)
class Move:
    move_id: int
    name: str
    move_type: int
    category: int
    power: int
    accuracy: int
    pp: int
    target: int
    is_direct: bool
    can_protect: bool
    magic_coat: bool
    snatch: bool
    mirror_move: bool
    substitute: int
    description: str

    def toDict(self) -> dict[str, ]:
        return {
            "move_id": self.move_id,
            "name": self.name,
            "move_type": self.move_type,
            "category": self.category,
            "power": self.power,
            "accuracy": self.accuracy,
            "pp": self.pp,
            "target": self.target,
            "is_direct": self.is_direct,
            "can_protect": self.can_protect,
            "magic_coat": self.magic_coat,
            "snatch": self.snatch,
            "mirror_move": self.mirror_move,
            "substitute": self.substitute,
            "description": self.description
        }


def main():
    soup_maker = SoupMaker()
    move_url_list = get_move_url_list(soup_maker)
    move_list = []
    for move_url in move_url_list:
        move = get_move_info(soup_maker, move_url)
        move_list.append(move.toDict())
        time.sleep(2)
    with open('./move.json', "w", encoding="utf-8") as f:
        json.dump(move_list, f, indent=4)


def get_move_url_list(soup_maker: SoupMaker) -> list[str]:
    """
        SVで有効な技の一覧(URL)を取得する。
        Args:
            :param soup_maker: 自作クラスであるsoup_makerを指定する
    """
    soup = soup_maker.makeSoup(move_list_url)
    table_body = soup.select_one("#contents > div:nth-child(4) > div > table > tbody")
    tr_list = table_body.find_all("tr", class_="sort_tr")
    move_url_list = []
    for tr in tr_list:
        a_element = tr.select_one("a")
        url = pt_domain + str(a_element["href"]).lstrip(".")
        move_url_list.append(url)
    return move_url_list


def get_move_info(soup_maker: SoupMaker, url: str) -> Move:
    """
        技の情報をURLから取得する。
        Args:
            :param soup_maker: 自作クラスであるsoup_makerを指定する
            :param url: 技の情報に関するページを指定する
    """
    print(url)
    soup = soup_maker.makeSoup(url)
    table_right_soup = soup.select_one("#contents > div:nth-child(6) > table")
    table_left_soup = soup.select_one("#contents > div:nth-child(7) > table")
    move_id = get_move_id(url)
    name = str(re.findall("『.*』", soup.select_one("#database").string)[0])[1: -1]
    description = soup.select_one("#contents > div.clear > table > tr > td").string
    if description is None:
        description = soup.select_one("#contents > div:nth-child(8) > table > tr > td").text
    right_td_list = [i.contents[0] for i in table_right_soup.select("tr > td")]
    left_td_list = [i.contents[0] for i in table_left_soup.select("tr > td")]
    td_list = right_td_list + left_td_list

    m_type = get_move_type(td_list[0])
    category = get_move_category(td_list[1])
    power = get_int_value(td_list[2])
    accuracy = get_int_value(td_list[3])
    pp = int(td_list[4])
    target = get_move_target(td_list[5])
    is_direct = str(td_list[6]) == "×"
    can_protect = str(td_list[7]) == "通常"
    magic_coat = str(td_list[8]) != "×"
    snatch = str(td_list[9]) != "×"
    mirror_move = str(td_list[10]) == "できる"
    substitute = str(td_list[11]) == "貫通"

    move = Move(move_id=move_id,
                name=name,
                move_type=m_type,
                category=category,
                power=power,
                accuracy=accuracy,
                pp=pp,
                target=target,
                is_direct=is_direct,
                can_protect=can_protect,
                magic_coat=magic_coat,
                snatch=snatch,
                mirror_move=mirror_move,
                substitute=substitute,
                description=description)
    return move


def get_move_id(url: str) -> int:
    """
    input: https://yakkun.com/sv/zukan/search/?move=858
    output: 858
    """
    return int(url.split("=")[1])


def get_move_type(element: bs4.element.Tag) -> int:
    """
    input: <a href="/sv/move_list.htm?type=1"><img alt="かくとう" src="//img.yakkun.com/poke/xy_type/n1.gif"/></a>
    output: 1
    """
    return int(element["href"].split("=")[1])


def get_move_category(element: bs4.element.Tag) -> int:
    """
    input: <a class="physics" href="/sv/move_list.htm?cat=1">物理</a>
    output: 1
    """
    return int(element["href"].split("=")[1])


def get_int_value(element: bs4.element.Tag) -> int:
    """
    input: 80
    output: 80
    input: -
    output: -1
    """
    if element.string == "-":
        return -1
    else:
        return int(element.string)


def get_move_target(element: bs4.element.Tag) -> int:
    """
    input: <a class="black" href="/sv/move_list.htm?target=0">1体選択</a>
    output: 0
    """
    return int(element["href"].split("=")[1])


if __name__ == "__main__":
    main()
