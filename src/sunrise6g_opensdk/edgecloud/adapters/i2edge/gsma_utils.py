#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - César Cajas (cesar.cajas@i2cat.net)
##


def map_hugepage(raw_hp: dict) -> dict:
    # Map from {'number': int, 'pageSize': str} to {'count': int, 'size': str}
    return {
        "pageSize": raw_hp.get("pageSize", ""),
        "number": raw_hp.get("number", ""),
    }


def map_compute_resource(raw_cr: dict) -> dict:
    # Map numCPU dict -> int, hugepages list, gpu list, vpu/fpga int to optional int or list
    # Cast cpuExclusivity to bool
    hugepages_raw = raw_cr.get("hugepages") or []
    hugepages = [map_hugepage(hp) for hp in hugepages_raw]

    # numCPU viene {'whole': {'value': int}}
    num_cpu_raw = raw_cr.get("numCPU")
    if isinstance(num_cpu_raw, dict):
        num_cpu = num_cpu_raw.get("whole", {}).get("value", 0)
    else:
        num_cpu = num_cpu_raw if isinstance(num_cpu_raw, int) else 0

    gpu = raw_cr.get("gpu") or None
    vpu = raw_cr.get("vpu")
    if isinstance(vpu, int) and vpu == 0:
        vpu = None

    fpga = raw_cr.get("fpga")
    if isinstance(fpga, int) and fpga == 0:
        fpga = None

    # cpuExclusivity
    cpu_exclusivity = raw_cr.get("cpuExclusivity")
    if isinstance(cpu_exclusivity, int):
        cpu_exclusivity = bool(cpu_exclusivity)

    # dict GSMA
    return {
        "cpuArchType": raw_cr.get("cpuArchType"),
        "numCPU": num_cpu,
        "memory": raw_cr.get("memory"),
        "diskStorage": raw_cr.get("diskStorage"),
        "gpu": gpu if gpu else None,
        "vpu": vpu,
        "fpga": fpga,
        "hugepages": hugepages if hugepages else None,
        "cpuExclusivity": cpu_exclusivity,
    }


def map_ostype(raw_os: dict) -> dict:
    # Simple passthrough
    return {
        "architecture": raw_os.get("architecture"),
        "distribution": raw_os.get("distribution"),
        "version": raw_os.get("version"),
        "license": raw_os.get("license"),
    }


def map_flavour(raw_flavour: dict) -> dict:
    fpga = raw_flavour.get("fpga")
    if isinstance(fpga, int):
        fpga = None if fpga == 0 else [str(fpga)]

    vpu = raw_flavour.get("vpu")
    if isinstance(vpu, int):
        vpu = None if vpu == 0 else [str(vpu)]

    cpu_exclusivity = raw_flavour.get("cpuExclusivity")
    if not isinstance(cpu_exclusivity, list):
        cpu_exclusivity = None

    # Map supportedOSTypes
    supported_os = raw_flavour.get("supportedOSTypes", [])
    supported_ostypes = [map_ostype(os) for os in supported_os]

    return {
        "flavourId": raw_flavour.get("flavourId"),
        "cpuArchType": raw_flavour.get("cpuArchType"),
        "supportedOSTypes": supported_ostypes,
        "numCPU": raw_flavour.get("numCPU"),
        "memorySize": raw_flavour.get("memorySize"),
        "storageSize": raw_flavour.get("storageSize"),
        "gpu": raw_flavour.get("gpu") or None,
        "fpga": fpga,
        "vpu": vpu,
        "hugepages": raw_flavour.get("hugepages") or None,
        "cpuExclusivity": cpu_exclusivity,
    }


def map_network_resources(raw_net: dict) -> dict:
    if not raw_net:
        return None
    return {
        "egressBandWidth": raw_net.get("egressBandWidth", 0),
        "dedicatedNIC": raw_net.get("dedicatedNIC", 0),
        "supportSriov": bool(raw_net.get("supportSriov")),
        "supportDPDK": bool(raw_net.get("supportDPDK")),
    }


def map_zone_service_level(raw_sli: dict) -> dict:
    if not raw_sli:
        return None
    return {
        "latencyRanges": {
            "minLatency": raw_sli.get("latencyRanges", {}).get("minLatency", 1),
            "maxLatency": raw_sli.get("latencyRanges", {}).get("maxLatency", 1),
        },
        "jitterRanges": {
            "minJitter": raw_sli.get("jitterRanges", {}).get("minJitter", 1),
            "maxJitter": raw_sli.get("jitterRanges", {}).get("maxJitter", 1),
        },
        "throughputRanges": {
            "minThroughput": raw_sli.get("throughputRanges", {}).get("minThroughput", 1),
            "maxThroughput": raw_sli.get("throughputRanges", {}).get("maxThroughput", 1),
        },
    }


def map_zone(raw_zone: dict) -> dict:
    reserved_compute = raw_zone.get("reservedComputeResources")
    if not reserved_compute or len(reserved_compute) == 0:
        reserved_compute = [
            {
                "cpuArchType": "ISA_X86_64",
                "numCPU": 0,
                "memory": 0,
                "diskStorage": 0,
                "gpu": None,
                "vpu": None,
                "fpga": None,
                "hugepages": None,
                "cpuExclusivity": False,
            }
        ]

    return {
        "zoneId": raw_zone.get("zoneId"),
        "reservedComputeResources": [map_compute_resource(cr) for cr in reserved_compute],
        "computeResourceQuotaLimits": [
            map_compute_resource(cr) for cr in raw_zone.get("computeResourceQuotaLimits", [])
        ],
        "flavoursSupported": [map_flavour(fl) for fl in raw_zone.get("flavoursSupported", [])],
        "networkResources": map_network_resources(raw_zone.get("networkResources")),
        "zoneServiceLevelObjsInfo": map_zone_service_level(
            raw_zone.get("zoneServiceLevelObjsInfo")
        ),
    }
