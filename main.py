from inquiry.cj import cj_inquiry
from inquiry.po import po_inquiry
from inquiry import inquiry

invoice = "520315867871"  # 테스트용 송장번호
data = inquiry('cj', invoice)
data = inquiry('po', "6896700517650")
print(data)
