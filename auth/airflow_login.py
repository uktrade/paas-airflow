# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
#  Modified by the Department for International Trade
"""
Override this file to handle your authenticating / login.
Copy and alter this file and put in your PYTHONPATH as airflow_login.py,
the new module will override this one.
"""
from airflow import models
from airflow.utils.db import provide_session
from airflow.utils.log.logging_mixin import LoggingMixin
from flask import url_for, redirect, request, session as flask_session
from flask_login import (  # noqa: F401
    current_user,
    login_required,
    login_user,
    logout_user,
    LoginManager,
)
from requests_oauthlib import OAuth2Session

from auth import config


log = LoggingMixin().log


class StaffUser(models.User):
    def __init__(self, user):
        self.user = user

    @property
    def is_active(self):
        """Required by flask_login"""
        return True

    @property
    def is_authenticated(self):
        """Required by flask_login"""
        return True

    @property
    def is_anonymous(self):
        """Required by flask_login"""
        return False

    def get_id(self):
        """Returns the current user id as required by flask_login"""
        return self.user.get_id()

    def data_profiling(self):
        """Provides access to data profiling tools"""
        return True

    def is_superuser(self):
        """Access all the things"""
        return True


class AuthenticationError(Exception):
    pass


class AuthbrokerBackend(object):
    def __init__(self):
        self.login_manager = LoginManager()
        self.login_manager.login_view = "airflow.login"
        self.flask_app = None
        self.client_id = config.AUTHBROKER_CLIENT_ID
        self.client_secret = config.AUTHBROKER_CLIENT_SECRET
        self.allowed_domains = config.AUTHBROKER_ALLOWED_DOMAINS.split(",")
        self.base_url = config.AUTHBROKER_URL

    def init_app(self, flask_app):
        self.flask_app = flask_app

        self.login_manager.init_app(self.flask_app)
        self.login_manager.user_loader(self.load_user)

        self.flask_app.add_url_rule("/oauth2callback", "oauth2callback", self.oauth2callback)

    def login(self, request):
        sso = OAuth2Session(self.client_id, redirect_uri=url_for("oauth2callback", _external=True))
        authorization_url, state = sso.authorization_url(self.base_url + "o/authorize/")

        flask_session["sso_state"] = {"state": state, "next": request.args.get("next")}

        return redirect(authorization_url)

    def get_user_profile_email(self, authbroker_token):
        resp = self.authbroker_client.get(f"{self.base_url}{self.me_path}", token=(authbroker_token, ""))

        if not resp or resp.status != 200:
            raise AuthenticationError(
                "Failed to fetch user profile, status ({0})".format(resp.status if resp else "None")
            )

        return resp.data["email"]

    def domain_check(self, email):
        domain = email.split("@")[-1]
        if domain in self.allowed_domains:
            return True
        return False

    @provide_session
    def load_user(self, userid, session=None):
        if not userid or userid == "None":
            return None

        user = session.query(models.User).filter(models.User.id == int(userid)).first()
        return StaffUser(user)

    @provide_session
    def oauth2callback(self, session=None):
        log.debug("Authbroker callback called")
        sso = OAuth2Session(
            self.client_id,
            state=flask_session["sso_state"]["state"],
            redirect_uri=url_for("oauth2callback", _external=True),
        )

        sso.fetch_token(
            self.base_url + "o/token/", client_secret=self.client_secret, authorization_response=request.url,
        )

        resp = sso.get(self.base_url + "api/v1/user/me/")

        if resp.status_code != 200:
            log.info("User profile request failed")
            return redirect(url_for("airflow.noaccess"))

        email = resp.json()["email"]

        if not self.domain_check(email):
            return redirect(url_for("airflow.noaccess"))

        next_url = flask_session["sso_state"].get("next", url_for("admin.index"))

        user = session.query(models.User).filter(models.User.username == email).first()

        if not user:
            user = models.User(username=email, email=email, is_superuser=False)

        session.merge(user)
        session.commit()
        login_user(StaffUser(user))
        session.commit()

        return redirect(next_url)


login_manager = AuthbrokerBackend()


def login(self, request):
    return login_manager.login(request)
