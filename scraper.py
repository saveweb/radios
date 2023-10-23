import os
import json
import requests as rq

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"
national_api = "https://apppc.cnr.cn/national"
local_list_api = "https://apppc.cnr.cn/local/list"
local_api = "https://apppc.cnr.cn/local"


def to_disk(path: str, radios):
    # radios = ["data"]["categories"][0]
    with open(path, "w") as f:
        for detail in radios["detail"]:
            _id: str = detail["id"]
            newsType: str = detail["newsType"]
            name: str = detail["name"]
            description: str = detail["description"]
            logo_url: str = detail["other_info6"]
            stream_url: str = detail["other_info11"][0]["url"]

            f.write("\t"
            .join([
                _id if _id else "null",
                name if name else "null",
                newsType if newsType else "null",
                stream_url if stream_url else "null",
                logo_url if logo_url else "null",
                description if description else "null",
            ]) + "\n"
            )


def main():
    sess = rq.session()
    sess.headers["User-Agent"] = UA
    national_json = sess.get(national_api).json()
    with open("national.json", "w") as f:
        f.write(
            json.dumps(national_json, ensure_ascii=False, separators=(',', ':'), indent=2)
        )
    radios = national_json["data"]["categories"][0]
    to_disk(path="national.txt", radios=radios)

    local_json_options = sess.get(local_list_api).json()
    with open("local_options.json", "w") as f:
        f.write(json.dumps(local_json_options, ensure_ascii=False, separators=(',', ':'), indent=2))
    for place in local_json_options["liveChannelPlace"]:
        place_id = place["id"]
        place_name = place["name"]
        print(place_id,place_name)
        local_json = sess.post(local_api, json={"id": place_id}).json()
        with open(f"local_{place_name}.json", "w") as f:
            f.write(json.dumps(local_json, ensure_ascii=False, separators=(',', ':'), indent=2))
        radios = local_json["data"]["categories"][0]
        to_disk(path=f"local_{place_name}.txt", radios=radios)

if __name__ == "__main__":
    os.chdir("scraped_data")
    main()