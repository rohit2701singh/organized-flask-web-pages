from datetime import datetime, timezone
from myapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    # print(user_id)
    # print(db.session.execute(db.select(User).where(User.id == user_id)).scalar())
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String, nullable=False, default='default.jpg')

    posts = db.relationship('Post', back_populates='author', lazy=True)   # backpopulates requires defining the relationship in both models.

    def __repr__(self): # When you print an object of class, __repr__ defines what gets displayed.
        return f"User Detail: User({self.username}, {self.email}, {self.image_file})"
                                                                                                   

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,  default=lambda: datetime.now(timezone.utc))   #datetime.utcnow depricated
    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='posts', lazy=True)
    
    def __repr__(self):
        return f"Post Detail: Post({self.title}, {self.date_posted})"
    