from flask import Flask, render_template, redirect, request, flash, url_for, session
import model

app = Flask(__name__)
app.secret_key = "thisisnotmuchofasecret"


##################################################################


@app.route("/")
def index():
	userid = session.get("userid")
	if session.get("userid"):
		return redirect(url_for("home"))
	else:
		return render_template("index.html")
	# else:   // swap this code back in to resume testing against index.html
	# 	fbID = '6019968'  # Rodie's ID #
	# 	return render_template("index.html", fbID=fbID)


@app.route("/check-fbid", methods=["POST"])
def check_for_user():
	fbid = request.form['fbid'] #from the post, collect fbid
	session['fbid'] = fbid	
	fbtoken = request.form['fbtoken']
	session['fbtoken'] = fbtoken

	print "try-lookup"
	try: 
		user = model.session.query(model.User).filter_by(facebookId=fbid).one()
		session['userid'] = user.id
		print "%r" % user
	except:
		return url_for("register")
	return url_for("home")


@app.route("/register")
def register():
	print "fbid %r" % session['fbid']
	return render_template("register.html")

    
@app.route("/register", methods=["POST"])
def submit_registration():
	FBID = session.get("fbid")
	emailform = request.form.get("alt_email")
	ageform = request.form.get("age")
	cityform = request.form.get("city")
	stateform = request.form.get("state")
	zipcodeform = request.form.get("zipcode")
	model.register_user(FBID, emailform, ageform, cityform, stateform, zipcodeform)

	# user = session.query(User).filter_by(facebookId=FBID).one()  
	# session['userid'] = user.id
	
	return redirect(url_for("index"))

# TODO: look up - window.location="http://.../" + response.authResponse.userID

@app.route("/clear_session")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/home")
def home():
	userid = session.get("userid")
	recent_posts = model.recent_posts(userid)
#	recent_assists = model.recent_assists(uid)
	recent_replies = model.recent_replies(userid)
	return render_template("home.html", recent_posts=recent_posts, recent_replies=recent_replies)


# @app.route("/messages")
# def inbox():
# 	return render_template("messages.html")


# @app.route("/profile")
# def profile():
# 	return render_template("your_profile.html")


@app.route("/user/<userid>")
def userpage(userid):
	FBID = model.getFacebookId(userid)  #gets the browsed user's id
	local_FBID = session.get("fbid")  # gets the logged-in user's id
	local_FBaccessToken = session.get("fbtoken")

	recent_posts = model.recent_posts(userid)
	recent_replies = model.recent_replies(userid)
	return render_template("user.html", recent_posts=recent_posts, recent_replies=recent_replies, FBID=FBID, 
				local_FBID=local_FBID, local_FBaccessToken=local_FBaccessToken)


@app.route("/posts/<postid>")
def post_details(postid):
	post = model.getPostInfo(postid)
	comments = model.getCommentsForPost(postid)

	return render_template("post.html", postid=postid, post=post, comments=comments)

@app.route("/posts/<postid>", methods=["POST"])
def add_comment(postid):
	FBID = session.get("fbid")
	userid = session.get("userid")
	
	roleform = request.form.get("role")
	commentform = request.form.get("comment")
	zipcodeform = request.form.get("zipcode")
	isasapform = request.form.get("isASAP")
	canweekdaysform = request.form.get("canWeekdays")
	caneveningsform = request.form.get("canEvenings")
	canweekendsform = request.form.get("canWeekends")
	cantravelform = request.form.get("canTravel")
	canmeetform = request.form.get("canMeet")
	buslinesform = request.form.get("busLines")	

	model.submit_comment(userid, postid, roleform, commentform, zipcodeform, isasapform, canweekdaysform, 
		caneveningsform, canweekendsform, cantravelform, canmeetform, buslinesform)

	return redirect(url_for("home"))


@app.route("/posts/<postid>/receive/<authorid>")
def select_recipient(postid, authorid):

	model.selectRecipientOfItem(postid, authorid)

	return "Okay"

@app.route("/posts/<postid>/assist/<helperid>")
def select_helper(postid, helperid):

	model.selectFacilitatorOfItem(postid, helperid)


@app.route("/feedback/<postid>/<authorid>/<targetid>")
def start_feedback(postid, authorid, targetid):

	return render_template("reputation.html", postid=postid, authorid=authorid, targetid=targetid)


@app.route("/feedback/<postid>/<authorid>/<targetid>", methods=["POST"])
def leave_feedback(postid, authorid, targetid):

	postid = request.form.get("postid")
	authorid = request.form.get("authorid")
	targetid = request.form.get("targetid")
	score = request.form.get("score")
	comment = request.form.get("comment")
	
	model.leaveFeedback(postid, authorid, targetid, score, comment)


@app.route("/submit")
def post():

	return render_template("create_post.html")

@app.route("/submit", methods=["POST"])
def submission():
	FBID = session.get("fbid")
	userid = session.get("userid")


	roleform = request.form.get("role")
	shortsummaryform = request.form.get("shortSummary")
	longdescriptionform = request.form.get("longDescription")
	zipcodeform = request.form.get("zipcode")
	isasapform = request.form.get("isASAP")
	canweekdaysform = request.form.get("canWeekdays")
	caneveningsform = request.form.get("canEvenings")
	canweekendsform = request.form.get("canWeekends")
	cantravelform = request.form.get("canTravel")
	canmeetform = request.form.get("canMeet")
	buslinesform = request.form.get("busLines")                

	model.submit_post(userid, roleform, shortsummaryform, longdescriptionform, zipcodeform, isasapform, 
		canweekdaysform, caneveningsform, canweekendsform, cantravelform, canmeetform, buslinesform)

	return redirect(url_for("home"))

@app.route("/recent")
def global_get_posts():
	last_ten = model.getLastTenPosts()
	return render_template("recent.html", last_ten=last_ten)

@app.route("/guidelines")
def posting_guidelines():
	return render_template("rules.html")

	# get postID
	# return /posts/ + postID

# @app.route("/history")
# def history():
# 	return render_template("history.html")


# @app.route("/search")
# def search():
# 	return render_template("search.html")

#TODO: route for /backdoor


if __name__ == "__main__":
    app.run(debug = True)
