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
$SECRET_KEY = (Get-Content .\quizer\quizer\settings.py | Where-Object {$_.startsWith('SECRET_KEY') } | ForEach-Object { $_.split("'") })[1]
Remove-Item -Recurse quizer
Copy-Item -Path .\tmp\quizer -Destination .\quizer -Recurse
Remove-Item -Recurse tmp

$SETTINGS = Get-Content .\deploy\settings
$SETTINGS = $SETTINGS.Replace('GENERATED_SECRET_KEY', $SECRET_KEY)

Write-Host "===========================================Initialized django app==============================================="
Write-Host "==========================================Enter configuration data============================================="
$MONGO_HOST = Read-Host "MongoDB host (default: 'localhost'): "
If ($MONGO_HOST -eq "")
{
  $MONGO_HOST="localhost"
}
$SETTINGS = $SETTINGS.Replace('MONGO_HOST', $MONGO_HOST)

$MONGO_PORT = Read-Host "MongoDB port (default: 27017): "
If ($MONGO_PORT -eq "")
{
  $MONGO_PORT="27017"
}
$SETTINGS = $SETTINGS.Replace('MONGO_PORT', $MONGO_PORT)

$MONGO_DBNAME = Read-Host "MongoDB database name (default: 'quizer'): "
If ($MONGO_DBNAME -eq "")
{
  $MONGO_DBNAME="quizer"
}
$SETTINGS = $SETTINGS.Replace('MONGO_DBNAME', $MONGO_DBNAME)
$SETTINGS = $SETTINGS.Replace('MONGO_TESTDBNAME', 'test_' + $MONGO_DBNAME)
Write-Output $SETTINGS > .\quizer\quizer\settings.py

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