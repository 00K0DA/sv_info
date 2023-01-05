from MyLogger3 import MyLogger
from SoupMaker import SoupMaker
import dataclasses
import json

ability_list_url = "https://yakkun.com/sv/ability_list.htm"


@dataclasses.dataclass(frozen=True)
class Ability:
    ability_id: int
    name: str
    description: str

    def toDict(self):
        return {
            "ability_id": self.ability_id,
            "name": self.name,
            "description": self.description
        }


def main():
    soup_maker = SoupMaker()
    soup = soup_maker.makeSoup(ability_list_url)
    table_soup = soup.select_one("#contents > div:nth-child(8) > table")
    tr_list = table_soup.select("tr")
    ability_list = []
    for tr in tr_list:
        td_list = tr.select("td")
        if len(td_list) == 0:
            continue
        else:
            ability_id = int(td_list[0].select_one("a")["href"].split("=")[1])
            ability_name = td_list[0].text
            description = td_list[1].text
            ability = Ability(ability_id=ability_id, name=ability_name, description=description)
            ability_list.append(ability.toDict())

    with open('./ability.json', "w", encoding="utf-8") as f:
        json.dump(ability_list, f, indent=4)


if __name__ == "__main__":
    main()
