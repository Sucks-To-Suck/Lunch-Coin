import cherrypy, rsa, pickle, json, hashlib, base64, time

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

    # If someone makes a new plot
    @cherrypy.expose
    def new_plot(self, new_plot_str):

        # Loads the Plot info
        new_plot_dic = json.loads(new_plot_str)

        # Initializes Variables
        public_key = getPublicKey()
        public_key.n = new_plot_dic['public_key.n']
        public_key.e = new_plot_dic['public_key.e']
        message = new_plot_dic['message']

        # Initializes more Variables
        base64_signed_message = bytes(new_plot_dic['signed_message'], 'utf-8')
        signed_message = base64.b64decode(base64_signed_message)

        # Verifies the request to make a plot
        verify_sign = rsa.verify(message.encode(), signed_message, public_key)

        # If Good
        if verify_sign == 'SHA-256':
            ledger = getLedger()

            # If they have enough coin
            if ledger[str(public_key.n) + '_LCH'] >= 10:

                ledger[str(public_key.n) + '_LCH'] = ledger[str(public_key.n) + '_LCH'] - 10
                ledger['__burn___LCH'] = ledger['__burn___LCH'] + 10
                dumpLedger(ledger)

                with open('plots.json', 'r') as plots_file_read:
                    plots_dic = json.load(plots_file_read)
                    plots_file_read.close()

                plots_dic['plot_max_crops'] = plots_dic['plot_max_crops'] + 2500

                with open('plots.json', 'w') as plot_file_write:
                    plots_dic[str(public_key.n)] = plots_dic['plot_max_crops']
                    json.dump(plots_dic ,plot_file_write)
                    plot_file_write.close()

                return str(plots_dic['plot_max_crops'])
            else: # If they do not have enough coin
                return '1'
        else: # If they did not sign properly
            return '2'

    # Updates and sends out the winning crop number
    @cherrypy.expose
    def check_harvest(self):

        # Opens the Plots JSON
        with open('plots.json', 'r') as plot_file:
            plot = json.load(plot_file)
            plot_file.close()

        # If it needs to be updated
        if plot['new_crop_time'] + 10 < time.time():
            plot['new_crop'] = time.time() % plot['plot_max_crops']
            plot['crop_awarded'] = 0
            plot['new_crop_time'] = time.time()

            # Opens the Plots JSON for writting
            with open('plots.json', 'w') as plot_file_write:
                json.dump(plot, plot_file_write)
                plot_file_write.close()

            return '1'
        else: # If same winning crop still valid
            return str(plot['new_crop'])

    # Checks whether someone wins the crop or not
    @cherrypy.expose
    def submit_harvest(self, sent_data, public_key_str):

        # Opens the Plots JSON for reading
        with open('plots.json', 'r') as plot_file:
            plot = json.load(plot_file)
            plot_file.close()

        # Loads the data that was sent over
        sent_plot = json.loads(sent_data)
        sent_public_key = json.loads(public_key_str)

        # Initializes the Public Key
        public_key = getPublicKey()
        public_key.n = sent_public_key['public_key.n']
        public_key.e = sent_public_key['public_key.e']

        # If the person is right and has not won
        if sent_plot['new_crop'] == plot['new_crop'] and plot['crop_awarded'] == 0:
            # If the winner claiming the prize is legit
            if (plot[str(public_key.n)] - 2500) <= plot['new_crop'] < plot[str(public_key.n)]:

                # Initializes the Ledger
                ledger = getLedger()

                # Pays the Reward
                ledger[str(public_key.n) + '_LCH'] = ledger[str(public_key.n) + '_LCH'] + 0.01

                # Saves the Ledger
                dumpLedger(ledger)

                # Stops them from winning with the same crop this go round
                plot['crop_awarded'] = 1

                # Saves that to the plto file
                with open('plots.json', 'w') as plot_file_write:
                    json.dump(plot, plot_file_write)
                    plot_file_write.close()

                print('<Someone Successfully Harvested!>')

                return '0'
            else: # If they won before, but have to wait until it updates
                print('<Someone is Trying to Harvest the same Crop!>')
        else: # Submitted the wrong Crop
            print('<Someone Failed the Harvest Submit!>')

# Main Function
if __name__ == '__main__':

    # Loads the config file
    config = runConfig()

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