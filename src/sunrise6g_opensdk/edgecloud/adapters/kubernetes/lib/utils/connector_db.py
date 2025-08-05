from typing import List

import pymongo

storage_url = None


class ConnectorDB:
    def __init__(self, host):
        self._storage_url = host
        self.mydb_mongo = "pi-edge"

    # def insert_document_k8s_platform(self, document=None, _id=None):
    #     collection = "kubernetes_platforms"
    #     myclient = pymongo.MongoClient(self._storage_url)
    #     mydbmongo = myclient[self.mydb_mongo]
    #     mycol = mydbmongo[collection]

    #     myquery = {"name": document["kubernetes_platform_name"]}
    #     mydoc = mycol.find_one(myquery)
    #     # keeps the last record (contains registrationStatus)
    #     if mydoc is not None:
    #         raise Exception(
    #             "Already Registered: Platform name",
    #             document["kubernetes_platform_name"],
    #         )
    #     try:
    #         insert_doc = {}
    #         insert_doc["name"] = document["kubernetes_platform_name"]
    #         insert_doc["auth_credentials"] = document["kubernetes_auth_credentials"]
    #         mycol.insert_one(insert_doc)
    #     except Exception as ce_:
    #         raise Exception("An exception occurred :", ce_)

    # def delete_document_k8s_platform(self, document=None, _id=None):
    #     collection = "kubernetes_platforms"
    #     myclient = pymongo.MongoClient(self._storage_url)
    #     mydbmongo = myclient[self.mydb_mongo]
    #     mycol = mydbmongo[collection]

    #     myquery = {"name": document["kubernetes_platform_name"]}
    #     mydoc = mycol.find_one(myquery)

    #     # keeps the last record (contains registrationStatus)
    #     if mydoc is None:
    #         raise Exception(
    #             "Not found: Platform name", document["kubernetes_platform_name"]
    #         )
    #     try:
    #         delete_doc = {}
    #         delete_doc["name"] = document["kubernetes_platform_name"]
    #         mycol.delete_one(delete_doc)
    #     except Exception as ce_:
    #         raise Exception("An exception occurred :", ce_)

    def insert_document_deployed_service_function(self, document=None, _id=None):

        collection = "deployed_service_functions"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        myquery = {
            "name": document["service_function_name"],
            "location": document["location"],
            "instance_name": document["instance_name"],
        }
        mydoc = mycol.find_one(myquery)
        # keeps the last record (contains registrationStatus)
        if mydoc is not None:
            return "Requested service function (with this name) already deployed and exists in deployed_apps database"
        # raise Exception("Already Registered: PaaS name", document["paas_name"])
        try:
            insert_doc = {}
            insert_doc["_id"] = document["_id"]
            insert_doc["name"] = document["service_function_name"]
            # insert_doc["type"] = document["paas_type"]
            insert_doc["location"] = document["location"]
            insert_doc["instance_name"] = document["instance_name"]

            if "scaling_type" in document:
                insert_doc["scaling_type"] = document["scaling_type"]
            #
            if "monitoring_service_URL" in document:
                insert_doc["monitoring_service_URL"] = document["monitoring_service_URL"]

            if "paas_name" in document:
                insert_doc["paas_name"] = document["paas_name"]

            # TODO: IS IT NEEDED?
            # if "volumes" in document:
            #     insert_doc["volumes"] = document["volumes"]

            # if "env_parameters" in document:
            #     insert_doc["env_parameters"] = document["env_parameters"]

            mycol.insert_one(insert_doc)
            return "Deployed service function registered successfully"
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)

    def delete_document_deployed_service_functions(self, document=None, _id=None):
        collection = "deployed_service_functions"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        myquery = {"instance_name": document["instance_name"]}
        mydoc = mycol.find_one(myquery)

        # keeps the last record (contains registrationStatus)
        if mydoc is None:
            return "Deployed Service function not found in the database"
            # raise Exception("Not found: PaaS name", document["paas_name"])
        try:
            delete_doc = {}
            delete_doc["instance_name"] = document["instance_name"]
            mycol.delete_one(delete_doc)
            return "Deployed Service function deleted successfully"
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)

    def insert_document_service_function(self, document=None, _id=None):
        # print(document)
        collection = "service_functions"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        myquery = {"name": document["service_function_name"]}
        mydoc = mycol.find_one(myquery)

        if mydoc is not None:
            return "Service function already exists in the catalogue"

        insert_doc = {}
        insert_doc["_id"] = document["service_function_id"]
        insert_doc["name"] = document["service_function_name"]
        insert_doc["type"] = document["service_function_type"]
        insert_doc["image"] = document["service_function_image"]
        insert_doc["app_provider"] = document["app_provider"]
        insert_doc["required_resources"] = document["required_resources"]
        insert_doc["version"] = document.get("version")
        if document.get("application_ports") is not None:
            insert_doc["application_ports"] = document.get("application_ports")
        if document.get("autoscaling_policies") is not None:
            insert_doc["autoscaling_policies"] = document.get("autoscaling_policies")
        # if "required_volumes" in document:
        #     insert_doc["required_volumes"] = document["required_volumes"]
        # if "privileged" in document:
        #     insert_doc["privileged"] = document["privileged"]
        # insert_doc["required_env_parameters"] = document["required_env_parameters"]
        result = mycol.insert_one(insert_doc)
        return result

    # ##TODO!!!!!
    # def update_document_service_function(document=None, _id=None):

    #     collection = "service_functions"
    #     myclient = pymongo.MongoClient(storage_url)
    #     mydbmongo = myclient[mydb_mongo]
    #     mycol = mydbmongo[collection]

    #     myquery = {"name": document["service_function_name"]}
    #     mydoc = mycol.find_one(myquery)

    #     if mydoc is not None:

    #         try:
    #             myquery = {"name": document["service_function_name"]}
    #             newvalues = {"$set": {"autoscaling_policies": document["autoscaling_policies"]}}
    #             mycol.update_one(myquery,newvalues)
    #             return "Service function updated successfully"
    #         except Exception as ce_:
    #             raise Exception("An exception occurred :", ce_)
    #     else:
    #         return "Service function not found in the catalogue"

    def delete_document_service_function(self, service_function_input_name=None, _id: str = None):

        # _id = ObjectId(_id)
        collection = "service_functions"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        myquery = {"_id": _id}
        print(myquery)
        mydoc = mycol.find_one(myquery)

        if mydoc is None:
            return "Service function not found in the database", 404
        try:
            delete_doc = {}
            delete_doc["_id"] = _id
            mycol.delete_one(delete_doc)
            return "Service function deregistered successfully", 200
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)

    def delete_document_paas_service(self, paas_service_input_name=None, _id=None):
        collection = "paas_services"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]
        myquery = {"name": paas_service_input_name}
        mydoc = mycol.find_one(myquery)

        if mydoc is None:
            return "PaaS Service not found in the database"
        try:
            delete_doc = {}
            delete_doc["name"] = paas_service_input_name
            mycol.delete_one(delete_doc)
            return "PaaS Service deregistered successfully"
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)

    def delete_document_deployed_paas_service(self, document=None, _id=None):
        collection = "deployed_paas_services"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        myquery = {"instance_name": document["instance_name"]}
        mydoc = mycol.find_one(myquery)

        if mydoc is None:
            return "Deployed PaaS service not found in the database"
        try:
            delete_doc = {}
            delete_doc["instance_name"] = document["instance_name"]
            mycol.delete_one(delete_doc)
            return "Deployed PaaS Service deleted successfully"
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)

    def insert_document_nodes(self, document=None, _id=None):
        collection = "points_of_presence"
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        myquery = {"name": document["name"]}
        mydoc = mycol.find_one(myquery)
        # keeps the last record (contains registrationStatus)
        if mydoc is not None:
            return ("Already Registered: Node name", document["name"])
        try:
            mycol.insert_one(document)
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)

    def get_documents_from_collection(
        self, collection_input, input_type=None, input_value=None
    ) -> List[dict]:
        collection = collection_input
        myclient = pymongo.MongoClient(self._storage_url)
        mydbmongo = myclient[self.mydb_mongo]
        mycol = mydbmongo[collection]

        try:
            mydoc_ = []
            for x in mycol.find():
                x["_id"] = str(x["_id"])
                if input_type is not None:
                    if input_value == x[input_type]:
                        mydoc_.append(x)
                        break
                else:
                    mydoc_.append(x)

            return mydoc_
        except Exception as ce_:
            raise Exception("An exception occurred :", ce_)
