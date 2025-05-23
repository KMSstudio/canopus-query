from inquiry.cj import cj_inquiry

invoice = "520315867871"  # 테스트용 송장번호
data = cj_inquiry(invoice)
print(data)
