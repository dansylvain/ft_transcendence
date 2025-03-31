from django.shortcuts import render

# Create your views here.
import pyotp
import qrcode
import io
import base64
import json
import httpx

# import os
from django.contrib.auth.decorators import login_required
from .forms import TwoFaForm

from ultimate_project.user.utils.manage_user_data import get_user_info_w_username, update_user_info


