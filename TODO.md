# Todo
Grader:
 - Add README/rubric 
 - Add grading menu
 - Fix vertical height bug in main menu
 - Allow usage for paging to multiple students (only
   supports one as of now)
 - Add a list view for managing students and grades.
 - Provide a way for easy export of grades into other
   formats. (Maybe)

Future Experimental Ideas:
 - Add a class dashboard for teachers to manage students
   and assignments. Assignments can be created, deleted,
   or modified.
 - Class open-enrollment/require approval
 - Add option for multiple teachers
    - Could be a role-based permission system. Students sign
      in/up for the class, and the teacher(s) can assign
      roles to people, such as students, teachers, and assistants
 - Allow teachers to edit all students' code
 - Optionally allow students to request help from assistants
   and teachers (maybe). 
 - Allow 'pair programming' with students in three modes:
    - Student Selected: Students choose who they want to
      work with.
       - If multiple students request to work with a
         specific student, it can be automatically
         picked
       - Otherwise, the teacher will be able to resolve
         conflicts.
       - Students will dissapear from selection view once
         they are sucessfully in a pair.
    - Teacher Selected: Teachers select who each student
      works with.
    - Randomized: Students are automatically paired together
    - In all three modes, teachers have the option to
      rearrange selections.
 - Create cirriculum for AP CS A classes. (Maybe in the
   future for AP CS P & CS III classes?)
 - Add an IDE section for students to develop their code.
 - Local (and remote?) code scanning, for checking for
   malicious software (to protect the host server.)
 - Offline code editing (for when students can't access
   the server.)
    - Maybe create a Replit server for managing running
      code when it can't access the main server? That
      causes issues for if a district has blocked the 
      repl.co domain. Some other hosting solution may
      be better? If the teacher or district already
      has a domain, it could be used along with a hosting
      solution to provide access outside of class.
 - Automatic grading of student submissions? Check if students
   completed what the requirement asked of them. Perhaps there's
   a library that can achieve this (i.e. did the student use
   a loop, etc.). If there's not already a library for this,
   regex could be used. Number of lines & if correct information
   was output is easy to implement otherwise.
