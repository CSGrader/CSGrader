window.RSA = {
  ord: function(s){return s.charCodeAt(0);},
  chr: String.fromCharCode,

  SystemRandom: function(num=8) {
    var randomvalue = window.crypto.getRandomValues(new Uint8Array(4096/8));
    var val = 1;
    for (var i = 0; i < num; i++) {
      val = val + randomvalue[i];
    }
    return val;
  },

  newkeys: function() {
    var a = RSA.SystemRandom();
    var b = RSA.SystemRandom();
    var a1 = RSA.SystemRandom();
    var b1 = RSA.SystemRandom();
    var M = (a * b) - 1;
    var e = (a1 * M) + a;
    var d = (b1 * M) + b;
    var n = ((e * d) - 1) / M;

    var pub = String(n)+","+String(e);
    var priv = String(n)+","+String(d);
    
    var pub_chars = "";
    for (var index = 0; index < pub.length; index++) {
      pub_chars += String(RSA.ord(pub[index]))+"-";
    }

    var priv_chars = "";
    for (var index = 0; index < priv.length; index++) {
      priv_chars += String(RSA.ord(priv[index]))+"-";
    }

    var priv_out = priv_chars.substr(0, priv_chars.length-1);
    var pub_out = pub_chars.substr(0, pub_chars.length-1);

    if (n==e || n==d) {
      return newkeys();
    } else {
      return [priv_out, pub_out];
    }
  },

  getkey: function(key) {
    var out = "";
    var key = key.split("-");
    for (var index = 0; index < key.length; index++) {
      out += String(RSA.chr(Number(key[index])));
    }
    out = out.split(",");
    return [BigInt(out[0]), BigInt(out[1])];
  },

  encode: function(pub, msg="") {
    var pub = RSA.getkey(pub);
    var out = "";
    for (var index = 0; index < msg.length; index++) {
      out += String(BigInt(pub[1] * BigInt(RSA.ord(msg[index]))) % BigInt(pub[0])) + ";";
    }
    return out.substr(0, out.length-1);
  },

  decode: function(priv, msg="") {
    var priv = RSA.getkey(priv);
    var charslist = msg.split(";");
    var out = "";
    for (var index = 0; index < charslist.length; index++) {
      out += RSA.chr(Number(BigInt(BigInt(charslist[index]) * priv[1]) % BigInt(priv[0])));
    }
    return out;
  }
};
