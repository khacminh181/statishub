import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=113.160.94.133,63830;"
    "DATABASE=FiinRatings;"
    "UID=FiinRatings.FRA.View;"
    "PWD=FiinR@tings1234;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
print("OK")