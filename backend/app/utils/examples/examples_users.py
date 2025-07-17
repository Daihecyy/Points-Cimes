from pydantic.config import JsonDict

example_UserUpdate: JsonDict = {
    "name": "Points Cime",
}

example_UserCreateRequest: JsonDict = {
    "email": "user@example.fr",
}

example_UserActivateRequest: JsonDict = {
    "name": "Points Cimes",
    "activation_token": "62D-QJI5IYrjuywH8IWnuBo0xHrbTCfw_18HP4mdRrA",
    "password": "areallycomplexpassword",
}
