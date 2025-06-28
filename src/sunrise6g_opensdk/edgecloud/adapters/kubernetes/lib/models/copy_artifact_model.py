from __future__ import absolute_import

from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib import util
from sunrise6g_opensdk.edgecloud.adapters.kubernetes.lib.models.base_model_ import Model


class CopyArtifactModel(Model):

    def __init__(
        self,
        src_registry: str,
        src_image_name: str,
        src_image_tag: str,
        dst_registry: str,
        dst_image_name: str = None,
        dst_image_tag: str = None,
        src_username: str = None,
        src_password: str = None,
        dst_username: str = None,
        dst_password: str = None,
    ):

        self.swagger_types = {
            "src_registry": str,
            "src_image_name": str,
            "src_image_tag": str,
            "dst_registry": str,
            "dst_image_name": str,
            "dst_image_tag": str,
            "src_username": str,
            "src_password": str,
            "dst_username": str,
            "dst_password": str,
        }

        self.attribute_map = {
            "src_registry": "src_registry",
            "src_image_name": "src_image_name",
            "src_image_tag": "src_image_tag",
            "dst_registry": "dst_registry",
            "dst_image_name": "dst_image_name",
            "dst_image_tag": "dst_image_tag",
            "src_username": "src_username",
            "src_password": "src_password",
            "dst_username": "dst_username",
            "dst_password": "dst_password",
        }
        self._src_registry = src_registry
        self._src_image_name = src_image_name
        self._src_image_tag = src_image_tag
        self._dst_registry = dst_registry
        self._dst_image_name = dst_image_name
        self._dst_image_tag = dst_image_tag
        self._src_username = src_username
        self._src_password = src_password
        self._dst_username = dst_username
        self._dst_password = dst_password

    @classmethod
    def from_dict(cls, dikt) -> "CopyArtifactModel":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CopyArtifactModel.  # noqa: E501
        :rtype: CopyArtifactModel
        """
        return util.deserialize_model(dikt, cls)

    @property
    def src_registry(self) -> str:
        """Gets the src_registry of this CopyArtifactModel.

        :return: The src_registry of this CopyArtifactModel.
        :rtype: str
        """
        return self._src_registry

    @src_registry.setter
    def src_registry(self, src_registry: str):
        """Sets the src_registry of this CopyArtifactModel.

        :param name: The src_registry of this CopyArtifactModel.
        :type name: str
        """

        self._src_registry = src_registry

    @property
    def src_image_name(self) -> str:
        """Gets the _src_image_name of this CopyArtifactModel.

        :return: The _src_image_name of this CopyArtifactModel.
        :rtype: str
        """
        return self._src_image_name

    @src_image_name.setter
    def src_image_name(self, src_image_name: str):
        """Sets the src_image_name of this CopyArtifactModel.

        :param name: The src_image_name of this CopyArtifactModel.
        :type name: str
        """

        self._src_image_name = src_image_name

    @property
    def src_image_tag(self) -> str:
        """Gets the src_image_tag of this CopyArtifactModel.

        :return: The src_image_tag of this CopyArtifactModel.
        :rtype: str
        """
        return self._src_image_tag

    @src_image_tag.setter
    def src_image_tag(self, src_image_tag: str):
        """Sets the src_image_tag of this CopyArtifactModel.

        :param name: The src_image_tag of this CopyArtifactModel.
        :type name: str
        """

        self._src_image_tag = src_image_tag

    @property
    def dst_registry(self) -> str:
        """Gets the dst_registry of this CopyArtifactModel.

        :return: The dst_registry of this CopyArtifactModel.
        :rtype: str
        """
        return self._dst_registry

    @dst_registry.setter
    def dst_registry(self, dst_registry: str):
        """Sets the dst_registry of this CopyArtifactModel.

        :param name: The dst_registry of this CopyArtifactModel.
        :type name: str
        """

        self._dst_registry = dst_registry

    @property
    def dst_image_name(self) -> str:
        """Gets the dst_image_name of this CopyArtifactModel.

        :return: The dst_image_name of this CopyArtifactModel.
        :rtype: str
        """
        return self._dst_image_name

    @dst_image_name.setter
    def dst_image_name(self, dst_image_name: str):
        """Sets the dst_image_name of this CopyArtifactModel.

        :param name: The dst_image_name of this CopyArtifactModel.
        :type name: str
        """

        self._dst_image_name = dst_image_name

    @property
    def dst_image_tag(self) -> str:
        """Gets the dst_image_tag of this CopyArtifactModel.

        :return: The dst_image_tag of this CopyArtifactModel.
        :rtype: str
        """
        return self._dst_image_tag

    @dst_image_tag.setter
    def dst_image_tag(self, dst_image_tag: str):
        """Sets the dst_image_tag of this CopyArtifactModel.

        :param name: The dst_image_tag of this CopyArtifactModel.
        :type name: str
        """

        self._dst_image_tag = dst_image_tag

    @property
    def src_username(self) -> str:
        """Gets the src_username of this CopyArtifactModel.

        :return: The src_username of this CopyArtifactModel.
        :rtype: str
        """
        return self._src_username

    @src_username.setter
    def src_username(self, src_username: str):
        """Sets the src_username of this CopyArtifactModel.

        :param name: The src_username of this CopyArtifactModel.
        :type name: str
        """

        self._src_username = src_username

    @property
    def src_password(self) -> str:
        """Gets the src_password of this CopyArtifactModel.

        :return: The src_password of this CopyArtifactModel.
        :rtype: str
        """
        return self._src_password

    @src_password.setter
    def src_password(self, src_password: str):
        """Sets the src_password of this CopyArtifactModel.

        :param name: The src_password of this CopyArtifactModel.
        :type name: str
        """

        self._src_password = src_password

    @property
    def dst_username(self) -> str:
        """Gets the dst_username of this CopyArtifactModel.

        :return: The dst_username of this CopyArtifactModel.
        :rtype: str
        """
        return self._dst_username

    @dst_username.setter
    def dst_username(self, dst_username: str):
        """Sets the dst_username of this CopyArtifactModel.

        :param name: The dst_username of this CopyArtifactModel.
        :type name: str
        """

        self._dst_username = dst_username

    @property
    def dst_password(self) -> str:
        """Gets the dst_password of this CopyArtifactModel.

        :return: The dst_password of this CopyArtifactModel.
        :rtype: str
        """
        return self._dst_password

    @dst_password.setter
    def dst_password(self, dst_password: str):
        """Sets the dst_password of this CopyArtifactModel.

        :param name: The dst_password of this CopyArtifactModel.
        :type name: str
        """

        self._dst_password = dst_password
