from inquiry.cj import cj_inquiry
from inquiry.po import po_inquiry

invoice = "520315867871"  # 테스트용 송장번호
data = cj_inquiry(invoice)
data = po_inquiry("6896700517650")
print(data)
