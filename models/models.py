from flask import Flask, render_template
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class OnegaiContent(Base):
    __tablename__ = 'onegaicontents'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    body = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)

    def __init__(self, title=None, body=None):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Title %r>' % (self.title)
