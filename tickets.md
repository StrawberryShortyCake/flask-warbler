# User

1. DONE A DB THROWS AN INTEGRITY ERROR AND WE ALREADY CAUGHT:
- fix signup class method to raise IntegrityError for not a unique username or email

2. DONE Fix logout route in app.py (view function)
    - Explore if g.user is a global user and we can use that to log out
    - flash logout success message
    - redirect back to login page

3. DONE Fix logout button in nav bar
    - here is the solution in show.jinja from Flask-notes

    - Can't be an anchor tag

    - Set up the csrf form on forms.py
    - set the csrf_form globally on the g.object
    - use it correctly in the base.jinja
    - I believe the g.csrf_form needs to be set in the before_request

    ``` html
    <form>
        {{ form.hidden_tag() }}
        <button class="btn btn-danger btn-sm"
                formaction="/users/{{ user.username }}/delete"
                formmethod="POST">
          Delete User
        </button>

        <button class="btn btn-danger btn-sm"
                formaction="/logout"
                formmethod="POST">
          Logout
        </button>
     </form>
    ```

4.** DONE IN USER SIGN UP METHOD ALREADY:
signup() method in app.py needs to add the user into the db in the if

5. DONE: login() method, when calling User.authenticate(), we need to specify the
named param arguments (username, password). User.authenticate() will pass back
False if it can't find a user

6. DONE: Need an image alt for users header image
    - /users/index.jinja
    - /users/following.jinja
    - /users/followers.jinja

7. DONE: Need {{ form.hidden_tag() }} for the forms with method POST

9. DONE, we used a g.object to pass it into the jinja instead
    Need to pass in the CSRF form
    - appy.py show_following() method
    - appy.py show_followers() method


10-A WIP. Add data to show.jinja
    - DONE: user location
    - DONE: user bio
    - FIXME: this needs to dynamically change correctly: user header_image
        ``` html taken from /user/index.jinja
            <div class="image-wrapper">
              <img src="{{ user.header_image_url }}"
                   alt=""
                   class="card-hero">
            </div>
        ```

10-B. DONE: Complete profile_update() method in app.py
    - need authorization
    - need to show edit.jinja


11. DONE: For profile_update() method in app.py, there are...
    - GET : which will be called on users/detail.jinja, but will render the
          /users/edit.jinja template with form (so pass in the form)
    - POST : which will be called on users/edit.jinja, and will process the form
          input
    - Possibly rename this method

12. DONE: delete_user() method in app.py needs a flash message for successful logout



14. DONE: Show the bio for users/
    - followers.jinja
    - following.jinja
    - list-users pages? index.jinja I believe.

15. DONE: Make a WTForm for editting the profile
    - username
    - email
    - image_url
    - header_image_url
    - bio

    Have a password protection for edits, does not change the password.
    - password
        - Can only edit profile if we enter the correct password
            - if not flash error and repopulate the form

    Redirect to user/detail.jinja

16. DONE: Fix homepage()
    The homepage for logged-in-users should show the last 100 warbles only from the users that the logged-in user is following, and that user, rather than warbles from all users.


## Questions
- Why not an email field for our signup form?
- How do we get more details from our Integrity Error? we want to see "username" vs "email"
- How do we get the header image working correctly?

## Further Studies
- Add labels to all forms
    - users/signup.jinja

- added a password verification before deleting profile

- add UI for showing /users

- add nav collapse




