import json, requests, hashlib, rsa, pickle, time, base64, os

# Runs and Returns the Config Data
def runConfig():

    # Opens the config File
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

# Checks if you already have a plot
plot_exists = os.path.exists('plot.json')

# If you already have a plot
if plot_exists:
    print('<You already have a plot!>')
else: # If you do not have a plot

    # Variables
    ledger = getLedger()
    public_key = getPublicKey()
    private_key = getPrivateKey()
    config = runConfig()
    message = config['message']

    # If you have enough coin to make a plot
    if ledger[str(public_key.n) + '_LCH'] >= 10:

        # Variables
        url = config['url'] + '/new_plot'

        # Sign a Message for validation
        signed_message = rsa.sign(message.encode(), private_key, 'SHA-256')

        # Makes it a string
        signed_message_str = str(base64.b64encode(signed_message), 'UTF-8')

        # Puts other variables into a Dictionary, then to a string
        new_plot_dic = {
            "signed_message": signed_message_str,
            "message": message,
            "public_key.n": public_key.n,
            "public_key.e": public_key.e
        }
        new_plot_str = json.dumps(new_plot_dic)

        # Wraps it all nicely
        data = {"new_plot_str": new_plot_str}

        # Sends it to a server
        r = requests.post(url, data=data)

        # If you do not have enough coin
        if r.text == '1':
            print('<You do not have enough coin to make a plot!>')
        elif r.text == '2': # If you lied about the signature
            print('<You did not correctly sign the message!>')
        else: # If you were all correct, and have the coin
            print('<Beginning to Till the Plot!>')

            # Initializing Variables
            plot_number = int(r.text)
            plot_start = plot_number - 2500

            # Initializing Dictionary
            plot_dic = {'plot_number': plot_number, 'new_crop': 0}

            # Tills the Plot
            for x in range(2500):
                plot_dic[str(x + plot_start)] = lunchHash(str(x + plot_start))

                # Saves the Info
                with open('plot.json', 'w') as plot_file:
                    json.dump(plot_dic, plot_file)
                    plot_file.close()

                # Sometimes tells you the till progress
                if x % 5 == 0:
                    print('<Tilling Plot! ' + str((x / 2500) * 100) + '% Finished!>')

            print ('<Plot Fully Tilled! You are ready to Farm!>')
    else: # If you do not have enough coin
        print('<You do not have enough coin! Try Updating the Ledger!>')
