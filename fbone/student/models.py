# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import Mutable
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from ..extensions import db
from ..utils import SEX_TYPE, STRING_LEN
from .constants import USER, USER_ROLE, ADMIN, INACTIVE, USER_STATUS


class BasicModel(db.Model):
    """
        Basic Model for inheritance.
    """
    __abstract__ = True

    id = Column(db.Integer, primary_key=True)
    created_on = Column(db.DateTime, default=datetime.utcnow)
    updated_on = Column(db.DateTime, onupdate=datetime.utcnow)


class Student(BasicModel):
    """
        Simple student in classroom.
    """
    __tablename__ = 'students'

    firstname = Column(db.String(STRING_LEN))
    lastname = Column(db.String(STRING_LEN))
    mail = Column(db.String(STRING_LEN), nullable=True, unique=True)
    doc = Column(db.String(10), nullable=True, unique=True)
    gender_code = Column(db.Integer)

    @property
    def gender(self):
        return SEX_TYPE.get(self.gender_code)

    # attendance = query...


class Subject(BasicModel):
    """
        Represents the whole course.
    """

    __tablename__ = 'subjects'

    name = Column(db.String(STRING_LEN))
    semester = Column(db.SmallInteger)  # TODO: usar Enum
    day = Column(db.SmallInteger)  # TODO: usar Enum
    starts_at = Column(db.Time)
    ends_at = Column(db.Time)


class Lesson(BasicModel):
    """
        Represents the daily class.
    """

    __tablename__ = 'lessons'

    date = Column(db.DateTime)
    topic = Column(db.String(STRING_LEN))
    # resources = relationship


class Grade(BasicModel):
    """
        Students grades.
    """

    __tablename__ = 'grades'

    first_mid_term_exam = Column(db.SmallInteger, default=None)
    second_mid_term_exam = Column(db.SmallInteger, default=None)
    first_makeup_exam = Column(db.SmallInteger, default=None)
    second_makeup_exam = Column(db.SmallInteger, default=None)
    third_makeup_exam = Column(db.SmallInteger, default=None)
    final_exam = Column(db.SmallInteger, default=None)


class Resource(BasicModel):
    """
        Teachers resources
    """

    __tablename__ = 'resources'

    description = Column(db.String(STRING_LEN))
    content = Column(db.LargeBinary)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN), nullable=False, unique=True)
    email = Column(db.String(STRING_LEN), nullable=False, unique=True)
    openid = Column(db.String(STRING_LEN), unique=True)
    activation_key = Column(db.String(STRING_LEN))
    created_time = Column(db.DateTime, default=get_current_time)

    avatar = Column(db.String(STRING_LEN))

    _password = Column('password', db.String(STRING_LEN), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)
    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    # ================================================================
    role_code = Column(db.SmallInteger, default=USER, nullable=False)

    @property
    def role(self):
        return USER_ROLE[self.role_code]

    def is_admin(self):
        return self.role_code == ADMIN

    # ================================================================
    # One-to-many relationship between users and user_statuses.
    status_code = Column(db.SmallInteger, default=INACTIVE)

    @property
    def status(self):
        return USER_STATUS[self.status_code]

    # ================================================================
    # One-to-one (uselist=False) relationship between users and user_details.
    user_detail_id = Column(db.Integer, db.ForeignKey("user_details.id"))
    user_detail = db.relationship("UserDetail", uselist=False, backref="user")

    # ================================================================
    # Follow / Following
    followers = Column(DenormalizedText)
    following = Column(DenormalizedText)

    @property
    def num_followers(self):
        if self.followers:
            return len(self.followers)
        return 0

    @property
    def num_following(self):
        return len(self.following)

    def follow(self, user):
        user.followers.add(self.id)
        self.following.add(user.id)

    def unfollow(self, user):
        if self.id in user.followers:
            user.followers.remove(self.id)

        if user.id in self.following:
            self.following.remove(user.id)

    def get_following_query(self):
        return User.query.filter(User.id.in_(self.following or set()))

    def get_followers_query(self):
        return User.query.filter(User.id.in_(self.followers or set()))

    # ================================================================
    # Class methods

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(User.name == login, User.email == login)).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_name(self, name):
        return User.query.filter(db.and_(User.name == name, User.email != self.id)).count() == 0
