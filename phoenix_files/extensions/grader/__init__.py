import subprocess, os, json, easygui, time
from flask import redirect as FLASK_REDIRECT

sdir = os.getcwd() + "/phoenix_files/extensions/grader"

# Create the assignment directory if it does not already exist
try:
  os.mkdir(f"{sdir}/assignment/")
except FileExistsError:
  pass

# Remove the cache directories from previous runs
subprocess.Popen(['rm', '-rf', f'{sdir}/.cache/', f'{sdir}/submissions/']).communicate()



# === [Setup] === #
# Set the default amount of points for the assignment
maxpoints = 20.

# Load the configuration file
config = json.load(open(f'{sdir}/config.json'))

# Create list for students' names
snames = []
student_settings = {}
doc_generated = []

# Get the list of any already-graded students, and load them into the grades list
grades_list = {}
if 'grades.json' in os.listdir(f'{sdir}/assignment/'):
  grades_list = json.load(open(f'{sdir}/assignment/grades.json'))


# # Define a simple Yes/No input mechanism
# def ask(q, y=None):
#   # Get the user input
#   i = input(f"{q} [Y/n] ").lower().replace(' ', '')
#
#   # If the user selects yes
#   if i in ('y', 'yes', ''):
#     if y != None:
#       y()
#     return True
#
#   # If the user selects no
#   elif i in ('n', 'no'):
#     return False
#
#   # Retry if the user enters something invalid
#   else:
#     return ask(q, y)






# # Get the name of the java class
# def cn(s):
#   # Get java files
#   jlist = [f.strip('.java') for f in (os.listdir(f'{sdir}/submissions/{s}/'))]
#
#   # Format the output for showing the java files
#   for i, f in enumerate(jlist):
#     print(f'({i}) {f}', end='\t')
#   print()
#
#   # Ask the user for the correct main class
#   try:
#     # Use the input to get the class name
#     return jlist[int(input(f'Select the main class file: [{jlist[0]} (0)] '))]
#   except ValueError:
#     # Use the first class if the user just presses enter
#     return jlist[0]
#   except:
#     # Retry if the user enters something invalid
#     return cn(s)


# The logic for grading a single student
# def grade_submission():
#   gr = input(f"What is the grade for this submission? [{maxpoints}/{maxpoints}] ")
#   grs = gr.split('/')
#   if gr == '':
#     # If the user just presses enter
#     grade = 100
#     grpts = maxpoints
#   elif gr.endswith('%'):
#     # If the user enters a percentage
#     grade = float(gr.strip('%'))
#     grpts = (grade / 100) * maxpoints
#   elif len(grs) == 1:
#     # If the user enters a grade as points out of the maximum points
#     grpts = float(gr)
#     grade = (grpts / maxpoints) * 100
#   elif len(grs) == 2:
#     # If the user enters a grade as points out of a custom maximum points
#     grade = (float(grs[0]) / float(grs[1])) * 100
#     grpts = grade * maxpoints
#   else:
#     # Retry if the user enters something invalid
#     grpts, grade = grade_submission()
#
#   return grpts, grade


# # === [Submission Execution] === #
# # Iterate through each student's submission
# for s in snames:
#   # Assign the main class name if it has not already been assigned
#   if not CLASSNAME:
#     CLASSNAME = cn(s)
#
#   # Check if the student has not already been graded, and ask if a regrade is desired
#   if (s.replace('_', ' ') not in grades_list.keys()) or ask(f"{s.replace('_', ' ')} has already been graded. Would you like to regrade them?"):
#     print(f'Grading {s.replace("_", " ")}...')
#
#     # Generate the command for compiling the java files, and print the contents of each file
#     compilecmd = config['compile'].copy()
#     for k in os.listdir(f'./submissions/{s}/'):
#       compilecmd.insert(1, f'./submissions/{s}/{k}')
#       print(f'==========\n{k}\n==========')
#       f = open(f'./submissions/{s}/{k}')
#       print(f.read()+'\n\n\n\n')
#       f.close()
#
#     # Fix the paths in the compile command
#     for i, x in enumerate(compilecmd):
#       compilecmd[i] = x.replace('%STUDNAME%', s)
#
#     # Fix the paths in the run command
#     runcmd = config['run'].copy()
#     for i, x in enumerate(runcmd):
#       runcmd[i] = x.replace('%STUDNAME%', s).replace('%EXEC%', CLASSNAME)
#
#
#     # Ask the user if they would like to compile the java files, and if so, ask if they would also like to run the program
#     print('\n\nRUNNING: ' + ' '.join(compilecmd))
#     if ask('Compile the program?', lambda : subprocess.call(compilecmd)):
#       print('\n\nRUNNING: ' + ' '.join(runcmd))
#       ask('Run the program?', lambda : runJava(runcmd, f'./submissions/{s}/'))
#
#     # Ask the user for the student's grade
#     grpts, grade = grade_submission()
#     grades_list[s.replace('_', ' ')] = {'points': f'{grpts}/{maxpoints}', 'grade': f'{grade}%'}

def send_from_directory(d, f):
  try:
    fp = open(f'{d}/{f}')
    fr = fp.read()
    fp.close()
    return fr
  except FileNotFoundError:
    return "File not found."


# Create dummy function to make the web server shut up
def postbuild(*args, **kwargs):
  pass


def run(app, pconfig={}, pcache={}):
  @app.route("/file/<student>/<file>")
  def get_student_file(student, file):
    return send_from_directory(f"{sdir}/submissions/{student}", file)


  @app.route("/doc/<student>")
  def get_student_doc(student):
    k = []
    for i in os.listdir(f'{sdir}/submissions/{student}/'):
      if i.endswith('.java'):
        k.append(f'{sdir}/submissions/{student}/'+i)
    if student not in doc_generated:
      subprocess.run(["javadoc", "-d", f"{sdir}/submissions/{student}/public", *k])
      subprocess.Popen(['python', '-m', 'phoenix', 'run', '-h', '-p', str(8190+snames.index(student))], cwd=f'{sdir}/submissions/{student}/')
      doc_generated.append(student)
      time.sleep(1)

    return FLASK_REDIRECT(f"http://127.0.0.1:{8190+snames.index(student)}/")

  @app.route("/upload")
  def upload_zip():
    fn = easygui.fileopenbox(msg="Select the Schoology zip file to upload", title="Upload Schoology Zip", default="*.zip", filetypes=["*.zip"])
    try:
      subprocess.Popen(["cp", fn, f"{sdir}/assignment/"]).communicate()
    except TypeError:
      return "Cancelled by user."


    # Unzip the submissions into a cache directory
    print('heehoo')
    subprocess.Popen(['unzip', '-o', f'{sdir}/assignment/*.zip', '-d', f'{sdir}/.cache/']).communicate()

    # Get the list of students, and create another cache directory
    students = os.listdir(f'{sdir}/.cache')
    print(students)
    os.mkdir(f'{sdir}/submissions/')

    # Queue extraction of the latest submission to the ./submissions/{Student Name}/ folder
    # for i, s in enumerate(students)
    processes = []  # The list of running unzip processes
    for s in students:
      # Get the latest attempts' directory
      attempts = os.listdir(f'{sdir}/.cache/'+s)
      latest = attempts[len(attempts) - 1]

      # Reformat students' names from "Last, First - UserID" to "First_Last", and add it to the list of student names
      name = s.split(' - ')[0].split(', ')
      name = f"{name[1]}_{name[0]}"
      snames.append(name)

      # Queue unzip of each students' assignment
      processes.append(subprocess.Popen(['unzip', '-o', f'{sdir}/.cache/{s}/{latest}/*', '-d', f'{sdir}/submissions/{name}']))

    # Wait for all extraction processes to finish
    for p in processes:
      p.communicate()
    return "Yep, that worked."


  @app.route("/save")
  def save():
    # Export the grades to the grades.json file
    json.dump(grades_list, open(f'{sdir}/assignment/grades.json', 'w'))

    # Remove the cache directories
    subprocess.Popen(['rm', '-rf', f'{sdir}/.cache/', f'{sdir}/submissions/']).communicate()


  @app.route("/run/<s>/<CLASSNAME>")
  def run(s, CLASSNAME):
    # Generate the command for compiling the java files, and print the contents of each file
    compilecmd = config['compile'].copy()
    for k in os.listdir(f'{sdir}/submissions/{s}/'):
      if k.endswith('.java'):
        compilecmd.insert(1, f'{sdir}/submissions/{s}/{k}')

    # Fix the paths in the compile command
    for i, x in enumerate(compilecmd):
      compilecmd[i] = x.replace('%STUDNAME%', s).replace('%SDIR%', sdir)

    # Fix the paths in the run command
    runcmd = config['run'].copy()
    for i, x in enumerate(runcmd):
      runcmd[i] = x.replace('%EXEC%', CLASSNAME)


    # Compile & run java program
    subprocess.run(compilecmd)
    return subprocess.Popen(runcmd, cwd=f'{sdir}/submissions/{s}/', stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()

  @app.route("/get_ungraded")
  def get_ungraded():
    glist = grades_list.keys()
    for i, n in enumerate(snames):
      if n not in glist:
        return json.dumps({'index': i, 'name': n})

  @app.route('/get_student/<s>')
  def get_student(s):
    if s not in student_settings.keys():
      fdat = {}
      for fn in os.listdir(f'{sdir}/submissions/{s}/'):
        fp = open(f'{sdir}/submissions/{s}/{fn}')
        fdat[fn] = fp.read()
        fp.close()

      student_settings[s] = json.dumps({
        'index': snames.index(s),
        'files': fdat
      })

    return student_settings[s]

