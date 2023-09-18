from flask import Flask


class DefaultConfig:
    env_name = 'DEFAULT'


class Development(DefaultConfig):
    env_name = 'DEVELOP'


class Test(DefaultConfig):
    env_name = 'TEST'
    TESTING = True


class Production(DefaultConfig):
    env_name = 'PRODUCTION'
