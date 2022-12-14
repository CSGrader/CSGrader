import subprocess, os, json

# Create the assignment directory if it does not already exist
try:
  os.mkdir("./assignment/")
except:
  pass

# Remove the cache directories from previous runs
subprocess.Popen(['rm', '-rf', './.cache/', './submissions/']).communicate()

# Unzip the submissions into a cache directory
subprocess.Popen(['unzip', '-o', './assignment/*.zip', '-d', './.cache/']).communicate()

# Get the list of students, and create another cache directory
students = os.listdir('.cache')
os.mkdir('./submissions/')

processes = []  # The list of running unzip processes
snames = []     # The list of student names

# Clear the screen
def clear():
  os.system('cls' if os.name == 'nt' else 'clear')

# Get the list of any already-graded students, and load them into the grades list
clear()
grades_list = {}
if 'grades.json' in os.listdir('./assignment/'):
  grades_list = json.load(open('./assignment/grades.json'))


# === [Setup] === #
# Get the maximum number of points available for earning
maxpoints = input("What is the maximum number of points available for this assignment? [20] ")
if maxpoints == '':
  maxpoints = 20
else:
  maxpoints = int(maxpoints)



# Queue extraction of the latest submission to the ./submissions/{Student Name}/ folder
# for i, s in enumerate(students)
for s in students:
  # Get the latest attempts' directory
  attempts = os.listdir('./.cache/'+s)
  latest = attempts[len(attempts) - 1]

  # Reformat students' names from "Last, First - UserID" to "First_Last", and add it to the list of student names
  name = s.split(' - ')[0].split(', ')
  name = f"{name[1]}_{name[0]}"
  snames.append(name)

  # Queue unzip of each students' assignment
  processes.append(subprocess.Popen(['unzip', '-o', f'./.cache/{s}/{latest}/*', '-d', './submissions/'+name]))

# Wait for all extraction processes to finish
for p in processes:
  p.communicate()

# Load the configuration file
config = json.load(open('./config.json'))

# Define a simple Yes/No input mechanism
def ask(q, y=None):
  # Get the user input
  i = input(f"{q} [Y/n] ").lower().replace(' ', '')

  # If the user selects yes
  if i in ('y', 'yes', ''):
    if y != None:
      y()
    return True

  # If the user selects no
  elif i in ('n', 'no'):
    return False

  # Retry if the user enters something invalid
  else:
    return ask(q, y)



# Initialize the classname variable
CLASSNAME = None



# Get the name of the java class
def cn(s):
  # Get java files
  jlist = [f.strip('.java') for f in (os.listdir(f'./submissions/{s}/'))]

  # Format the output for showing the java files
  for i, f in enumerate(jlist):
    print(f'({i}) {f}', end='\t')
  print()

  # Ask the user for the correct main class
  try:
    # Use the input to get the class name
    return jlist[int(input(f'Select the main class file: [{jlist[0]} (0)] '))]
  except ValueError:
    # Use the first class if the user just presses enter
    return jlist[0]
  except:
    # Retry if the user enters something invalid
    return cn(s)


# The logic for running a single student's submission
def runJava(rc, cwd):
  print('\n== [BEGIN OUTPUT] ==')
  subprocess.call(rc, cwd=cwd)
  print('== [END OUTPUT] ==\n')


# The logic for grading a single student
def grade_submission():
  gr = input(f"What is the grade for this submission? [{maxpoints}/{maxpoints}] ")
  grs = gr.split('/')
  if gr == '':
    # If the user just presses enter
    grade = 100
    grpts = maxpoints
  elif gr.endswith('%'):
    # If the user enters a percentage
    grade = float(gr.strip('%'))
    grpts = (grade / 100) * maxpoints
  elif len(grs) == 1:
    # If the user enters a grade as points out of the maximum points
    grpts = float(gr)
    grade = (grpts / maxpoints) * 100
  elif len(grs) == 2:
    # If the user enters a grade as points out of a custom maximum points
    grade = (float(grs[0]) / float(grs[1])) * 100
    grpts = grade * maxpoints
  else:
    # Retry if the user enters something invalid
    grpts, grade = grade_submission()

  return grpts, grade



# === [Submission Execution] === #
# Iterate through each student's submission
for s in snames:
  # Assign the main class name if it has not already been assigned
  if not CLASSNAME:
    clear()
    CLASSNAME = cn(s)

  # Check if the student has not already been graded, and ask if a regrade is desired
  clear()
  if (s.replace('_', ' ') not in grades_list.keys()) or ask(f"{s.replace('_', ' ')} has already been graded. Would you like to regrade them?"):
    print(f'Grading {s.replace("_", " ")}...')

    # Generate the command for compiling the java files, and print the contents of each file
    compilecmd = config['compile'].copy()
    for k in os.listdir(f'./submissions/{s}/'):
      compilecmd.insert(1, f'./submissions/{s}/{k}')
      print(f'==========\n{k}\n==========')
      f = open(f'./submissions/{s}/{k}')
      print(f.read()+'\n\n\n\n')
      f.close()

    # Fix the paths in the compile command
    for i, x in enumerate(compilecmd):
      compilecmd[i] = x.replace('%STUDNAME%', s)

    # Fix the paths in the run command
    runcmd = config['run'].copy()
    for i, x in enumerate(runcmd):
      runcmd[i] = x.replace('%STUDNAME%', s).replace('%EXEC%', CLASSNAME)


    # Ask the user if they would like to compile the java files, and if so, ask if they would also like to run the program
    print('\n\nRUNNING: ' + ' '.join(compilecmd))
    if ask('Compile the program?', lambda : subprocess.call(compilecmd)):
      print('\n\nRUNNING: ' + ' '.join(runcmd))
      ask('Run the program?', lambda : runJava(runcmd, f'./submissions/{s}/'))

    # Ask the user for the student's grade
    grpts, grade = grade_submission()
    grades_list[s.replace('_', ' ')] = {'points': f'{grpts}/{maxpoints}', 'grade': f'{grade}%'}


# Export the grades to the grades.json file
json.dump(grades_list, open('./assignment/grades.json', 'w'))

# Remove the cache directories
subprocess.Popen(['rm', '-rf', './.cache/', './submissions/']).communicate()

# Print the grades
clear()
for n, g in grades_list.items():
  print(f"{n}: {g['points']} ({g['grade']})")


