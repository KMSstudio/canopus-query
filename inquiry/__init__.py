from typing import Literal
from .cj import cj_inquiry
from .po import po_inquiry

__all__ = ['cj_inquiry', 'po_inquiry', 'inquiry']

def inquiry(company: Literal['cj', 'po'], invoice: str):
    """
    company: 'cj' 또는 'po'만 가능
    invoice: 송장 번호
    """
    if company == 'cj':
        return cj_inquiry(invoice)
    elif company == 'po':
        return po_inquiry(invoice)

    else:
        raise ValueError("지원하지 않는 회사입니다. 'cj' 또는 'po'만 사용할 수 있습니다.")
