from flask import Blueprint, render_template, session, redirect, url_for, flash, request

home = Blueprint("home", __name__)

@home.route("/")
def home_page():
    return render_template("homepage.html")

@home.route("/about")
def about_home():
    return render_template("about.html")