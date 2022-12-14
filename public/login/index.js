// Send XHR to recieve the public key
var xhr = new XMLHttpRequest();
xhr.open("GET", "/api/public_key", true);
xhr.onreadystatechange = function() {
  if (xhr.readyState == 4) {
    window.pub = xhr.responseText;
  }
}
xhr.send();

function login() {
  $.post("/api/login", {
    username: $("#username").val(),
    password: RSA.encode(window.pub, $("#password").val())
  });
}

function register() {
  $.post("/api/register", {
    username: $("#username").val(),
    password: RSA.encode(window.pub, $("#password").val())
  });
}

