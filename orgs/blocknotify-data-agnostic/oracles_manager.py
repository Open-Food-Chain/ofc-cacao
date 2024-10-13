import json
import time

import os
from dotenv import load_dotenv

load_dotenv()

collections = os.getenv('COLLECTIONS').split(',')  # Assuming 'collections' is a comma-separated list

class OraclesManager:
    def __init__(self, wallet_Interface, org_name):
        self.min_funds = 6

        self.wallet = wallet_Interface
        self.org_name = org_name
        self.addresses = {}
        self.org_oracle_name = "OO_" + self.org_name
        

        self.ab_oracle_name = []
        self.ab_oracle = {}

        self.addr_book_prefix = "AB_"

        for collection in collections:
            name = self.addr_book_prefix + collection + "_" + self.org_name
            self.ab_oracle_name.append(name)

        self.org_oracle = self.find_oracle_txid(self.org_oracle_name)
        if self.org_oracle == None:
            print("create org oracle triggered")
            self.create_org_oracle()

        self.wait_until_org_oracle_has_funds()

        for name in self.ab_oracle_name:
            self.ab_oracle[name] = self.search_this_org_oracles(name)
            if self.ab_oracle[name] == None:
                print("create orderbook oracle triggered")
                self.ab_oracle[name] = self.create_address_book_oracle(name)
            self.wait_until_oracle_has_funds(self.ab_oracle[name])

        print("FINISHED")


    def create_org_oracle( self ):
        ret = self.wallet.create_string_oracle(self.org_oracle_name, "This oracle will have a list of all oracles used by this organization")
        self.org_oracle = ret
        return ret

    def find_oracle_txid( self, name ):
        oracle_list = self.wallet.get_oracle_list()

        for oracle in oracle_list:
            info = self.wallet.get_oracle_info(oracle)
            if info['name'] == name:
                return info['txid']

        return None

    def subscribe_to_org_oracle( self ):
        return self.wallet.subscribe_to_oracle(self.org_oracle, "1")

    def publish_to_addressbook_oracle( self, collection, dic ):
        name = self.addr_book_prefix + collection + "_" + self.org_name

        oracle_txid = self.search_this_org_oracles(name)

        string = json.dumps(dic)

        return self.wallet.publish_data_string_to_oracle(oracle_txid, string)

    def publish_to_org_oracle( self, new_oracle_name, new_oracle_txid ):
        dic = {}

        dic[new_oracle_name] = new_oracle_txid 

        string = json.dumps(dic)

        return self.wallet.publish_data_string_to_oracle(self.org_oracle, string)

    def create_address_book_oracle( self, name ):
        description = "This oracle will have a list all the fields and their addresses for collection " + name 
        ret = self.wallet.create_string_oracle(name, description)
        #self.ab_oracle = ret

        self.publish_to_org_oracle(name, ret)

        return ret

    def publish_to_oracle_json( self, oracle_txid, key, value ):
        dic = {}

        dic[key] = value 

        string = json.dumps(dic)


        return self.wallet.publish_data_string_to_oracle(oracle_txid, string)

    def publish_json_to_oracle( self, oracle_txid, dic):
        
        string = json.dumps(dic)

        return self.wallet.publish_data_string_to_oracle(oracle_txid, string)


    def wait_until_org_oracle_has_funds( self ):
        funds = 0

        while funds < self.min_funds:
            ret = self.wallet.get_oracle_info(self.org_oracle)

            print(ret)
            if len(ret['registered']) > 0:
                funds = float(ret['registered'][0]['funds'])
                funds = int(funds)
                print(funds)
                if funds < self.min_funds:
                    time.sleep(30)
                    self.subscribe_to_org_oracle()
            else:
                self.wallet.recreate_oracle_from_fund(self.org_oracle) ## we need to recreate

    def fund_oracle( self, oracle_txid ):
        funds = 0

        while funds < self.min_funds:
            ret = self.wallet.get_oracle_info(oracle_txid)
            if len(ret['registered']) > 0:
                funds = float(ret['registered'][0]['funds'])
                funds = int(funds)
                print(funds)
                if funds < self.min_funds:
                    time.sleep(30)
                    self.wallet.subscribe_to_oracle(oracle_txid, "1")
            else:
                self.wallet.recreate_oracle_from_fund(oracle_txid) ## we need to recreate

    def wait_until_oracle_has_funds( self, oracle_txid ):
        funds = 0

        while funds < self.min_funds:
            ret = self.wallet.get_oracle_info(oracle_txid)
            if len(ret['registered']) > 0:
                funds = float(ret['registered'][0]['funds'])
                funds = int(funds)
                print(funds)
                if funds < self.min_funds:
                    time.sleep(30)
                    self.fund_oracle(oracle_txid)
            else:
                self.wallet.recreate_oracle_from_fund(oracle_txid) ## we need to recreate

    def search_this_org_oracles( self, name ):
        oracles_of_this_org = self.wallet.get_oracle_data(self.org_oracle)['samples']

        print("CHECK SAMPLES")
        print(oracles_of_this_org)
        print(type(oracles_of_this_org))

        for oracle in oracles_of_this_org:
            #print(oracle)
            try:
                #print(oracle['data'][0])
                data = json.loads(oracle['data'][0])

                print(name)

                if name in data:
                    return data[name]

            except BaseException:
                pass

    def get_this_org_collection_addressbook( self, collection ):
        name = self.addr_book_prefix + collection + "_" + self.org_name

        org_txid = self.search_this_org_oracles(name)

        return org_txid

    def search_oracles_json( self, name, oracle_txid ):
        samples = self.wallet.get_oracle_data(oracle_txid)['samples']


        for sample in samples:
            #print(oracle)
            try:
                #print(oracle['data'][0])
                data = json.loads(sample['data'][0])
                if name in data:
                    return data[name]

            except BaseException:
                pass

        return None

    def get_oracles_json( self, oracle_txid ):
        samples = self.wallet.get_oracle_last_data(oracle_txid)['samples']

        print("samples")
        print(samples)

        for sample in samples:
            #print(oracle)
            try:
                #print(oracle['data'][0])
                data = json.loads(sample['data'][0])

                return data

            except BaseException:
                pass

        return None

    def check_and_update_address_book( self, field_names, key_addr, collection):

        print("the json: ")
        print(key_addr)

        name = self.addr_book_prefix + collection + "_" + self.org_name

        address_book_txid = self.search_this_org_oracles(name)

        print("addy book tx id")
        print(address_book_txid)

        stored_value = self.get_oracles_json( address_book_txid )

        if stored_value == None:
            ret = self.publish_json_to_oracle(address_book_txid, key_addr)
            return "stored: " + key_addr

        print(field_names)

        for key in field_names:
            if key not in key_addr:
                print("exec1")
                return "error: " + str(key_addr)
            
            if key not in stored_value:
                print("exec2")
                ret = self.publish_json_to_oracle(address_book_txid, key_addr)
                print("return: ")
                print(ret)
                return "stored: " + str(key_addr)

            if stored_value[key] != key_addr[key]:
                print("exec3")
                ret = self.publish_json_to_oracle(address_book_txid, key_addr)
                print("return: ")
                print(ret)
                return "stored: " + str(key_addr)

        return None

    def check_and_update_address_book_field( self, field, address, collection):
        name = self.addr_book_prefix + collection + "_" + self.org_name

        address_book_txid = self.search_this_org_oracles(name)

        stored_value = self.search_oracles_json( field, address_book_txid)

        if stored_value == None:
            self.publish_to_oracle_json(address_book_txid, field, address)
            return "stored: " + field + " with value: " + address

        if stored_value != address:
            self.publish_to_oracle_json(address_book_txid, field, address)
            return "stored: " + field + " with value: " + address    

        return None