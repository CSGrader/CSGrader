# CSGrader
CSGrader is a feature-filled but easy-to-use system to help Computer Science teachers in
easily grading assignments. It is built off of the Phoenix Web Server framework, and the
backend is written in python. 

## Install Required Dependencies
```bash
pip install phoenix-ws easygui
```
It also uses NW.JS for it's frontend UI. Install that, according to the method available
for your Operating System. (We might undo that, and make everything run entirely in the
browser, but for now, it is a requirement.)

## Start Server
```bash
python -m phoenix run
```

## Connect to Server
Open http://127.0.0.1:8080/ in your web browser
