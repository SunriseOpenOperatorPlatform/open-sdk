from src.edgecloud.clients.piedge.lib.models.base_model_ import Model
from src.edgecloud.clients.piedge.lib import util

class GenericResponse(Model):

    def __init__(self, code: int, response):

        """ 
        :param code: the http status code for every request
        :param object: the object returned with every response. Can be any object defined within π-edge, a list or a simple string
        
        """
        self._code=code
        self._response=response

    
    @property
    def code(self) -> int:
        """Gets the code of this GenericResponse.

        :return: The code of this GenericResponse.
        :rtype: int
        """
        return self._code
    
    @code.setter
    def code(self, code: int):
        """Sets the code of this GenericResponse.

        :param code: The code of this GenericResponse.
        :type int
        """

        self._code = code

    
    @property
    def response(self):
        """Gets the response of this GenericResponse.

        :return: The response of this GenericResponse.
        :rtype: object
        """
        return self._response
    
    @response.setter
    def response(self, response):
        """Sets the response of this GenericResponse.

        :param response: The response of this GenericResponse.
        :type object
        """

        self._response = response