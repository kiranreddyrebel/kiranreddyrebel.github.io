# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# basic imports
from http.server import SimpleHTTPRequestHandler
import os
from urllib.parse import parse_qs, urlparse
from xbmcvfs import translatePath
import xbmcaddon
from resources.lib.utils import login, sendOTPV2

# codequick imports
from codequick import Script

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo("path")


class JioTVProxy(SimpleHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_response(200)

            html = os.path.join(translatePath(
                ADDON_PATH), "resources", "login.html")
            try:
                f = open(html, 'rb')
            except IOError:
                self.send_error(404, "File not found")
                return None

            self.send_header("Content-type", "text/html")
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs.st_size))
            self.end_headers()
            self.wfile.write(bytes(f.read()))
            f.close()
            return
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        if self.path == "/login":
            data_string = self.rfile.read(
                int(self.headers['Content-Length']))

            qs = parse_qs(data_string.decode('utf-8'))
            error = None
            Script.log(qs, lvl=Script.INFO)
            try:
                if qs.get("type")[0] == "password":
                    error = login(qs.get("username")[0], qs.get("password")[0])
                elif qs.get("type")[0] == "otp":
                    mobile = qs.get("mobile")[0]
                    if qs.get("otp"):
                        error = login(mobile, qs.get("otp")[0], mode="otp")
                    else:
                        error = sendOTPV2(mobile)
                else:
                    error = "Invalid Type"
            except Exception as e:
                Script.log(e, lvl=Script.ERROR)
                error = str(e)

            if error:
                location = "/?error="+str(error)
            elif qs.get("type")[0] == "otp" and qs.get("otp") is None:
                location = "/?otpsent=" + qs.get("mobile")[0]
            else:
                location = "/?success"
            self.send_response(302)
            self.send_header('Location', location)
            self.end_headers()
        else:
            self.send_error(404, "File not found")
