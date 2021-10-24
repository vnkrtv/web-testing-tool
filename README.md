# web-testing-tool

[![Build Status](https://travis-ci.com/vnkrtv/web-testing-tool.svg?branch=master)](https://travis-ci.com/vnkrtv/web-testing-tool)
![Docker](https://github.com/vnkrtv/web-testing-tool/workflows/Docker/badge.svg)

### Fast deployment

`docker-compose up -d` - run app on 8000 port


### Description
Testing tool implemented on Django. Data storage is implemented in the DBMS PostgreSQL.  
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
- ```git clone https://github.com/vnkrtv/web-testing-tool.git```
- ```cd web-testing-tool```
- ```docker build -t quizer .``` - create 'quizer' docker image with application
- Set env vars in .env
- ```docker run --env-file=.env --name testing-app quizer ```

Next it's possible to set up automatic application resume after server reboot. Ubuntu solves this problem with the systemd initialization system:  
- ```sudo cp ./deploy/web-testing-tool.service /etc/systemd/system/web-testing-tool.service```
- ```sudo systemctl daemon-reload```
- ```sudo systemctl start web-testing-tool```

It's also possible to build a working application on the host system to be able to improve it. Required MongoDB and python3:
- ```git clone https://github.com/vnkrtv/web-testing-tool.git```
- ```cd web-testing-tool```
- ```./deploy/build_for_linux``` or ```powershell .\deploy\build_for_win.ps1```
- ```. ./venv/bin/activate``` or ```.\venv\Scripts\activate```
- ```python ./quizer/manage.py runserver``` or ```python .\quizer\manage.py runserver```
### Usage 
Run app by command:   
```
docker run -p <HOST_PORT>:80 \
  --env-file=.env \
  --name testing-app quizer
```
Container envs:  
- URL_PREFIX - prefix for all paths in app (for example, "quizer"), default - ""
- WORKERS_NUM - number of async workers
- PostgreSQL vars
 
To run test, you need:
- auth as user belong to group 'lecturer'
- go to '/available_tests/' page and run one of them. You can select test by subject and its name
    
After that you can pass test:
- auth as user belong to group 'student'
- go to '/available_tests/' page and run it

To stop test and see students results:
- auth as user belong to group 'lecturer' and launched the test
- go to '/running_tests/' page and stop it. Then you see detailed testing result of each student 
### Testing    
Run all tests with coverage by running (venv must be activated):   
- ```coverage run quizer/manage.py test main```

```
Name                               Stmts   Miss  Cover
------------------------------------------------------
api/permissions.py                    13      0   100%
api/serializers.py                   169     26    85%
api/views.py                         192     58    70%
main/consumers.py                     16     16     0%
main/decorators.py                    33      9    73%
main/forms.py                         22      3    86%
main/models.py                       133     13    90%
main/templatetags/main_extras.py      66     24    64%
main/utils.py                        198    128    35%
main/views.py                        302    154    49%
------------------------------------------------------
TOTAL                               1144    431    62%

```
For detailed report run:
- ```coverage report```  
- ```coverage html```  
- ```x-www-browser ./htmlcov/index.html``` for Linux or ```Invoke-Expression .\htmlcov\index.html``` for Windows

### Code inspection

For code inspection run - ```pylint quizer/main/*.py```:
- ```Your code has been rated at 10/10```