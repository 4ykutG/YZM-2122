import urllib

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=OGUZHAND;"
    "DATABASE=kelime_ezberleme;"
    "Trusted_Connection=yes;"
)

class Config:
    SECRET_KEY = 'gizli_anahtar'  # CSRF koruması için rastgele anahtar
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=" + params
    SQLALCHEMY_TRACK_MODIFICATIONS = False
