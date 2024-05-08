# User

1. fix signup class method to raise ValueError for not a unique username or email

2. Fix logout route in app.py
    - Explore if g.user is a global user and we can use that to log out

3. Fix logout button in nav bar
    - here is the solution in show.jinja from Flask-notes

    - Can't be an anchor tag

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



