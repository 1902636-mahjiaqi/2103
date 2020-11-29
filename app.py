from flask import Flask, redirect, url_for, render_template, request, flash, session
# from flask_login import login_user, current_user, LoginManager, login_manager
import pymongo
from functools import wraps

from src.UserFunctions import UserAuth, UserCreate, SelectLikedArticles, SelectUserPayment, InsertPaymentMethod, \
    Transact, CheckTier, DeleteUser
from src.ArticlesFunction import SelectAllArticleTitle, SelectArticleDetails, LikeArticle, CheckLike, UnlikeArticle
from src.NoSQLStatement import TopTenSentimentForAllCategory, NumOfArticlesByAgencyWithName, \
    TopTenMostLikesArticleWithArticleTitle, TierAnalysis, SentimentValueCategory, MostArticleLikedAgency, \
    AllAvgSentimentRating, TopPaymentMethod
from src.WordCloud import generateWordCloud

# UserName: test PW:123 Admin

app = Flask(
    __name__,
    template_folder="templates",
)
app.secret_key = 'secretkeyhere'

# run application
if __name__ == '_main_':
    app.run(debug=True)

client = pymongo.MongoClient("mongodb+srv://admin:IBXxRxezhvT9f4D3@cluster0.vkqbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client["ICT2103_Project"]


# ensure page is login (for users)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


# ensure page is login (for administrators)
def admin_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' and 'is_admin' in session:
            return f(*args, **kwargs)
        else:
            flash('You are unauthorized to view this page, please login as administrator.')
            return redirect(url_for('login'))

    return wrap


# ensure page is logout and clear session
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for('login'))


########################### MAIN ###########################
# return route to login view
@app.route("/")
def login():
    tier = 1
    return render_template("main/login.htm", tier=tier)


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('usernameTB')
    password = request.form.get('passwordTB')

    account = UserAuth(db, username, password)
    if account:
        session['logged_in'] = True
        session['id'] = UserAuth(db, username, password)[0]
        session['username'] = UserAuth(db, username, password)[1]

        # check whether if account is administrator is admin
        # 0 is not admin
        # 1 is admin
        if (UserAuth(db, username, password)[4] == 1):
            session['is_admin'] = True

        # Redirect to home page
        user_id = session['id']
        article = SelectLikedArticles(db, user_id)

        tier = CheckTier(db, user_id)

        return render_template('main/user_profile.htm', username=session['username'], article=article, tier=tier)
    else:
        flash('Please check your login details and try again.')
        session.clear()

    if (username == "" or password == ""):
        flash('Please enter login details')

    return redirect(url_for('login'))


# return route to register view
@app.route("/register")
def register():
    return render_template("main/register.htm")


@app.route("/register", methods=['POST'])
def register_post():
    reg_username = request.form.get('reg_usernameTB')
    reg_pw = request.form.get('reg_pwTB')
    reg_conpw = request.form.get('confirm_pwTB')

    if (reg_pw == reg_conpw):
        if (UserAuth(db, reg_username, reg_pw) == None):
            UserCreate(db, reg_username, reg_pw)
            flash('Account successfully created.')
    else:
        flash('Account exist.')
    return redirect(url_for('register'))


########################### USER ###########################
# return route to user dashboard view
@app.route("/user_dashboard")
def user_dashboard():
    generateWordCloud(db)

    # code for top 10 sentiment for all category graph
    topTenSentimentForCategory = TopTenSentimentForAllCategory(db)
    values1 = []
    labels1 = []
    legend1 = 'Top Ten Sentiment For All Category'
    for x in range(len(topTenSentimentForCategory)):
        labels1.append((topTenSentimentForCategory[x][0])[:10])
        values1.append(topTenSentimentForCategory[x][1])

    # code for number of articles by agency graph
    numOfArticlesByAgency = NumOfArticlesByAgencyWithName(db)
    values2 = []
    labels2 = []
    legend2 = 'Number of articles by agency'
    for x in range(len(numOfArticlesByAgency)):
        labels2.append(numOfArticlesByAgency[x][0])
        values2.append(numOfArticlesByAgency[x][1])

    # code for top 10 articles with most likes graph
    topTenMostLikesArticle = TopTenMostLikesArticleWithArticleTitle(db)
    values3 = []
    labels3 = []
    legend3 = 'Top 10 articles with the most likes'
    for x in range(len(topTenMostLikesArticle)):
        labels3.append((topTenMostLikesArticle[x][0])[:10])
        values3.append(topTenMostLikesArticle[x][1])


    user_id = session['id']
    tier = CheckTier(db, user_id)

    return render_template("main/user_dashboard.htm", username=session['username'], values1=values1, labels1=labels1,
                           legend1=legend1, values2=values2, labels2=labels2, legend2=legend2, values3=values3,
                           labels3=labels3, legend3=legend3, tier=tier)


# return route to user article view
@app.route("/article")
@login_required
def article():
    article = SelectAllArticleTitle(db)
    user_id = session['id']
    tier = CheckTier(db, user_id)

    return render_template("main/article.htm", article=article, username=session['username'], tier=tier)


@app.route("/view_article", methods=['GET', 'POST'])
@login_required
def view_article():
    user_id = session['id']
    article_id = request.form['article_id']
    like = request.form['like']

    article_item = SelectArticleDetails(db, article_id)
    check_like = CheckLike(db, user_id, article_id)

    # check if liked
    if like == 'true' and check_like == False:
        LikeArticle(db, user_id, article_id)

    if like == 'false' and check_like == True:
        UnlikeArticle(db, user_id, article_id)

    user_id = session['id']
    tier = CheckTier(db, user_id)

    # else:
    return render_template('main/view_article.htm', username=session['username'], article_id=article_id,
                           article_item=article_item, check_like=check_like, like=like, tier=tier)


# return route to user favourite view, profile, privillege, etc
@app.route("/user_profile")
@login_required
def user_profile():
    user_id = session['id']
    article = SelectLikedArticles(db, user_id)
    tier = CheckTier(db, user_id)

    return render_template("main/user_profile.htm", article=article, username=session['username'], tier=tier)


@app.route("/user_profile_unfav", methods=['GET', 'POST'])
@login_required
def user_profile_unfav():
    user_id = session['id']
    article_id = request.form['article_id']
    UnlikeArticle(db, user_id, article_id)
    article = SelectLikedArticles(db, user_id)
    tier = CheckTier(db, user_id)

    return render_template("main/user_profile.htm", article=article, username=session['username'], tier=tier)


# return route to user purchase view
@app.route("/user_purchase", methods=['GET'])
@login_required
def user_purchase():
    user_id = session['id']
    tier = CheckTier(db, user_id)
    checkCurrentCreditCard = SelectUserPayment(db, user_id)
    if checkCurrentCreditCard != "None":
        return render_template("main/user_purchase.htm", username=session['username'],
                               cardNumber=checkCurrentCreditCard[0], expiryDate=checkCurrentCreditCard[1], tier=tier)
    else:
        return render_template("main/user_purchase.htm", username=session['username'], tier=tier)


@app.route("/user_purchase", methods=['POST'])
def user_purchase_post():
    user_id = session['id']
    reg_cardNumber = request.form.get('cardNumber')
    reg_expiryDate = request.form.get('expiryDate')

    InsertPaymentMethod(db, user_id, reg_cardNumber, reg_expiryDate)
    isSuccessful = Transact(db, user_id)
    if isSuccessful == True:
        flash('Account successfully upgraded.')
    else:
        flash('An error has occurred, please try again later.')

    # return render_template("main/user_profile.htm", username=session['username'])
    return redirect(url_for('user_profile'))


# return route to user purchase view
@app.route("/user_privilege")
@login_required
def user_privilege():
    user_id = session['id']
    tier = CheckTier(db, user_id)

    return render_template("main/user_privilege.htm", username=session['username'], tier=tier)


####################### ADMINISTRATOR #######################
# return route to admin dashboard view
@app.route("/admin_dashboard")
@admin_login_required
def admin_dashboard():
    # code for tier analysis graph
    tierAnalysis = TierAnalysis(db)
    values1 = []
    labels1 = []
    legend1 = 'Tier Analysis'
    for x in range(len(tierAnalysis)):
        if (tierAnalysis[x][0]) == 1:
            labels1.append("Free")
        else:
            labels1.append("Paid")
        values1.append(tierAnalysis[x][1])

    # code for sentiment value category graph
    sentimentValueCategory = SentimentValueCategory(db)
    values2 = []
    labels2 = []
    legend2 = 'Sentiment Value Category'
    for x in range(len(sentimentValueCategory)):
        print(sentimentValueCategory)
        labels2.append((sentimentValueCategory[x][0]))
        values2.append(sentimentValueCategory[x][1])

    # code for most article liked agency graph
    mostArticleLikedAgency = MostArticleLikedAgency(db)
    values3 = []
    labels3 = []
    legend3 = 'Most Article Liked Agency'
    for x in range(len(mostArticleLikedAgency)):
        labels3.append((mostArticleLikedAgency[x][0]))
        values3.append(mostArticleLikedAgency[x][1])

    # code for average sentiment rating graph
    allAvgSentimentRating = AllAvgSentimentRating(db)
    values4 = []
    labels4 = []
    legend4 = 'Average Sentiment for Agency'
    for x in range(len(allAvgSentimentRating)):
        labels4.append((allAvgSentimentRating[x][0]))
        values4.append(allAvgSentimentRating[x][1])

    # code for average sentiment rating graph
    topPaymentMethod = TopPaymentMethod(db)
    values5 = []
    labels5 = []
    legend5 = 'Top Payment Method'
    for x in range(len(topPaymentMethod)):
        labels5.append((topPaymentMethod[x][0]))
        values5.append(topPaymentMethod[x][1])

    user_id = session['id']
    tier = CheckTier(db, user_id)

    return render_template("main/admin_dashboard.htm", username=session['username'], values1=values1, labels1=labels1,
                           legend1=legend1, values2=values2, labels2=labels2, legend2=legend2, values3=values3,
                           labels3=labels3, legend3=legend3, values4=values4, labels4=labels4, legend4=legend4,
                           values5=values5, labels5=labels5, legend5=legend5, tier=tier)


####################### DELETE USER #######################
@app.route("/delete_user")
@login_required
def delete_user():
    user_id = session['id']
    tier = CheckTier(db, user_id)

    isSuccessful = DeleteUser(db, user_id)
    if isSuccessful == True:
        flash('Account successfully deleted.')
        tier = 1
        return render_template("main/login.htm", tier=tier)
    else:
        flash('An error has occurred, please try again later.')

    return render_template("main/user_profile.htm", tier=tier, username=session['username'])