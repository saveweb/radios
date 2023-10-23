import os
import json
import time
import requests as rq

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"
national_api = "https://apppc.cnr.cn/national"
local_list_api = "https://apppc.cnr.cn/local/list"
local_api = "https://apppc.cnr.cn/local"

sess = rq.session()
sess.headers["User-Agent"] = UA

scraped_dir = "scraped_data"

def delay_request(r: rq.Response, *args, **kwargs):
    time.sleep(0.2)
sess.hooks['response'].append(delay_request)

def to_disk(path: str, radios, radio_dir: str=""):
    # radios = ["data"]["categories"][0]
    with open(path, "w") as f:
        for detail in radios["detail"]:
            _id: str = detail["id"]
            newsType: str = detail["newsType"]
            name: str = detail["name"]
            description: str = detail["description"]
            logo_url: str = detail["other_info6"]
            stream_url: str = detail["other_info11"][0]["url"]

            f.write("\t".join([
                _id if _id else "null",
                name if name else "null",
                newsType if newsType else "null",
                stream_url if stream_url else "null",
                logo_url if logo_url else "null",
                description if description else "null",
            ]) + "\n"
            )
            if radio_dir:
                os.makedirs(radio_dir, exist_ok=True)
                yaml_file = f"{radio_dir}/{name}.yml"
                logo_file = f"{radio_dir}/{name}.{logo_url.split('.')[-1]}"
                if os.path.exists(yaml_file):
                    continue
                with open(yaml_file, "w") as g:
                    g.write(
f"""\
title: {name}
description: {description}
homepage: 
schedule: 
logo: {logo_url}
source-url: {stream_url}
source-type: hls
location: CN;
language: chi
timezone: Asia/Shanghai
note: 
Suggested ID: radio-
submitted: no
"""
                    )
                with open(logo_file, "wb") as h:
                    h.write(sess.get(logo_url).content)


def main():
    national_json = sess.get(national_api).json()
    with open(f"{scraped_dir}/national.json", "w") as f:
        f.write(
            json.dumps(national_json, ensure_ascii=False, separators=(',', ':'), indent=2)
        )
    radios = national_json["data"]["categories"][0]
    to_disk(path=f"{scraped_dir}/national.txt", radios=radios, radio_dir="National")

    local_json_options = sess.get(local_list_api).json()
    with open(f"{scraped_dir}/local_options.json", "w") as f:
        f.write(json.dumps(local_json_options, ensure_ascii=False, separators=(',', ':'), indent=2))
    for place in local_json_options["liveChannelPlace"]:
        place_id = place["id"]
        place_name = place["name"]
        print(place_id,place_name)
        local_json = sess.post(local_api, json={"id": place_id}).json()
        with open(f"{scraped_dir}/local_{place_name}.json", "w") as f:
            f.write(json.dumps(local_json, ensure_ascii=False, separators=(',', ':'), indent=2))
        radios = local_json["data"]["categories"][0]
        to_disk(path=f"{scraped_dir}/local_{place_name}.txt", radios=radios, radio_dir=f"Local/{place_name}")

if __name__ == "__main__":
    main()