# web-testing-tool

[![Build Status](https://travis-ci.com/vnkrtv/web-testing-tool.svg?branch=master)](https://travis-ci.com/vnkrtv/web-testing-tool)
![Docker](https://github.com/vnkrtv/web-testing-tool/workflows/Docker/badge.svg)
![Ubuntu](https://github.com/vnkrtv/web-testing-tool/workflows/Ubuntu/badge.svg)

### Description
Testing tool implemented on Django. Data storage is implemented in the DBMS MongoDB.  
Implemented system features:
- adding users and new study subjects using Django admin panel as superuser_only
- separation of access rights for 2 groups - 'student' and 'lecturer'
- adding tests and questions with images to them using the web interface as a user belonging to 'lecturer' group
- adding questions from existing files   
- editing existing questions and tests
- launching of existing tests by the user of 'lecturer' group, possibility of passing running tests by users of the 'student' group  
- possibility to view the results of students passing tests, storing all results in database with the possibility of further analysis  


### User's groups and opportunities
As a part of SMS microservices architecture the application provides the following rights and roles for users:

| SMS role | App group | Is superuser in app  | Opportunities                                                         |
|-------------|--------------------------------|--------------------------------|------------------------------------------------------------------------------|
| student     | student                        | -                              | 1. Passing launched tests                                              |
| teacher     | lecturer                       | -                              | 1. Tests editing<br>2. Questions editing<br>3. Subjects editing                              |
| admin       | lecturer                       | +                              | 1. Tests editing   <br>2. Questions editing<br>3. Subjects editing |

### Deploying  

As docker container:
- ```git clone https://github.com/LeadNess/web-testing-tool.git```
- ```cd web-testing-tool```
- ```docker build -t quizer .``` - create 'quizer' docker image with application 
- ```docker run -p <HOST_PORT>:80 -e MONGO_HOST=<MONGO_HOST> -e MONGO_PORT=<MONGO_PORT> -e MONGO_DNNAME=<MONGO_DNNAME> -e DEMONSTRATION_VARIANT=<y> URL_PREFIX=<URL_PREFIX> --name testing-app quizer ```

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
```
docker run -p <HOST_PORT>:80 \
  -e MONGO_HOST=<MONGO_HOST> \
  -e MONGO_PORT=<MONGO_PORT> \
  -e MONGO_DBNAME=<MONGO_DBNAME> \
  -e AUTH_URL=<AUTH_URL> \
  -e URL_PREFIX=<URL_PREFIX> \
  -e DEMONSTRATION_VARIANT=<y> \
  --name testing-app quizer
```
Container envs:  
- MONGO_HOST - MongoDB host, default - "localhost"
- MONGO_PORT - MongoDB port, default - 27017
- MONGO_DBNAME - MongoDB database name for app, default - "quizer"
- AUTH_URL - auth url for getting public key using JWT, default - "http://sms.gitwork.ru/auth/public_key/"
- URL_PREFIX - prefix for all paths in app (for example, "quizer"), default - ""
- DEMONSTRATION_VARIANT - if set, adds some data for demonstration purposes:
  - user 'user' with password 'password', who belongs to group 'student'
  - 2 added subjects 'Python' and 'OSS', 3 tests and 2 questions for one of them
  
For any building option, the application initially contains one user:
- user 'admin' with password 'admin', who belongs to group 'lecturer' and who is also a superuser_only, which is able to enter django admin panel and add new lecturers,students or superusers

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
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
quizer/main/decorators.py                    29      3    90%
quizer/main/forms.py                         17      0   100%
quizer/main/models.py                        30      1    97%
quizer/main/mongo.py                        141     41    71%
quizer/main/templatetags/main_extras.py      60      8    87%
quizer/main/utils.py                        140     63    55%
quizer/main/views.py                        338    115    66%
-------------------------------------------------------------
TOTAL                                       755    231    69%
```
For detailed report run:
- ```coverage report```  
- ```coverage html```  
- ```x-www-browser ./htmlcov/index.html``` for Linux or ```Invoke-Expression .\htmlcov\index.html``` for Windows

### Code inspection

For code inspection run - ```pylint quizer/main/*.py```:
- ```Your code has been rated at 10/10```