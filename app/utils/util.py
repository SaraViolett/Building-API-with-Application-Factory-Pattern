from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "a super secret, secret key"#specific to this server

def encode_token(id): #using unique pieces of info to make our tokens specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(id) #This needs to be a string or the token will be malformed and won't be able to be decoded.
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decoration(*arg, **kwargs): #allow to recieved arguements that will get passed along to the next function
        token = None
        
        #look for token in the request
        #token attached to the header of the request. key="Authorization". "Bear <token>"
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        
        if not token:
            return jsonify({"error": "missing token"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.id = int(data['sub'])
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"error": "token is expired"}), 401
        except jose.exceptions.JWTError:
            return jsonify({"error": "invalid token"}), 401
        
        return f(*arg, **kwargs)
    
    return decoration
        