import sys
import datetime
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

def load_private_key_from_file(file_path: str) -> rsa.RSAPrivateKey:
    """Load a .pem file RSA key from disk"""
    try:
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
            )
            return private_key
    except FileNotFoundError:
        print(f"Error: cannot find file \'{file_path}\'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading API key from \'{file_path}\'", file=sys.stderr)
        sys.exit(1)

def load_access_key_from_file(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            kalshi_access_key = f.read().strip()
            if not kalshi_access_key:
                raise ValueError("Access key file is empty")
            return kalshi_access_key
    except FileNotFoundError:
        print(f"Error: cannot find file \'{file_path}\'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading Access key from \'{file_path}\'", file=sys.stderr)
        sys.exit(1) 

def sign_pss_text(private_key: rsa.RSAPrivateKey, text: str) -> str:
    # Before signing, we need to hash our message.
    # The hash is what we actually sign.
    # Convert the text to bytes
    message = text.encode('utf-8')

    try:
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    except InvalidSignature as e:
        raise ValueError("RSA sign PSS failed") from e

# methods: GET: retrieve data, POST: send an order, DELETE: remove an order, maybe more, but idk
def make_headers(access_key_file_location: str,     # file location of the access key
                 private_key_file_location: str,    # file location of the private key
                 method: str,                       # info above
                 path: str):                        # 
    # get the current time
    current_time = datetime.datetime.now()

    # convert the time to a timestamp (seconds since the epoch)
    timestamp = current_time.timestamp()

    # convert the timestamp to milliseconds
    current_time_milliseconds = int(timestamp * 1000)
    timestampt_str = str(current_time_milliseconds)

    # load the RSA private key
    private_key = load_private_key_from_file(private_key_file_location)
    
    # load the access key
    access_key = load_access_key_from_file(access_key_file_location)

    msg_string = timestampt_str + method + path

    sig = sign_pss_text(private_key, msg_string)

    return {
            'KALSHI-ACCESS-KEY': access_key,
            'KALSHI-ACCESS-SIGNATURE': sig,
            'KALSHI-ACCESS-TIMESTAMP': timestampt_str
        }
