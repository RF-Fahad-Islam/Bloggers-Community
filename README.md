
Bloggers' Community
===================

Welcome to the Bloggers' Community repository! This is a full-stack application built with a **Flask** backend and a frontend using **HTML, CSS, JavaScript, and HTMX**. It's designed to provide a platform for bloggers to share their thoughts, interact with others, and manage their content seamlessly. 


![enter image description here](https://cdn.hashnode.com/res/hashnode/image/upload/v1673443377427/fd39c44f-8cfc-4620-b74f-0d5e564a67b0.jpeg?w=1600&h=840&fit=crop&crop=entropy&auto=compress,format&format=webp)

A live version of the application is deployed and can be viewed here: **[Live Demo Link]** (Currently the website is not live for server costs)

📋 Table of Contents
--------------------

1.  [Features](https://www.google.com/search?q=%23-features "null")

2.  [Tech Stack](https://www.google.com/search?q=%23-tech-stack "null")

3.  [Getting Started](https://www.google.com/search?q=%23-getting-started "null")

    -   [Prerequisites](https://www.google.com/search?q=%23prerequisites "null")

    -   [Installation](https://www.google.com/search?q=%23installation "null")

4.  [Usage](https://www.google.com/search?q=%23-usage "null")

5.  [Contributing](https://www.google.com/search?q=%23-contributing "null")


✨ Features
----------

-   **Social Authentication:** Secure user registration and login with Google OAuth.

-   **Session Management:** Persistent user sessions using server-side cookies.

-   **Admin Panel:** A dedicated admin interface powered by Flask-Admin for site management.

-   **Blog Post Management:** Users can perform full CRUD (Create, Read, Update, Delete) operations on their blog posts.

-   **Markdown Support:** Write blogs in Markdown, which are automatically converted to HTML for display.

-   **Dynamic UI with HTMX:** Modern, interactive user experience without complex JavaScript frameworks.

-   **Responsive Design:** A clean and modern UI built with Tailwind CSS that looks great on all devices.

🚀 Tech Stack
-------------

This project is built with a powerful Python backend and a classic frontend stack, enhanced with modern libraries.

-   **Frontend:**

    -   [HTML5](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5 "null")

    -   [Tailwind CSS](https://tailwindcss.com/ "null")

    -   [JavaScript (ES6+)](https://developer.mozilla.org/en-US/docs/Web/JavaScript "null")

    -   [HTMX](https://htmx.org/ "null")

-   **Backend:**

    -   [Python](https://www.python.org/ "null") & [Flask](https://flask.palletsprojects.com/ "null") - Core web framework.

    -   [Gunicorn](https://gunicorn.org/ "null") - WSGI HTTP Server for production.

    -   **Database & ORM:**

        -   [PostgreSQL](https://www.postgresql.org/ "null") - The primary relational database.

        -   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/ "null") - SQL ORM for Flask.

        -   [Flask-Migrate](https://flask-migrate.readthedocs.io/ "null") - Handles SQLAlchemy database migrations.

        -   [psycopg2-binary](https://pypi.org/project/psycopg2-binary/ "null") - PostgreSQL database adapter for Python.

    -   **Authentication & Forms:**

        -   [Authlib](https://authlib.org/ "null") - For integrating Google OAuth login.

        -   [Flask-Session](https://www.google.com/search?q=https://pythonhosted.org/Flask-Session/ "null") - For server-side session management.

        -   [Flask-WTF](https://flask-wtf.readthedocs.io/ "null") - For handling web forms.

    -   **Utilities:**

        -   [Flask-Admin](https://flask-admin.readthedocs.io/ "null") - For the admin interface.

        -   [Beautiful Soup (bs4)](https://www.crummy.com/software/BeautifulSoup/ "null") - For web scraping tasks.

        -   [Markdown](https://pypi.org/project/Markdown/ "null") & [markdownify](https://pypi.org/project/markdownify/ "null") - For converting between HTML and Markdown.

        -   [readtime](https://pypi.org/project/readtime/ "null") - To calculate the estimated read time for blogs.

        -   [python-dotenv](https://pypi.org/project/python-dotenv/ "null") - For managing environment variables.

🛠️ Getting Started
-------------------

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Make sure you have the following software installed on your machine:

-   [Python](https://www.python.org/downloads/ "null") (3.8 or higher) & pip

-   [PostgreSQL](https://www.postgresql.org/download/ "null")

-   [Git](https://git-scm.com/downloads "null")

-   A code editor like [VS Code](https://code.visualstudio.com/ "null")

### Installation

1.  **Clone the repository:**

    ```
    git clone https://github.com/RF-Fahad-Islam/Bloggers-Community.git
    cd Bloggers-Community

    ```

2.  **Setup the Backend (Flask Server):**

    -   Navigate to the `server` directory.

        ```
        cd server

        ```

    -   Create and activate a virtual environment:

        ```
        # For macOS/Linux
        python3 -m venv venv
        source venv/bin/activate

        # For Windows
        python -m venv venv
        .\venv\Scripts\activate

        ```

    -   Install the required Python packages:

        ```
        pip install -r requirements.txt

        ```

    -   Set up your PostgreSQL database and create a `.env` file in the `/server` folder with your credentials:

        ```
        # Example for PostgreSQL
        DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME"

        # Secret key for sessions and forms
        SECRET_KEY="your_super_secret_key_here"

        # Google OAuth Credentials
        GOOGLE_CLIENT_ID="your_google_client_id"
        GOOGLE_CLIENT_SECRET="your_google_client_secret"

        ```

    -   Initialize and upgrade the database with Flask-Migrate:

        ```
        flask db init  # Only run this the very first time
        flask db migrate -m "Initial migration"
        flask db upgrade

        ```

3.  **Frontend Setup:**

    -   The frontend consists of static HTML, CSS, and JavaScript files. **No installation is required.**

4.  **Run the Application:**

    -   **Start the Backend Server:** From the `/server` directory (with the virtual environment activated), run:

        ```
        flask run

        ```

        The server will start on `http://127.0.0.1:5000`.

    -   **Access the Frontend:** Open your web browser and navigate to `http://127.0.0.1:5000`. The Flask application will serve the HTML pages directly.

Usage
-----

Once the application is running, you can:

-   Register or log in with your Google account.

-   Navigate the site to read blogs from all users.

-   Create and publish your own posts using a Markdown editor.

-   Update or delete your own posts.

-   Access the admin panel (if you have admin privileges) to manage the site.

🤝 Contributing
---------------

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project

2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)

3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)

4.  Push to the Branch (`git push origin feature/AmazingFeature`)

5.  Open a Pull Request
