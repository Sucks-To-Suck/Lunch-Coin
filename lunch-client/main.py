import json, requests, hashlib, rsa, pickle, time

# Runs and Returns the Config Data
def runConfig():

    # Opens the config File
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
        json_file.close()

    return config

# Updates the Ledger
def syncLedger():

    # Url Needed to Update the Ledger
    url = config['url'] + '/ledger_receive'

    # Receives the ledger file from the server
    data = requests.get(url)

    # Opens and Saves the json file called ledger, overrides previous text if the file exists
    with open('ledger.json', 'w') as json_file:
        loaded_data = json.loads(data.text)

        # Dumps the Data into your copy of the ledger
        json.dump(loaded_data, json_file)

        print('<ledger updated>')

# Checks if there are keys generated, if not then it generates a public private key pair
def publicPrivateGen():

    # If they do not exist
    if config['generated_keys'] == 'false':
        print('<Wallet not Detected! Generating a New One>')

        # Generates the Key Pair
        (public_key, private_key) = rsa.newkeys(1024)

        # Updates the Config
        config['generated_keys'] = 'true'

        # Updates the Config (cont)
        with open('config.json', 'w') as json_file:
            json.dump(config, json_file)
            json_file.close()

        # Saves the Public Key
        with open('public_key.txt', 'wb') as public_key_file:
            pickle.dump(public_key, public_key_file)
            public_key_file.close()

        # Saves the Private Key
        with open('private_key.txt', 'wb') as private_key_file:
            pickle.dump(private_key, private_key_file)
            private_key_file.close()

        # Sends the new wallet info to the server
        addNewWallet()

        print('<Wallet Generated!>')

    # If it exists
    elif config['generated_keys'] == 'true':
        print('<Wallet Detected!>')

    # Otherwise
    else:
        print('<Please put true or false as an option in the config for wallet generation>')

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
    with open('private_key.txt', 'rb') as private_key_file:

        # Loads the computer jumbo in the file into usable object
        private_key = pickle.load(private_key_file)
        private_key_file.close()

        return private_key

# Adds the New Wallet to the Ledger
def addNewWallet():

    # Gets the Public Key
    public_key = getPublicKey()

    # Creates a Dictionary for your Public Key Info
    public_key_dic = {
        'public_key.n': public_key.n,
        'public_key.e': public_key.e
    }

    # Puts the dictionary into a string for sending
    public_key_str = json.dumps(public_key_dic)

    # Defines Stuff for HTTP Posting
    url = config['url'] + '/add_new_wallet'
    data = {'json_str': public_key_str}

    # HTTP Posts the data across
    r = requests.post(url, data=data)

    # If something went wrong
    if r.text != '0':
        print('<Adding the Wallet Failed. Contact Josh for Help!>')

# Runs the Lunch Hash function on the inputted string
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

# Main Function
if __name__ == "__main__":

    # Opens and Runs the Config
    config = runConfig()

    # Runs once at the beginning of the program
    publicPrivateGen()

    # Runs continuously rather than at the beginning of the program once
    while True:

        # Syncs the ledger with the server
        syncLedger()

        time.sleep(10)