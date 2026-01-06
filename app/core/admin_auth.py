from fastapi import Header, HTTPException, Request
import os

admin_key = os.getenv("ADMIN_KEY")

def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


# def verify_admin_ui(request: Request):
#     token = request.cookies.get("admin_key")
#     if token != admin_key:
#         raise HTTPException(status_code=403)
    
def verify_admin_ui(request: Request):
    if request.url.path.endswith("/login"):
        return True

    token = request.cookies.get("admin_key")
    if token != admin_key:
        raise HTTPException(status_code=403)
