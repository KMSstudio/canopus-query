# from inquiry.cj import cj_inquiry
# from inquiry.po import po_inquiry
# from inquiry import inquiry

# invoice = "520315867871"  # 테스트용 송장번호
# data = inquiry('cj', invoice)
# data = inquiry('po', "6896700517650")
# print(data)

# construct/main.py

from database import add_invoice, dbutil, construct

if __name__ == "__main__":
    # 우체국택배 송장번호 예시 사용
    # add_invoice('po', '6896700517650', 100)
    construct()
    dbutil.dump('database.db')
