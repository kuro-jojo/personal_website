import datetime
from dotenv import load_dotenv
import logging
import socket
import os
from flask import Flask, render_template, request, redirect, url_for
from logging.handlers import SysLogHandler

load_dotenv()

from src.models.UserMessage import UserMessage
from src.models import UserMessage
from src.modules.form import fetch_contact_data

app = Flask(__name__)
paperTrailAppUrl = os.getenv("PAPER_TRAIL_URL")
paperTrailAppPort = os.getenv("PAPER_TRAIL_PORT")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS '] = False
db = UserMessage.db
db.init_app(app)

def init():
    """Initialize some configurations"""
    # create tables
    with app.app_context():
        # log("Creating database")
        print("Creating database")
        db.create_all()

init()

@app.route("/")
def home():
    """Send to homepage"""
    log()    
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    """save a message from the user into a databse

    Returns:
        Response: redirection to the homepage
    """
    try:
        userMessage = fetch_contact_data(request.form)
        db.session.add(userMessage)
        db.session.commit()
        log("Receive new message via contact form")
        return ("Message sent successfully", 200)
    except Exception as e:
        log(f"Exception found : {e}", logging.ERROR)
    return redirect(url_for("home"))



def log(msg="", level=logging.INFO):
    """Logs message to a remote log viewer"""
    if not paperTrailAppUrl and not paperTrailAppPort:
        raise TypeError("An url and a port is requested")

    syslog = SysLogHandler(address=(paperTrailAppUrl, int(paperTrailAppPort)))
    syslog.addFilter(ContextFilter())
    format = "%(asctime)s %(hostname)s Portfolio-kuro-jojo: %(message)s"
    formatter = logging.Formatter(format, datefmt="%b %d %H:%M:%S")
    syslog.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(syslog)
    logger.setLevel(level)
    message = f"IP : {request.remote_addr} - Browser : {request.headers.get('User-Agent').split(' ')[0]} : {msg}"
    logger.info(message)

class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
