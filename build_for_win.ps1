python -m venv venv
Write-Host "Created virtual environment..."
.\venv\Scripts\activate

New-Item -ItemType Directory -Name tmp
Copy-Item -Path .\quizer -Destination .\tmp\quizer -Recurse
Remove-Item -Recurse .\quizer

Write-Host "===========================================Start loading requirements==========================================="
pip install --no-cache-dir -r requirements.txt
Write-Host "=========================================Successfully loaded requeirments======================================="

django-admin startproject quizer
$SECRET_KEY = Get-Content .\quizer\quizer\settings.py | Where-Object {$_.startsWith('SECRET_KEY') } | ForEach-Object { $_.split("'") }
$SECRET_KEY = $SECRET_KEY[1]

Set-Location quizer
python manage.py startapp main
Set-Location ..
Remove-Item -Recurse quizer
Copy-Item -Path .\tmp\quizer -Destination .\quizer -Recurse

$OLD_SECRET_KEY = (Get-Content .\quizer\quizer\settings.py | Where-Object {$_.startsWith('SECRET_KEY') } | ForEach-Object { $_.split("'") })[1]
Get-Content ./settings.py | ForEach-Object { If ( $_.startsWith('SECRET_KEY') ) { $_.replace($OLD_SECRET_KEY, $SECRET_KEY) >> tmp } Else { $_ >> tmp } }
Move-Item -Path .\tmp -Destination .\quizer\quizer\settings.py

Remove-Item -Recurse tmp
Write-Host "===========================================Initialized django app==============================================="
Write-Host "==========================================Enter configuration data============================================="
$MONGO_HOST = Read-Host "MongoDB host: "
If ($MONGO_HOST -eq "")
{
  $MONGO_HOST="localhost"
}
Write-Output "MONGO_HOST = '$MONGO_HOST'" >> config.py

$MONGO_PORT = Read-Host "MongoDB port: "
If ($MONGO_PORT -eq "")
{
  $MONGO_PORT="27017"
}
Write-Output "MONGO_PORT = '$MONGO_PORT'" >> config.py

$MONGO_USER = Read-Host "MongoDB user: "
If ($MONGO_HOST -eq "")
{
  $MONGO_USER=""
}
Write-Output "MONGO_USER = '$MONGO_USER'" >> config.py

$MONGO_PASSWORD = Read-Host "MongoDB password: "
If ($MONGO_PASSWORD -eq "")
{
  $MONGO_PASSWORD=""
}
Write-Output "MONGO_PASSWORD = '$MONGO_PASSWORD'" >> config.py

$MONGO_DBNAME = Read-Host "MongoDB database name: "
If ($MONGO_DBNAME -eq "")
{
  $MONGO_DBNAME="quizer"
}
Write-Output "MONGO_DBNAME = '$MONGO_DBNAME'" >> config.py

Copy-Item -Path .\config.py -Destination .\quizer\quizer\config.py
Move-Item -Path .\config.py -Destination .\quizer\main\config.py

python .\quizer\manage.py makemigrations
python .\quizer\manage.py migrate

Write-Host "===========================================Start creating groups==============================================="

Write-Host 'from django.contrib.auth.models import Group; l = Group(id=1, name="lecturer"); l.save()' | python .\quizer\manage.py shell
Write-Host "Created 'lecturer' group"
Write-Host 'from django.contrib.auth.models import Group; s = Group(id=2, name="student"); s.save()' | python .\quizer\manage.py shell
Write-Host "Created 'student' group"
Write-Host "===========================================Enter superuser info==============================================="
python .\quizer\manage.py createsuperuser
Write-Host 'from django.contrib.auth.models import User; a = User.objects.get(id=1); a.groups.add(1); a.save(); print("Added user %s to group %s" % (a.username, "lecturer"))'  | python .\quizer\manage.py shell
Write-Host 'from django.contrib.auth.models import User; s = User(id=4, username="user"); s.set_password("password"); s.groups.add(2); s.save()' | python .\quizer\manage.py shell
Write-Host "Added user 'user' with password 'password' to group 'student'"
Write-Host "from main.models import QuestionsStorage; strg = QuestionsStorage.connect_to_mongodb(host='$MONGO_HOST', port='$MONGO_PORT', db_name='$MONGO_DBNAME'); strg.add_one(question={'formulation': 'First question with multiselect', 'tasks_num': 3, 'multiselect': True, 'with_images': False, 'options': [{'option': 'First true option', 'is_true': True}, {'option': 'Second false option', 'is_true': False}, {'option': 'Third true option', 'is_true': True}]}, test_id=1); strg.add_one(question={'formulation': 'Second question with single answer', 'tasks_num': 2, 'multiselect': False, 'with_images': False, 'options': [{'option': 'False option', 'is_true': False}, {'option': 'True option', 'is_true': True}]}, test_id=1)" | python .\quizer\manage.py shell
