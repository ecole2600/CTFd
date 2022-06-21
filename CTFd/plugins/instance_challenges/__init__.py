from __future__ import division  # Use floating point for math calculations

import math

from flask import Blueprint

from CTFd.models import Challenges, Solves, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.migrations import upgrade
from CTFd.utils.modes import get_model


class InstanceChallengeModel(DynamicChallenge):
    __mapper_args__ = {"polymorphic_identity": "instance"}
    endpoint = db.Column(db.Text, nullable=False)
    endpoint_access_key = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(InstanceChallengeModel, self).__init__(**kwargs)


class InstanceChallenge(DynamicValueChallenge):
    id = "instance"  # Unique identifier used to register challenges
    name = "instance"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/instance_challenges/assets/create.html",
        "update": "/plugins/instance_challenges/assets/update.html",
        "view": "/plugins/instance_challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/instance_challenges/assets/create.js",
        # "update": "/plugins/instance_challenges/assets/update.js",
        "view": "/plugins/instance_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/instance_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "instance_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = InstanceChallengeModel

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.
        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = InstanceChallengeModel.query.filter_by(
            id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)
        InstanceChallenge.calculate_value(challenge)
        # TODO: Destroy instance
        print("Solved. Destroy instance")

    @classmethod
    def deploy(cls, user, team, challenge, request):
        # TODO: Create instance
        print("Deploy challenge for user", user, challenge)


def load(app):
    upgrade()
    CHALLENGE_CLASSES["instance"] = InstanceChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/instance_challenges/assets/"
    )
