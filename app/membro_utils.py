import re
import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

def clean_digits(val: str) -> str:
    if not val:
        return ""
    return re.sub(r'\D', '', str(val))

def validate_cpf(cpf_str: str) -> bool:
    """
    Validates Brazilian CPF document using checksum algorithm.
    """
    if not cpf_str:
        return False
    digits = clean_digits(cpf_str)
    if len(digits) != 11:
        return False
    if len(set(digits)) == 1:
        return False # e.g. 111.111.111-11
    
    # Check 1st digit
    s1 = sum(int(digits[i]) * (10 - i) for i in range(9))
    d1 = (s1 * 10) % 11
    if d1 == 10:
        d1 = 0
    if int(digits[9]) != d1:
        return False

    # Check 2nd digit
    s2 = sum(int(digits[i]) * (11 - i) for i in range(10))
    d2 = (s2 * 10) % 11
    if d2 == 10:
        d2 = 0
    if int(digits[10]) != d2:
        return False

    return True

def format_cpf(cpf_str: str) -> str:
    if not cpf_str:
        return ""
    digits = clean_digits(cpf_str)
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return cpf_str

def mask_cpf(cpf_str: str) -> str:
    if not cpf_str:
        return ""
    digits = clean_digits(cpf_str)
    if len(digits) == 11:
        return f"***.***.{digits[6:9]}-{digits[9:]}"
    return "***.***.***-**"

def generate_next_codigo_membro(db: Session) -> str:
    """
    Generates sequential member code in M0001, M0002, M0003 format.
    """
    from app.models import Membro
    membros = db.query(Membro.codigo_membro).all()
    max_num = 0
    for (c_val,) in membros:
        if c_val and str(c_val).startswith("M"):
            try:
                num = int(str(c_val)[1:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    next_num = max_num + 1
    return f"M{next_num:04d}"
