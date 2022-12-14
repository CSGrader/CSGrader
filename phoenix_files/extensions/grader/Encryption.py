import random, math, zlib, base64, hashlib
# from Crypto import Random
# from Crypto.Cipher import AES as aesenc



# class AES:
#   BLOCK_SIZE = 16
#   pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
#   unpad = lambda s: s[:-ord(s[len(s) - 1:])]
#   def encode(plain_text, key):
#       private_key = hashlib.sha256(key.encode("utf-8")).digest()
#       plain_text = pad(plain_text)
#       iv = Random.new().read(aesenc.block_size)
#       cipher = aesenc.new(private_key, aesenc.MODE_CBC, iv)
#       return base64.b64encode(iv + cipher.encrypt(plain_text))
#   def decode(cipher_text, key):
#       private_key = hashlib.sha256(key.encode("utf-8")).digest()
#       cipher_text = base64.b64decode(cipher_text)
#       iv = cipher_text[:16]
#       cipher = aesenc.new(private_key, aesenc.MODE_CBC, iv)
#       return unpad(cipher.decrypt(cipher_text[16:]))



class Vignere:
  def encode(msg, key): 
    out = [] 
    ext = (key*abs(len(msg)-len(key)+1))[:len(msg)]
    for i in range(len(msg)): 
      x = (ord(msg[i]))+(ord(ext[i]))
      out.append(chr(x)) 
    return("".join(out)) 
  
  def decode(msg, key): 
    out = [] 
    ext = (key*abs(len(msg)-len(key)+1))[:len(msg)]
    for i in range(len(msg)): 
      x = int(ord(msg[i]))-(ord(ext[i]))
      out.append(chr(x)) 
    return("".join(out)) 



class RSA:
  def newkeys():
    a = random.SystemRandom().randint(2, 2000)
    b = random.SystemRandom().randint(2, 2000)
    a1 = random.SystemRandom().randint(2, 2000)
    b1 = random.SystemRandom().randint(2, 2000)
    M = (a * b) - 1
    e = (a1 * M) + a
    d = (b1 * M) + b
    n = ((e * d) - 1) / M
    pub = f"{str(int(n))},{str(int(e))}"
    priv = f"{str(int(n))},{str(int(d))}"
    pub_chars = ""
    for i in pub:
      pub_chars += str(ord(i))+"-"
    priv_chars = ""
    for i in priv:
      priv_chars += str(ord(i))+"-"
    priv_out = priv_chars.rstrip("-")
    pub_out = pub_chars.rstrip("-")
    return priv_out, pub_out
  
  def getkey(key):
    out = ""
    for i in key.split("-"):
      out += chr(int(i))
    out = out.split(",")
    return (int(out[0]), int(out[1]))
  
  def encode(pub, msg=""):
    pub = RSA.getkey(pub)
    to_char = list(msg)
    out = ""
    for char in to_char:
      out += str(((pub[1] * ord(char)) % pub[0])) + ";"
    return out.rstrip(';')
  
  def decode(priv, msg=""):
    priv = RSA.getkey(priv)
    charslist = msg.split(';')
    out = ""
    for char in charslist:
      out += chr(((int(char) * priv[1]) % priv[0]))
    return out



class Secure:
  def encode(msg, otheruser_pub, thisuser_priv, sym_key='a'):
    symmetric = Vignere.encode(msg, sym_key)
    signature = RSA.encode(thisuser_priv, symmetric)
    enmessage = RSA.encode(otheruser_pub, signature)
    return enmessage
  
  def decode(msg, otheruser_pub, thisuser_priv, sym_key='a'):
    signature = RSA.decode(thisuser_priv, msg)
    symmetric = RSA.decode(otheruser_pub, signature)
    demessage = Vignere.decode(symmetric, sym_key)
    return demessage


