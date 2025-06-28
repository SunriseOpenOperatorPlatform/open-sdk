from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib import util
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.base_model_ import Model


class HelmInstall(Model):
    def __init__(
        self,
        uri: str,
        deployment_name: str,
        repo_username: str = None,
        repo_password: str = None,
    ):  # noqa: E501
        """HelmInstallModel - a model defined in Swagger

        :param name: The name of this HelmInstall.  # noqa: E501
        :type name: str
        :param hostname: The hostname of this HelmInstall.  # noqa: E501
        :type hostname: str
        :param ip: The ip of this HelmInstall.  # noqa: E501
        :type ip: str
        :param password: The password of this HelmInstall.  # noqa: E501
        :type password: str
        """
        self.swagger_types = {
            "uri": str,
            "deployment_name": str,
            "repo_username": str,
            "repo_password": str,
        }

        self.attribute_map = {
            "uri": "uri",
            "deployment_name": "deployment_name",
            "repo_username": "repo_username",
            "repo_password": "repo_password",
        }
        self._uri = uri
        self._deployment_name = deployment_name
        self._repo_password = repo_password
        self._repo_username = repo_username

    @classmethod
    def from_dict(cls, dikt) -> "HelmInstall":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The addNode of this AddNode.  # noqa: E501
        :rtype: AddNode
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uri(self) -> str:
        """Gets the uri of a HelmInstallModel


        :return: The uri of this HelmInstallModel.
        :rtype: str
        """
        return self._uri

    @uri.setter
    def uri(self, uri: str):
        """Sets the name of this HelmInstallModel.


        :param name: The name of this HelmInstallModel.
        :type name: str
        """

        self._uri = uri

    @property
    def deployment_name(self) -> str:
        """Gets the deployment_name of this HelmInstallModel.


        :return: The deployment_name of this HelmInstallModel.
        :rtype: str
        """
        return self._deployment_name

    @deployment_name.setter
    def deployment_name(self, deployment_name: str):
        """Sets the hostname of this HelmInstallModel.


        :param hostname: The hostname of this HelmInstallModel.
        :type hostname: str
        """

        self._deployment_name = deployment_name

    @property
    def repo_username(self) -> str:
        """Gets the repo_username of this HelmInstallModel.


        :return: The repo_username of this HelmInstallModel.
        :rtype: str
        """
        return self._repo_username

    @repo_username.setter
    def repo_username(self, repo_username: str):
        """Sets the repo_username of this HelmInstallModel.


        :param repo_username: The repo_username of this HelmInstallModel.
        :type repo_username: str
        """

        self._repo_username = repo_username

    @property
    def repo_password(self) -> str:
        """Gets the repo_username of this HelmInstallModel.


        :return: The repo_username of this HelmInstallModel.
        :rtype: str
        """
        return self._repo_password

    @repo_password.setter
    def repo_password(self, repo_password: str):
        """Sets the repo_password of this HelmInstallModel.


        :param repo_password: The repo_password of this HelmInstallModel.
        :type repo_password: str
        """

        self._repo_password = repo_password
