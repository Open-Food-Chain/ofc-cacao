# Import necessary modules
import re
import json
import binascii
import hashlib
from datetime import datetime
from object_parser import ObjectParser

# ObjectParser class definition goes here
# [Paste the ObjectParser class code here]

def main():
    # Create an instance of ObjectParser
    obj_parser = ObjectParser()

    true = True

    # Define a test object with various data types
    test_object = {"DNI":{"double_hash":true,"value":"A98OGTX79A"},"costSales":{"clear_text":true,"value":"6okai15tah"},"productId":{"clear_text":true,"value":"mpqhgaub79"},"quantity":{"clear_text":true,"value":96},"salesDate":{"clear_text":true,"value":"inedvbh938"},"transactionDate":{"clear_text":true,"value":"noo7ycfgqz"},"unique_value":{"unique":true,"value":"A98OGTX79A"},"unit":{"clear_text":true,"value":"jmqdg2gql5"},"userType":{"clear_text":true,"value":"jiy6yd95tg"}}

    # Call the parse_obj method with the test object
    response = obj_parser.preprocess_save(test_object)

    # Print the response
    print("Response from parse_obj:")
    print(json.dumps(response, indent=4))


# Run the main function
if __name__ == "__main__":
    main()
