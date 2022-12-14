import subprocess, os, json, easygui, time, multiprocessing
from flask import redirect as FLASK_REDIRECT, session, request
from webappify import WebApp as webappify
from . import Encryption

sdir = os.path.expanduser("~/Desktop/Grader")

# Create the assignment directory if it does not already exist
try:
  os.mkdir(sdir)
except FileExistsError:
  pass

try:
  os.mkdir(f"{sdir}/assignment/")
except FileExistsError:
  pass

# Remove the cache directories from previous runs
subprocess.Popen(['rm', '-rf', f'{sdir}/cache/', f'{sdir}/submissions/']).communicate()



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

# Create Public and Private login keys
priv, pub = Encryption.RSA.newkeys()

pw_pub0 = None
pw_pub1 = None

try:
  pw_pub0, pw_pub1 = json.load(open(f'{sdir}/data.json'))['password_keys']
except FileNotFoundError:
  print('No accounts file found. Generating keys and creating an admin account...')
  # Create Password Encryption keys
  # I was too lazy to implement SHA, so I just used RSA and threw away the private key
  pw_priv0, pw_pub0 = Encryption.RSA.newkeys()
  pw_priv1, pw_pub1 = Encryption.RSA.newkeys()
  del(pw_priv0)
  del(pw_priv1)
  
  # With this much stuff, I should probably switch to a database, which would
  # allow for multiple simultaneous connections of reading and writing course content
  json.dump({
    'password_keys': [
      pw_pub0,
      pw_pub1
    ],
    'org': {
      'default': {
        'name': 'Default Organization',
        'desc': 'Default organization',
        'users': {
          'admin': {
            # Create a default admin account, username: admin, password: admin
            'pwd': Encryption.RSA.encode(pw_pub0, Encryption.RSA.encode(pw_pub1, 'admin')),
            # Roles rank from highest to lowest being admin, teacher, assistant, student
            'roles': ['admin']
          }
        },
        'classes': {
          'Default AP CS A class': {
            'subject': 'AP CS A',
            'desc': 'Default AP CS A class',
            'users': {
              # Username: ['teacher', 'assistant', 'student']
              'admin': {'role': ['teacher'], 'content': {}}
            },
            'units': {
              'Unit 1 - Hello World': {
                'subtitle': 'Getting started with Java',
                'desc': 'This unit will teach you how to write your first Java program.',
                'content': {
                  '1.1 - Hello World': {
                    'desc': 'Write a program that prints "Hello World!" to the console.',
                    'points': 10,
                    'instructions': 'Use the System.out.println() method to print "Hello World!" to the console.',
                    'files': {
                      'HelloWorld.java': 'public class HelloWorld {\n  public static void main(String[] args) {\n    // Write your code here\n  }\n}'
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
  }, open(f'{sdir}/data.json', 'w'))
  print('Done. There is now an admin account with the username "admin" and the password "admin".')

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
  @app.route('/api/public_key')
  def api_public_key():
    return pub

  @app.route('/api/login', methods=['POST'])
  def api_login():
    data = request.get_json()
    print(data)
    users = json.load(open(f'{sdir}/data.json'))
    p = Encryption.RSA.encode(pw_pub0, Encryption.RSA.encode(pw_pub1, Encryption.RSA.decode(priv, data['password'])))
    print(p)
    if data['username'] in users.keys():
      if users['org']['default']['users'][data['username']]['pwd'] == p:
        session['username'] = data['username']
        return FLASK_REDIRECT('/dashboard')
      else:
        return p, 403
    else:
      return p, 403

  @app.route('/api/register', methods=['POST'])
  def api_register():
    data = request.get_json()
    users = json.load(open(f'{sdir}/data.json'))
    if data['username'] in users.keys():
      return '', 403
    else:
      users['org']['default']['users'][data['username']] = {'pwd': data['password'], 'roles': ['unverified']}
      json.dump(users, open(f'{sdir}/users.json', 'w'))
      session['username'] = data['username']
      return FLASK_REDIRECT('/dashboard')

  ## PENDING REWRITE ##
  @app.route("/files")
  def get_student_files():
    # Create a dict of dicts, files['student_name']['file_name'] = file_contents
    files = {}
    for s in os.listdir(f"{sdir}/submissions/"):
      files[s] = {}
      for f in os.listdir(f"{sdir}/submissions/{s}"):
        files[s][f] = open(f"{sdir}/submissions/{s}/{f}").read()

    # Convert files into JSON
    return json.dumps(files)


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
    subprocess.Popen(['unzip', '-o', f'{sdir}/assignment/*.zip', '-d', f'{sdir}/cache/']).communicate()

    # Get the list of students, and create another cache directory
    students = os.listdir(f'{sdir}/cache')
    os.mkdir(f'{sdir}/submissions/')

    # Queue extraction of the latest submission to the ./submissions/{Student Name}/ folder
    # for i, s in enumerate(students)
    processes = []  # The list of running unzip processes
    for s in students:
      # Get the latest attempts' directory
      attempts = os.listdir(f'{sdir}/cache/'+s)
      latest = attempts[len(attempts) - 1]

      # Reformat students' names from "Last, First - UserID" to "First_Last", and add it to the list of student names
      name = s.split(' - ')[0].split(', ')
      name = f"{name[1]}_{name[0]}"
      snames.append(name)

      # Queue unzip of each students' assignment
      processes.append(subprocess.Popen(['unzip', '-o', f'{sdir}/cache/{s}/{latest}/*', '-d', f'{sdir}/submissions/{name}']))

    # Wait for all extraction processes to finish
    for p in processes:
      p.communicate()
    return "Yep, that worked."


  @app.route("/save")
  def save():
    # Export the grades to the grades.json file
    json.dump(grades_list, open(f'{sdir}/assignment/grades.json', 'w'))

    # Remove the cache directories
    subprocess.Popen(['rm', '-rf', f'{sdir}/cache/', f'{sdir}/submissions/', f'{sdir}/assignment']).communicate()


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

  # Open a new QTWebEngine window
  def showWindow():
    wa = webappify('Schoology Grader', f'http://127.0.0.1:{pconfig["port"]}/', '')
    wa.run()

  proc = multiprocessing.Process(target=showWindow)
  # proc.start()


