from app import db
from app.models import User, likes

u = User.query.all()
# print(u)
pap = User.query.get(1)
me = User.query.get(2)
keaton = User.query.get(3)
# print(pap)
# print(me)
# print(keaton)

pap.add_like(me)
keaton.add_like(me)
me.add_like(keaton)
me.add_like(pap)

print(me.your_likes())
# print(me.liked.all())




# likes = User.query.liked()





# from app import db
# from app.models import User

# u1 = User.query.get(1)
# u2 = User.query.get(2)
# u3 = User.query.get(3)
# # u2.add_like(u3)
# # u1.add_like(u3)
# # print(u2.does_like(u3))



# f1 = u2.your_likes().all()
# print(f1)

