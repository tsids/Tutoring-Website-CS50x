# CS50 Final Project
### [Video Demo](https://www.youtube.com/watch?v=M2T_En5b-e8)
### Description:
For my final project, I created a tutoring website called "The Tutor Spot". Students can sign up, choose their tutor, and begin to learn live from people around the world. Tutors can also register and teach their students. 

This site was built using flask. I used Bulma to style the pages and a bit of javascript to make the site more user friendly. I also used sqlite as the database, and included images and webfonts to make the site more readable.

Here is a run down of all the pages:

#### Error
An error page that shows up whenever something goes wrong, or when information is not entered properly in the login forms. It redirects the user to a page with a 404 error on it. The page also shows what went wrong.

#### Register
The register page lets a new user register themselves on the website. It asks for the user's name, username, email, password, and whether they want to register as a student or tutor. Once registered, it redirects them to the home page.

#### Login
The login page for every user. The user must enter their username, password, and select their learning status to determine if they are a student or tutor. Once logged in, it redirects the user to the homepage.

#### Index
This is the home page for every user. Every user is directed here with a flashing message after logging in or after updating the settings page. It also shows the student's current tutors.

#### Students
A tutor is able to see all registered students. Students can register from their own account, and will be able to apply to the teacher. Once they register, a list of students shows up on the tutor's side

#### Tutors
A page where a student can see all available tutors. They can apply to any tutor, and the tutor will be added to their list of current tutors on the home page. They can also message the tutor.

#### About
A brief description of the site. It includes the site's purpose, its goals, and the mission statement. The about page also shows the struggles of the site's growth and how the site achieved success.
#### Contact
The contact page allows a user to contact the site's owners. The user enters their name, email, and message, and will be directed to a confirmation page, confirming that the message was sent.

#### Settings
This page gives the user the option to change their password, and delete their account. Once an account is deleted, its information cannot be retrieved. It also displays a user's username, which they are unable to change.