from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"

    def __set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "email": self.email,
            "dateCreated": self.date_created
        }
    
    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        description = db.Column(db.String, nullable=False)
        completed = db.Column(db.Boolean, nullable=False, default=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        due_date = db.Column(db.DateTime, nullable=True)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.save()
        
        def __repr__(self):
            return f"<Task {self.id}|{self.title}>"

        def save(self):
            db.session.add(self)
            db.session.commit()
                
        def update(self, **kwargs):
            for attr, value in kwargs.items():
                setattr(self, attr, value)
            self.save()
    
        def delete(self):
            db.session.delete(self)
            db.session.commit()
            
        def to_dict(self):
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "completed": self.completed,
                "created_at": self.created_at,
                "due_date": self.due_date

            }
        