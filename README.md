# Multi-User Blog

This software allows users to create an account, create new blog posts and
comments on posts, edit their existing posts and comments, and like other
users' posts are comments.

This software is running live at http://matt-benjamin.appspot.com/

## Setting Up Your own deployment
Alternatively to using the live link above, you may run this software locally
or deploy it to your own AppEngine account:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of
 this sample.
2.
    a. To run the app locally, use the devserver using dev_appserver.py DIR.
    You may then use the software by visiting its URI  (by default:
    localhost:8080 )

    b. If deploying to App Engine, either upload the software with the Google
    AppEngineLauncher or run the command appcfg.py -A [YOUR_PROJECT_ID] update DIR
    You can view additional information [here](https://cloud.google.com/appengine/docs/python/gettingstartedpython27/deploying-the-application#deploying_the_app_to_app_engine)

## Using the Blog
The main pages of the blog can be navigated by using the menu on the top-right
corner of the page. For a user not logged in, they are:
##### Home
    The home page will display the last 10 blog posts that have been made by
    all users.

##### Signup
    The signup page allows a user to create an account. Usernames must be
    unique and can be between 3 and 20 characters. Characters must be
    alphanumeric, hyphens and underscores are also accepted. Passwords
    must also be between 3 and 20 characters. An email may be provided
    optionally, but at this time providing one does not add any functionality.

##### Login
    The login page allows a user to enter their unique username and password
    in order to login. A user must be logged in in order to create, edit, or
    delete their posts and comments, or to like/unlike other users posts and
    comments.

A user who is logged in will see the following menu:

##### Home
##### New Post
    The new post page display a form to create new posts. Simply enter your new
    post's subject and body and click the Create Post button below the form!
##### [Username]
    Display's the current logged in user's username. Links to /user/[username]
    The /user/[username] page will display the last 10 posts that have been
    made by that user.
##### Logout
    Allows the current user to log out.

#### Other Pages

##### Post
    Clicking on any post's title will load the page for that post. Here, users
    can read and submit comments in reply to the post.
##### Delete Item
    Should a user wish to delete a post or comment, this page will ask the user
    for confirmation.
##### Edit Page
    If a user wishes to edit the content or a prior post or comment, this page
    will display a form similar to the form used to create a new post or
    comment.

#### Likes
To toggle a post or comment that you wish to like or unlike, simply click
on the Like button under the header of the item.