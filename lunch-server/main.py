import cherrypy, rsa, pickle, json, hashlib, base64

# Runs and Returns the Config Data
def runConfig():

    # Opens the Config File
    with open('config.json', 'r') as json_file:

        # Saves the JSON data
        config = json.load(json_file)
        json_file.close()

    return config

# Gets the saved Ledger
def getLedger():

    # Opens the Ledger File
    with open('ledger.json', 'r') as ledger_file:

        # Saves the Ledger Data
        ledger = json.load(ledger_file)
        ledger_file.close()

        return ledger

# Dumps the Ledger Data
def dumpLedger(ledger):

    # Opens the Ledger File
    with open('ledger.json', 'w') as ledger_file:

        # Dumps the Ledger Data
        json.dump(ledger, ledger_file)
        ledger_file.close()

def getBlock():
    with open('block.json', 'r') as block_file:
        block = json.load(block_file)
        block_file.close()

        return block

def dumpBlock(block):
    with open('block.json', 'w') as block_file:
        json.dump(block, block_file)
        block_file.close()

# Checks if there are keys generated, if not then it generates a public private key pair
def publicPrivateGen(config_file):

    # If they do not exist
    if config_file['generated_keys'] == 'false':
        print('<Wallet not Detected! Generating a New One>')

        # Generates the Key Pair
        (public_key, private_key) = rsa.newkeys(1024)

        # Updates the Config
        config_file['generated_keys'] = 'true'

        # Updates the Config (cont)
        with open('config.json', 'w') as json_file:
            json.dump(config_file, json_file)
            json_file.close()

        # Saves the Public Key
        with open('public_key.txt', 'wb') as public_key_file:
            pickle.dump(public_key, public_key_file)
            public_key_file.close()

        # Saves the Private Key
        with open('private_key.txt', 'wb') as private_key_file:
            pickle.dump(private_key, private_key_file)
            private_key_file.close()

        print('<Wallet Generated!>')

    else:
        print('<Wallet Detected!>')

# Gets the Public Key from the File once it is needed
def getPublicKey():

    # Opens the Public Key File
    with open('public_key.txt', 'rb') as server_public_key_file:

        # Loads the computer jumbo in the file into usable variable
        server_public_key = pickle.load(server_public_key_file)
        server_public_key_file.close()

        return server_public_key

# Gets the Private Key from the File once it is needed
def getPrivateKey():

    # Opens the Private Key File
    with open('private_key.txt', 'rb') as server_private_key_file:

        # Loads the computer jumbo in the file into usable variable
        server_private_key = pickle.load(server_private_key_file)
        server_private_key_file.close()

        return server_private_key

# Runs the sha 256 function on the inputted string
def lunchHash(function_input):

    # The String needs to be a byte string, so this converts it
    input_hash = bytes(function_input, 'utf-8')

    # Specifies that we are using sha256 as the choice of hash
    m = hashlib.sha256()

    # Runs sha 16,000,000 times to make the hash take much longer
    for temp_var in range(16000000):

        # Updates the input
        m.update(input_hash)

        # Hashes and Returns the Bytes
        loop_hash = m.digest()

        # Used to cycle the new hash again
        input_hash = loop_hash

    # Runs the Finale Hash, but outputs it as a string
    m.update(input_hash)
    finale_hash = m.hexdigest()

    # Returns the finale hash
    return finale_hash

# A class with functions used by cherrypy to detect and execute if someone interacts with the server
class App:

    # The cherry.expose makes the function name a possible website to connect to, and dedicates a thread to the function
    # This function runs when someone connects to (this server)/ledger_update, updating their copy of the ledger
    @cherrypy.expose
    def ledger_receive(self):

        # Opens and reads the ledger file
        with open('ledger.json', 'r') as json_file:

            # Reads the ledger file
            data = json_file.read()

        # Sends the data to the client
        return data

    # Runs when a Client adds a New Wallet to the Ledger
    @cherrypy.expose
    def add_new_wallet(self, json_str):

        # Gets the Ledger
        ledger = getLedger()

        # Loads the Dictionary Data from the sent JSON
        new_public_dic = json.loads(json_str)

        # Converts the Public Key.n to a string for the json file key
        new_public_str = str(new_public_dic['public_key.n'])

        # Saves the Public Key
        ledger[new_public_str + '_n'] = new_public_dic['public_key.n']
        ledger[new_public_str + '_e'] = new_public_dic['public_key.e']

        # Defines that they have no coin
        ledger[new_public_str + '_LCH'] = 0

        # Saves the info to the Ledger
        dumpLedger(ledger)

        print('<New Wallet Generated>')

        return '0'

    # Runs when a transaction is submitted
    @cherrypy.expose
    def transaction(self, transaction_data, transaction_public_key):

        # Loads the JSON strings into dictionary's
        new_transaction = json.loads(transaction_data)
        new_public_key = json.loads(transaction_public_key)

        # Converts the sent string into a byte string, then decodes that base 64 byte string into a normal byte string for the verify function
        base64_byte_str = bytes(new_transaction['signature'], 'utf-8')
        signature = base64.b64decode(base64_byte_str)

        # Fills the public key with their public key
        public_key = getPublicKey()
        public_key.n = new_public_key['public_key.n']
        public_key.e = new_public_key['public_key.e']

        # Makes the message that is used in verification a byte string
        message = bytes(new_transaction['message'], 'utf-8')

        # Verifies the signature
        verify_message = rsa.verify(message, signature, public_key)

        # If Legit
        if verify_message == 'SHA-256':

            # Loads Variables and checks if the person has enough coin
            transaction_n = new_transaction['t_n']
            transaction_e = new_transaction['t_e']
            transaction_amount = new_transaction['t_amount']

            # Loads the Ledger
            ledger = getLedger()

            # If they do not have enough coin
            if transaction_amount > ledger[str(public_key.n) + '_LCH']:
                print ('<Not enough coin to send!>')
                return '2'

            # Else
            else:

                # Takes Away the Coin from their name
                ledger[str(public_key.n) + '_LCH'] = ledger[str(public_key.n) + '_LCH'] - transaction_amount

                # Gives the coin to whoever it is being sent too
                ledger[str(transaction_n) + '_LCH'] = ledger[str(transaction_n) + '_LCH'] + transaction_amount

                # Saves it to the ledger
                dumpLedger(ledger)

                print('<Valid Transaction Verified!>')
                return '0'

        # Otherwise
        else:
            print('<Fraudulent Transaction Detected!>')
            return '1'

# Main Function
if __name__ == '__main__':

    # Loads the config file
    config = runConfig()

    # Initializes the Block Dictionary
    block = getBlock()

    # Generates a Public Private Key Pair if one does not exist
    publicPrivateGen(config)

    # Server Config
    web_config = {
        'global': {
            'server.socket_host': config['url'],
            'server.socket_port': config['port']
        }
    }

    # Starts up the cherrypy server
    cherrypy.quickstart(App(), '/', web_config)