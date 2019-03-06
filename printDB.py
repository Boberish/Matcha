from app import db
from app.models import User

u1 = User.query.get(1)
u2 = User.query.get(2)
u3 = User.query.get(3)
u4 = User.query.get(4)
u2.add_like(u3)
u3.add_like(u2)
# u1.add_like(u2)
# u1.add_like(u3)
# db.session.commit()
# u1.add_like(u4)
# u1.add_like(?
# print(u1.does_like(u2))
# print(u2.does_like(u3))
# print( u3.your_likes().first().liked.all())
print( u3.likes_you().all())
# print(u1.liked.all())

# print(f1)
