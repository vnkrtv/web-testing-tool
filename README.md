# Quizer

### Description
Testing system implemented on Django. Data storage is implemented in the DBMS MongoDB.  
Implemented system features:
- adding users and new study subjects using Django admin panel as superuser
- separation of access rights for 2 groups - 'student' and 'lecturer'
- adding tests and questions with images to them using the web interface as a user belonging to 'lecturer' group
- adding questions from existing files   
- editing existing questions and tests
- launching of existing tests by the user of 'lecturer' group, possibility of passing running tests by users of the 'student' group  
- possibility to view the results of students passing tests, storing all results in database with the possibility of further analysis  

Coming soon:
- analysis of student test results
### Installation
- ```git clone https://github.com/LeadNess/Quizer.git```
- ```cd Quizer```
- Build django application - ```./build_for_linux``` or ```powershell .\build_for_win.ps1```
- ```./build_docker``` - create 'quizer' docker image
### Usage
Run app by command:   
- ```docker run quizer```  
  
When you can connect to app in browser by following link: http://172.17.0.2:8000.
This is a test version of the program, created for demonstration purposes.   
There are 2 users in this option:
- user 'admin' with password 'admin', who belongs to group 'lecturer' and who is also a superuser (so you can enter django admin panel)
- user 'user' with password 'password', who belongs to group 'student'    

There is also 1 added subject 'Python', 1 added test 'PZ1' and 2 added questions.
### Testing    
Run all tests with coverage by running (venv must be activated):   
```coverage run quizer/manage.py test main```
#### pylint   
- main/models.py:  
```Your code has been rated at 10/10```  
- main/views.py:  
```Your code has been rated at 10/10```  
- main/tests.py:  
```Your code has been rated at 10/10```
- main/decorators.py:  
```Your code has been rated at 10/10``` 
#### coverage   
```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
quizer/main/admin.py                         3      0   100%
quizer/main/apps.py                          4      0   100%
quizer/main/config.py                        5      0   100%
quizer/main/decorators.py                   21      0   100%
quizer/main/migrations/0001_initial.py       7      0   100%
quizer/main/migrations/__init__.py           0      0   100%
quizer/main/models.py                      108      5    95%
quizer/main/tests.py                       258      0   100%
quizer/main/urls.py                          4      0   100%
quizer/main/views.py                       232     23    90%
------------------------------------------------------------
TOTAL                                      642     28    96%
```
For detailed report run:
- ```coverage html```  
- ```x-www-browser ./htmlcov/index.html``` for Linux or ```Invoke-Expression .\htmlcov\index.html``` for Windows
