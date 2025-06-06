# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from src.edgecloud.clients.piedge.lib.models.base_model_ import Model
from src.edgecloud.clients.piedge.lib import util


class UpdateNode():
    def __init__(self, name: str=None, hostname: str=None, ip: str=None, password: str=None, location: str=None):  # noqa: E501
        """UpdateNode - a model defined in Swagger

        :param name: The new name of the Node.  # noqa: E501
        :type name: str
        :param hostname: The new hostname of the Node.  # noqa: E501
        :type hostname: str
        :param ip: The new ip of the Node.  # noqa: E501
        :type ip: str
        :param password: The new password of the Node.  # noqa: E501
        :type password: str
        :param location: The new location of the Node.  # noqa: E501
        :type location: str
        """
        self.swagger_types = {
            'name': str,
            'hostname': str,
            'ip': str,
            'password': str,
            'location': str
        }

        self.attribute_map = {
            'name': 'name',
            'hostname': 'hostname',
            'ip': 'ip',
            'password': 'password',
            'location': 'location'
        }
        self._name = name
        self._hostname = hostname
        self._ip = ip
        self._password = password
        self._location = location

    @classmethod
    def from_dict(cls, dikt) -> 'UpdateNode':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The addNode of this AddNode.  # noqa: E501
        :rtype: AddNode
        """
        return util.deserialize_model(dikt, cls)
    
    @property
    def name(self) -> str:
        """Gets the name of this Node.


        :return: The name of this Node.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Node.


        :param name: The name of this Node.
        :type name: str
        """

        self._name = name

    @property
    def hostname(self) -> str:
        """Gets the hostname of this Node.


        :return: The hostname of this Node.
        :rtype: str
        """
        return self._hostname

    @hostname.setter
    def hostname(self, hostname: str):
        """Sets the hostname of this Node.


        :param hostname: The hostname of this Node.
        :type hostname: str
        """

        self._hostname = hostname

    @property
    def ip(self) -> str:
        """Gets the ip of this Node.


        :return: The ip of this Node.
        :rtype: str
        """
        return self._ip

    @ip.setter
    def ip(self, ip: str):
        """Sets the ip of this Node.


        :param ip: The ip of this Node.
        :type ip: str
        """

        self._ip = ip


    @property
    def password(self) -> str:
        """Gets the password of this Node.


        :return: The password of this Node.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password: str):
        """Sets the password of this Node.


        :param password: The password of this Node.
        :type password: str
        """

        self._password = password

    @property
    def location(self) -> str:
        """Gets the location of this Node.


        :return: The location of this Node.
        :rtype: str
        """
        return self._location

    @location.setter
    def location(self, location: str):
        """Sets the location of this Node.


        :param location: The location of this Node.
        :type location: str
        """

        self._location = location 