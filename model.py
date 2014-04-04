from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
# from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from sqlalchemy import update
import time
import datetime
import sqlite3
import os
import sys

DB_URI = os.getenv("DATABASE_URI")
##############################################################################

 
ENGINE = create_engine(DB_URI, echo=False)

session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()


##############################################################################


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    facebookId = Column(Integer)
    altEmail = Column(String(64), nullable=True)
    age = Column(Integer)
    city = Column(String(64), nullable=True)
    state = Column(String(2)) # get this to a 2-letter value from a drop-down
    zipcode = Column(String(15))
    registrationDate = Column(Integer)


class Post(Base):
	__tablename__ = "listings"
	id = Column(Integer, primary_key = True)
	ownerId = Column(Integer, ForeignKey('users.id'))
	timeStamp = Column(Integer)
	zipcode = Column(String(15), nullable=True)
	role = Column(String(16))
	shortSummary = Column(String(30))
	longDescription = Column(String(300))
	pictureId = Column(Integer)
	isASAP = Column(Integer)
	canWeekdays = Column(Integer)
	canEvenings = Column(Integer)
	canWeekends = Column(Integer)
	canTravel = Column(Integer)
	canMeet = Column(Integer)
	busLines = Column(String(64), nullable=True)  # two splits - ",", whitespace? or regex both
	offerExtendedTo = Column(Integer)

	author = relationship("User", backref=backref("listings", order_by=id))

	def time_string(instance_of_class):
		dateObject = time.localtime(instance_of_class.timeStamp)
		return time.strftime('%m-%d-%Y %H:%M:%S', dateObject)




class Response(Base):
	__tablename__ = "responses"
	id = Column(Integer, primary_key = True)
	authorId = Column(Integer, ForeignKey('users.id'))
	listingId = Column(Integer, ForeignKey('listings.id'))
	role = Column(String(16))
	timeStamp = Column(Integer) 
	zipcode = Column(String(15), nullable=True)
	comment = Column(String(300))
	canASAP = Column(Integer) 
	canWeekdays = Column(Integer)
	canEvenings = Column(Integer)
	canWeekends = Column(Integer)
	canTravel = Column(Integer)
	canMeet = Column(Integer)
	busLines = Column(String(64), nullable=True)
	wasOffered = Column(Integer)
	wasOfferedAssist = Column(Integer)
	offerStatus = Column(String(64))
	offerAssistStatus = Column(String(64))
	timeSelected = Column(Integer)
	lastUpdated = Column(Integer)

	responder = relationship("User", backref=backref("responses"), order_by=id)
	post = relationship("Post", backref=backref("responses"), order_by = id)

	def time_string(instance_of_class):
		dateObject = time.localtime(instance_of_class.timeStamp)
		return time.strftime('%m-%d-%Y %H:%M:%S', dateObject)




##############################################################################

# metadata = MetaData()
# metadata.create_all(ENGINE)


def register_user(fbId, emailform, ageform, cityform, stateform, zipcodeform):
	temp_user = User(facebookId=fbId, altEmail=emailform, age=ageform, city=cityform, state=stateform, 
				zipcode=zipcodeform, registrationDate=int(time.time())) #check time.time usage
	session.add(temp_user)
	session.commit()

def submit_post(userid, roleform, shortsummaryform, longdescriptionform, zipcodeform, isasapform, 
	canweekdaysform, caneveningsform, canweekendsform, cantravelform, canmeetform, buslinesform):

	temp_post = Post(ownerId=userid, role=roleform, shortSummary=shortsummaryform, 
		longDescription=longdescriptionform, zipcode=zipcodeform, isASAP=isasapform, 
		canWeekdays=canweekdaysform, canEvenings=caneveningsform, canWeekends=canweekendsform, 
		canTravel=cantravelform, canMeet=canmeetform, busLines=buslinesform, timeStamp=int(time.time()))
	session.add(temp_post)
	session.commit()

def recent_posts(uid):
	u = session.query(User).get(uid)
	post_list = session.query(Post).filter_by(ownerId=u.id)
	post_list = post_list.order_by(Post.id.desc())
	return post_list

def recent_replies(uid):
	u = session.query(User).get(uid)
	reply_list = session.query(Response).filter_by(authorId=u.id)
	reply_list = reply_list.order_by(Response.id.desc())
	return reply_list

def getPostInfo(postid):
	post = session.query(Post).get(postid)
	return post

def getCommentsForPost(postid):
	c = session.query(Post).get(postid)
	comments = session.query(Response).filter_by(listingId=c.id)
	return comments

def getLastTenPosts():
	last_ten = session.query(Post).order_by(Post.id.desc()).limit(10)
	return last_ten

def getFacebookId(userid):
	u = session.query(User).get(userid)
	return u.facebookId

def selectRecipientOfItem(postid, recipientid):
	post = session.query(Post).get(postid)
#	post=session.query(Post).filter_by(id=postid).first()
	post.offerExtendedTo = recipientid
	session.commit()


def submit_comment(userid, postid, roleform, commentform, zipcodeform, isasapform, canweekdaysform, caneveningsform, 
	canweekendsform, cantravelform, canmeetform, buslinesform):

	temp_comment = Response(authorId=userid, listingId=postid, role=roleform, comment=commentform, zipcode=zipcodeform, 
		canASAP=isasapform, canWeekdays=canweekdaysform, canEvenings=caneveningsform, 
		canWeekends=canweekendsform, canTravel=cantravelform, canMeet=canmeetform, busLines=buslinesform, 
		timeStamp=int(time.time()))
	session.add(temp_comment)
	session.commit()




