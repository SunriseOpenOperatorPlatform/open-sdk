from sunrise6g_opensdk import Sdk as sdkclient


def main():
    # The module that imports the SDK package, must specify which adapters will be used:
    client_specs = {
        "edgecloud": {
            "client_name": "i2edge",
            "base_url": "http://IP:PORT",
        },
        "network": {
            "client_name": "open5gs",
            "base_url": "http://IP:PORT",
            "scs_as_id": "id_example",
        },
    }

    clients = sdkclient.create_clients_from(client_specs)
    edgecloud_client = clients.get("edgecloud")
    network_client = clients.get("network")

    print("EdgeCloud client ready to be used:", edgecloud_client)
    print("Network client ready to be used:", network_client)

    # Examples:
    # EdgeCloud
    # print("Testing edgecloud client function: get_edge_cloud_zones:")
    # zones = edgecloud_client.get_edge_cloud_zones()
    # print(zones)

    # Network
    # print("Testing network client function: EXAMPLE_FUNCTION:")
    # network_client.get_qod_session(session_id="example_session_id")


if __name__ == "__main__":
    main()
