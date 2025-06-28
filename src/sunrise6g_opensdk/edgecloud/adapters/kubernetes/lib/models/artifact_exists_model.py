from __future__ import absolute_import

from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib import util
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.base_model_ import Model


class ArtifactExistsModel(Model):

    def __init__(
        self,
        registry_url: str = None,
        artefact_name: str = None,
        artefact_tag: str = None,
        username: str = None,
        password: str = None,
    ):

        self.swagger_types = {
            "registry_url": str,
            "artefact_name": str,
            "artefact_tag": str,
            "username": str,
            "password": str,
        }

        self.attribute_map = {
            "registry_url": "registry_url",
            "artefact_name": "artefact_name",
            "artefact_tag": "artefact_tag",
            "username": "username",
            "password": "password",
        }
        self._registry_url = registry_url
        self._artefact_name = artefact_name
        self._artefact_tag = artefact_tag
        self._username = username
        self._password = password

    @classmethod
    def from_dict(cls, dikt) -> "ArtifactExistsModel":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CopyArtifactModel.  # noqa: E501
        :rtype: CopyArtifactModel
        """
        return util.deserialize_model(dikt, cls)

    @classmethod
    def to_dict(self) -> dict:
        dict_object = {}
        if self.registry_url is not None:
            dict_object["registry_url"] = self.registry_url
        if self.artefact_name is not None:
            dict_object["artefact_name"] = self.artefact_name
        if self.artefact_tag is not None:
            dict_object["artefact_tag"] = self.artefact_tag
        if self.username is not None:
            dict_object["username"] = self.username
        if self.password is not None:
            dict_object["password"] = self.password
        return dict_object

    @property
    def registry_url(self) -> str:
        """Gets the registry_url of this ArtifactExistsModel.

        :return: The registry_url of this ArtifactExistsModel.
        :rtype: str
        """
        return self._registry_url

    @registry_url.setter
    def registry_url(self, registry_url: str):
        """Sets the registry_url of this ArtifactExistsModel.

        :param name: The registry_url of this ArtifactExistsModel.
        :type name: str
        """

        self._registry_url = registry_url

    @property
    def artefact_name(self) -> str:
        """Gets the artefact_name of this ArtifactExistsModel.

        :return: The artefact_name of this ArtifactExistsModel.
        :rtype: str
        """
        return self._artefact_name

    @artefact_name.setter
    def artefact_name(self, artefact_name: str):
        """Sets the artefact_name of this ArtifactExistsModel.

        :param name: The artefact_name of this ArtifactExistsModel.
        :type name: str
        """

        self._artefact_name = artefact_name

    @property
    def artefact_tag(self) -> str:
        """Gets the artefact_tag of this ArtifactExistsModel.

        :return: The artefact_tag of this ArtifactExistsModel.
        :rtype: str
        """
        return self._artefact_tag

    @artefact_tag.setter
    def artefact_tag(self, artefact_tag: str):
        """Sets the artefact_tag of this ArtifactExistsModel.

        :param name: The artefact_tag of this ArtifactExistsModel.
        :type name: str
        """

        self._artefact_tag = artefact_tag

    @property
    def username(self) -> str:
        """Gets the username of this ArtifactExistsModel.

        :return: The username of this ArtifactExistsModel.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username: str):
        """Sets the username of this ArtifactExistsModel.

        :param name: The username of this ArtifactExistsModel.
        :type name: str
        """

        self._username = username

    @property
    def password(self) -> str:
        """Gets the password of this ArtifactExistsModel.

        :return: The password of this ArtifactExistsModel.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password: str):
        """Sets the password of this ArtifactExistsModel.

        :param name: The password of this ArtifactExistsModel.
        :type name: str
        """

        self._password = password
