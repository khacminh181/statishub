from fastapi import Header, HTTPException
import os

admin_key = os.getenv("ADMIN_KEY")

def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True
