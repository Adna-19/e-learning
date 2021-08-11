# e-learning

E-learning platform is a web-application built on top of Django (High level framework written in python). In Django we use the concept of app for single individual feature. Each single feature is packaged into a single app. In this application, we have two types of users, teachers and students. A teacher can create courses, adds modules to the courses and can add content to each module. A user with teacher account will have access to the CMS built for content creators. On the other hand, a student is the public visitor of our application, who can view courses and can take courses. A student is allowed to give reviews on courses. Moreover we have two types of courses, free courses and paid courses. Student can directly enroll itself in a free course, but for a paid course, student will first purchase the course and after successful payment, student will be enrolled in that course. Students can give reviews and ratings on a certain course. Each course consists of multiple modules/chapters containing quizzes, videos, text, images, files(pdf, docx, ppt). The project contains a blog app for content sharing through articles. A teacher can also write articles on the blog and students can read and clap on these articles. A quiz app is developed for creating quizzes and managing results of each student in a certain quiz. For the better performance, In-memory caching is done through the use of Redis(NoSQL, In-memory Database and message broker). A custom API is generated for providing data to third-party applications or Front-end i.e React, Vue or Angular.

## Project consists of 4 Apps

 - **Accounts**
 - **Courses**
 - **Blog**
 - **Quiz**

## Requirements

 - **Python**  (2.7+)
 - **Django**
 - **Redis**
 - **Browser Chrome/Firefox**

## Installation
Clone the repository and create your virtual environment using **virtualenv/pyenv** . I'm using virtualenv.

    virtualenv myenv
   Activate the environment using:

	source myenv/bin/activate     # on Linux/Mac

    myenv/Scripts/activate		  # on Windows

install all the dependencies in your environment from **requirments.txt** file by using following command:

    pip install -r requirements.txt

First of all collect static files, make sure you are in the directory where **manage.py** is accessible:

    python manage.py collectstatic  
Then migrate all the database models using:

    python manage.py makemigrations
    python manage.py migrate

Now create your superuser using:

    python manage.py createsuperuser --user "name" --email "email"

After creating superuser, now you can simply fireup the server by:

    python manage.py runserver

Then Goto: http://127.0.0.1:8000/course/home/

Now that you are a superuser, In order to access Teachers CMS or Students Dashboard, you have to signup for a student/teacher account. Then a user_role will be attached to your account, based on that you will be provided with access rights. Now if you are a student, you can buy/learn/complete courses or if you are teacher you can create courses/quizzes/articles and publish them.

## Features

 - **Paypal Payment Gateway**
 - **Polymorphic Database models for Course Contents**
 - **Caching for better performance**
 - **Constant Backups**
 - **Authentication via google**
 - **Email Verification on SignUp**
 - **Cookie based Shopping Cart**
 - **REST API generated**

## Future Work

 - Using React/Vue for Client Side.
 - More robust Payment Gateway like Stripe.
 - Course recommendations using association analysis (ML)
 - Q/A Forum
 -  Coupon
 - Some code optimizations
