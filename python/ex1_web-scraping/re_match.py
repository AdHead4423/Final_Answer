import re
def split_address(address):
    pattern = r"^(東京都|北海道|(?:京都|大阪)府|.{2,3}県)(.*?[市区町村])(.+)$"

    match = re.match(pattern,address)

    if match:
        prefecture = match.group(1)
        city = match.group(2)
        rest = match.group(3)

        building_pattern = r"^(\D+)([0-9０-９\-ー−丁目条番号地\s,，]+)(.*)$"
        building_match = re.match(building_pattern,rest)

        if building_match:
            town = building_match.group(1).strip()
            street = building_match.group(2).strip()
            building = building_match.group(3).strip()
        else:
            street = rest.strip()
            building = ""

        city += town

        return prefecture,city,street,building
    else:
        return "","","",""


test_address = "神奈川県横浜市中区山下町市場通191-10"
pref, city, street, building = split_address(test_address)

print("都道府県：{}".format(pref))
print("市区町村：{}".format(city))
print("番地：{}".format(street))
print("建物名：{}".format(building))