# @/inquiry/cj.py

import requests
from datetime import datetime

def cj_inquiry(invoice: str) -> str:
    session = requests.Session()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0"
    }
    params = {"wblNo": invoice}

    try:
        res = session.post(
            "https://trace.cjlogistics.com/next/rest/selectTrackingDetailList.do",
            data=params,
            headers=headers,
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
    except Exception:
        return {"success": False, "finish": False, "table": []}

    table = []
    finish = False

    if data.get("resultCode") == 200 and data.get("data") and data["data"].get("svcOutList"):
        for step in data["data"]["svcOutList"]:
            location = step.get("branNm", "").strip()
            status = step.get("crgStDnm", "").strip()
            date_str = step.get("workDt", "").strip()
            time_str = step.get("workHms", "").strip()

            try:
                dt_str = f"{date_str} {time_str}"
                timestamp = int(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").timestamp())
            except: continue

            table.append({"location": location, "status": status, "timestamp": timestamp})
            if "배송완료" in status:
                finish = True
        return {"success": True, "finish": finish, "table": table}
    else: 
        return { "success": False, "finish": False, "table": [] }
