window.fname = "No File Loaded"
window.nameel;
window.codeel;
window.docel;
window.menuel;
window.fileel;
window.CLASSNAME = '';
window.files = {};

window.student = {
  output: "There was no output.",
  documentation: "",
  index: 0,
  files: {},
  name: "No Student Selected",
  file: "No File Loaded"
};

function setCode(v, e) {
  e.setValue(v);
  e.getSelection().clearSelection();
}

// Interface with the new API to get all students and their files
function getFiles() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/files');
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
        window.files = JSON.parse(xhr.responseText);
        getUngraded();
        }
    }
    xhr.send();
}

window.onload = function() {
  window.nameel = document.querySelector("#name");
  window.codeel = document.querySelector("#code");
  window.docel = document.querySelector("#doc");
  window.menuel = document.querySelector("#menu");
  window.fileel = document.querySelector("#files");
  window.cnel = document.querySelector("#classname");
  window.editor = ace.edit("code");
  editor.setTheme("ace/theme/terminal");
  editor.session.setMode("ace/mode/java");
  editor.setShowInvisibles(true);
  editor.setReadOnly(true);
  setSource();

  setInterval(function() {
    window.nameel.innerHTML = window.student.name.replace('_', ' ') + "<br>" + window.fname + "<br>" + "Show menu with Alt+M";
  }, 150);

  document.querySelector('html').addEventListener('keydown', function(e) {
    // console.log(e);
    if (e.altKey && [
      'z', 's',           // Show source
      'x', 'o',           // Show output
      'c', 'd',           // Show documentation
      'v', 'p',           // Previous student
      'b', 'n',           // Next student
      ' ', 'Enter',       // Run Code
      'm', 'Escape',      // Show menu
      'Control', 'Shift'  // Show grading options
    ].includes(e.key)) {
      e.preventDefault();
      if (e.key == 'z' || e.key == 's') {
        setSource();
      } else if (e.key == 'x' || e.key == 'o') {
        setOutput();
      } else if (e.key == 'c' || e.key == 'd') {
        setDocumenation();
      } else if (e.key == 'v' || e.key == 'p') {
        prevStudent();
      } else if (e.key == 'b' || e.key == 'n') {
        getUngraded();
      } else if (e.key == ' ' || e.key == 'Enter') {
        runCode();
      } else if (e.key == 'm' || e.key == 'Escape') {
        showMenu();
      } else if (e.key == 'Control' || e.key == 'Shift') {
        showGradingOptions();
      }
    }
  });


  getUngraded();
}

function changeFile(f) {
  window.fname = f;
  setSource();
}

function loadStudent(student) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/get_student/'+student);
  xhr.onreadystatechange = function() {
    window.fname = 'No File Loaded'
    if (xhr.readyState == 4) {
      window.student = {
        output: "Press Alt+Enter or Alt+Space to run the code.",
        documentation: "",
        index: 0,
        files: {},
        name: student
      };

      json = JSON.parse(xhr.responseText);
      for (var i = 0; i < Object.keys(json).length; i++) {
        var key = Object.keys(json)[i];
        window.student[key] = json[key];
      }

      var filenames = Object.keys(window.student.files)
      changeFile(filenames[0]); 

      var filenameList = ''
      for (var i = 0; i < filenames.length; i++) {
        var filename_i = filenames[i];
        filenameList += '<button class="file_list_item" onclick="changeFile(\''+filename_i+'\')">'+filename_i+'</button>';
      }
      fileel.innerHTML = filenameList;

      var files = Object.keys(window.student.files);
      var classdropdown = "<option value=''></option>";
      for (var i = 0; i < files.length; i++) {
        var fn = files[i].split('.')[0];
        classdropdown += "<option value='" + fn + "'>" + fn + "</option>";
      }
      window.cnel.innerHTML = classdropdown;
      // window.cnel.selectedIndex = indexof(window.cnel.options, window.CLASSNAME);
      var ol = Object.values(window.cnel.options);
      for (var i = 0; i < ol.length; i++) {
        if (ol[i].value == window.CLASSNAME) {
          window.cnel.selectedIndex = i;
          break;
        }
      }
    }
  }
  xhr.send();

  var docxhr = new XMLHttpRequest();
  docxhr.open('GET', '/doc/'+student+'/index.html');
  docxhr.onreadystatechange = function() {
    window.docel.innerHTML = '<iframe src="/doc/' + student + '" style="width: 100%; height: 100%; border: none; background-color: #fff;"></iframe>';
  }
  docxhr.send();
}

function uploadZip() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/upload');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      getUngraded();
    }
  }
  xhr.send();
  // showMenu();
}




function setSource() {
  try {
    window.docel.style.display = "none";
  } catch (e) {}
  window.codeel.style.display = "block";
  if (window.student.files == {} || window.fname == "No File Loaded") {
    setCode("No file loaded.", window.editor);
  } else {
    setCode(window.student.files[window.fname], window.editor);
  }
}

function setOutput() {
  try {
    window.docel.style.display = "none";
  } catch (e) {}
  window.codeel.style.display = "block";
  setCode(window.student.output, window.editor);
}



function getDoc() {
  if (window.student.name == "No Student Selected") {
    window.docel.innerHTML = "No student has been selected; could not generate documentation.";
  } //else if (window.student.documentation == "") {
  //   window.docel.innerHTML = "Generating javadoc...";
  //   setTimeout(getDoc, 250);
  // } else {
  //   window.docel.innerHTML = window.student.documentation;
  // }
}

function setDocumenation() {
  window.codeel.style.display = "none";
  window.docel.style.display = "block";
  getDoc();
}




function prevStudent() {
  console.log("Sending request to get previous student.");
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/prev/'+(window.student.index-1));
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      var data = JSON.parse(xhr.responseText);
      loadCode(data.file, data.student);
    }
  }
  xhr.send();
}

// Get next ungraded student (previously `nextStudent()`)
function getUngraded() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/get_ungraded');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      var data = JSON.parse(xhr.responseText);
      loadStudent(data.name);
      window.student.index = data.index;
    }
  }
  xhr.send();
}

function runCode() {
  if (window.CLASSNAME != '') {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/run/'+window.student.name+'/'+window.CLASSNAME);
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        window.student.output = xhr.responseText;
        setOutput();
      }
    }
    xhr.send();
  } else {
    window.student.output = "Please set the main class name in the menu (Alt+M).";
    setOutput();
  }
}

function showMenu() {
  window.menuel.classList = ["", "menu-active"][Number(window.menuel.classList == "")];
}

function showGradingOptions() {

}

function setClassName() {
  window.CLASSNAME = window.cnel.options[window.cnel.selectedIndex].value;
}
