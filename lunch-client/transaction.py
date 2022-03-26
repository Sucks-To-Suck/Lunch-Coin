import json, requests, rsa, pickle, base64

# Runs and Returns the Config Data
def runConfig():
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
        json_file.close()

    return config

# Gets the Public Key from the File once it is needed
def getPublicKey():

    # Opens the Public Key File
    with open('public_key.txt', 'rb') as public_key_file:

        # Loads the computer jumbo in the file into usable object
        public_key = pickle.load(public_key_file)
        public_key_file.close()

        return public_key

# Gets the Private Key from the File once it is needed
def getPrivateKey():

    # Opens the Private Key File
    with open('private_key.txt', 'rb') as private_key_file:

        # Loads the computer jumbo in the file into usable object
        private_key = pickle.load(private_key_file)
        private_key_file.close()

        return private_key

# Gets the saved Ledger
def getLedger():

    # Opens the Ledger File
    with open('ledger.json', 'r') as ledger_file:

        # Loads the Ledger File Info
        ledger = json.load(ledger_file)
        ledger_file.close()

        return ledger

# Runs the Config to get needed info
config = runConfig()

# Gets the Public Key
public_key = getPrivateKey()

# Gets the locally saved ledger
ledger = getLedger()

# Ask User who they are sending coin to, and how much:
print('This program will allow you to send coin to another person on the network. False information entered will not count against you, only inconvenience you.\n')

t_n = input('Please enter the longer of the two numbers of the public key you are sending coin to.\n')
t_e = input('Please enter the smaller of the two numbers of the public key you are sending coin to.\n')

# Prevents users from sending coin that there local machine says they do not have
while True:
    t_amount = input('How much coin do you want to send?\n')

    # Converts the input to a float type
    t_amount = float(t_amount)

    # If you do not have enough coin according to your copy of the ledger
    if t_amount > ledger[str(public_key.n) + '_LCH']:
        print('Your wallet does not contain enough coin, try resyncing the ledger with the server.')

    # Otherwise
    else:
        break

# Variables
url = config['url'] + '/transaction'
message = config['message']

# Gets the Private Key
private_key = getPrivateKey()

# Signs a Message, proving authenticity
signed_message = rsa.sign(message.encode(), private_key, 'SHA-256')

# Converts the bytes to base 64 bytes (because problems occur if I did not), then to a string to be put into the json file (transaction_dic)
signed_message_str = str(base64.b64encode(signed_message), 'UTF-8')

# Creates the Dictionary of Info
transaction_dic = {
    'signature': signed_message_str,
    'message': message,
    't_n': t_n,
    't_e': t_e,
    't_amount': t_amount
}

# Makes the Dictionary a json string, to be sent over http
transaction_str = json.dumps(transaction_dic)

# Creates a Dictionary for your Public Key Info
public_key_dic = {
    'public_key.n': public_key.n,
    'public_key.e': public_key.e
}

# Puts the dictionary into a string for sending
public_key_str = json.dumps(public_key_dic)

# Wraps it all nicely into one bigger JSON
data = {'transaction_data': transaction_str, 'transaction_public_key': public_key_str}

# Sends the info to the server
r = requests.post(url, data=data)

# If Successful
if r.text == '0':
    print('<Transaction Successful!>')

# If not signed correctly
elif r.text == '1':
    print('<You signed the transaction fraudulently! Transaction not Successful!>')

# If you do not have enough Coin according to the server
elif r.text == '2':
    print('<You do not have enough Coin to send this Transaction. Try sending Less!>')

# Else
else:
    print('!!If you see this, it means you either are trying to send coin to a wallet that does not exist, or something went wrong.\n'
          'Try to use a valid wallet address again, but if the error persists, contact Josh about it!!')