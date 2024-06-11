# config.py
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'roma'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tasktrek.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
