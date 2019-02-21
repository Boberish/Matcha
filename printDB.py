from app import db
from app.models import User

u = User.query.all()
print(u)
