# web-testing-tool

[![Build Status](https://travis-ci.com/LeadNess/web-testing-tool.svg?branch=master)](https://travis-ci.com/LeadNess/web-testing-tool)
![Docker](https://github.com/LeadNess/web-testing-tool/workflows/Docker/badge.svg)
### Description
Testing tool implemented on Django. Data storage is implemented in the DBMS MongoDB.  
Implemented system features:
- adding users and new study subjects using Django admin panel as superuser
- separation of access rights for 2 groups - 'student' and 'lecturer'
- adding tests and questions with images to them using the web interface as a user belonging to 'lecturer' group
- adding questions from existing files   
- editing existing questions and tests
- launching of existing tests by the user of 'lecturer' group, possibility of passing running tests by users of the 'student' group  
- possibility to view the results of students passing tests, storing all results in database with the possibility of further analysis  

### Deploying  

As docker container:
- ```git clone https://github.com/LeadNess/web-testing-tool.git```
- ```cd web-testing-tool```
- ```docker build -t quizer .``` - create 'quizer' docker image with application and MongoDB
- ```docker run -p 80:80 --name testing-app quizer ```

Next it's possible to set up automatic application resume after server reboot. Ubuntu solves this problem with the systemd initialization system:  
- ```sudo cp ./deploy/web-testing-tool.service /etc/systemd/system/web-testing-tool.service```
- ```sudo systemctl daemon-reload```
- ```sudo systemctl start web-testing-tool```

It's also possible to build a working application on the host system to be able to improve it. Required MongoDB and python3:
- ```git clone https://github.com/LeadNess/web-testing-tool.git```
- ```cd web-testing-tool```
- ```./deploy/build_for_linux``` or ```powershell .\deploy\build_for_win.ps1```
- ```. ./venv/bin/activate``` or ```.\venv\Scripts\activate```
- ```python ./quizer/manage.py runserver``` or ```python .\quizer\manage.py runserver```
### Usage 
Run app by command:   
- ```docker run -p 80:80 --name testing-app quizer```  
  
When you can connect to app in browser by following link: http://localhost:80.
This is a test version of the program, created for demonstration purposes.   
There are 2 users in this option:
- user 'admin' with password 'admin', who belongs to group 'lecturer' and who is also a superuser (so you can enter django admin panel and add new lecturers,students or superusers)
- user 'user' with password 'password', who belongs to group 'student'    

There are also 2 added subjects 'Python' and 'OSS', 3 tests and 2 questions for one of them.

To run test, you need:
- auth as user belong to group 'lecturer'
- go to '/tests/' page and run one of them. You can select test by subject and its name
    
After that you can pass test:
- auth as user belong to group 'student'
- go to '/tests/' page and run it

To stop test and see students results:
- auth as user belong to group 'lecturer' and launched the test
- go to '/running_tests/' page and stop it. Then you see detailed testing result of each student 
### Testing    
Run all tests with coverage by running (venv must be activated):   
- ```coverage run quizer/manage.py test main```

```
Name                        Stmts   Miss  Cover
-----------------------------------------------
quizer/main/decorators.py      27      1    96%
quizer/main/models.py          27      0   100%
quizer/main/mongo.py           92      5    95%
quizer/main/views.py          244     23    91%
-----------------------------------------------
TOTAL                         390     29    93%
```
For detailed report run:
- ```coverage report```  
- ```coverage html```  
- ```x-www-browser ./htmlcov/index.html``` for Linux or ```Invoke-Expression .\htmlcov\index.html``` for Windows

### Code inspection

For code inspection run - ```pylint quizer/main/*.py```:
- ```Your code has been rated at 10/10```