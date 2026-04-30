# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# xbmc imports
from xbmcaddon import Addon
from xbmc import executebuiltin, log, LOGINFO
from xbmcgui import Dialog, DialogProgress

# codequick imports
from codequick import Route, run, Listitem, Resolver, Script
from codequick.utils import keyboard
from codequick.script import Settings
from codequick.storage import PersistentDict
import xbmc
import time
import xbmcgui
import sys

# add-on imports
from resources.lib.utils import (
    getTokenParams,
    getHeaders,
    isLoggedIn,
    login as ULogin,
    logout as ULogout,
    check_addon,
    sendOTPV2,
    get_local_ip,
    getChannelHeaders,
    getSonyHeaders,
    getZeeHeaders,
    zeeCookie,
    getChannelHeadersWithHost,
    quality_to_enum,
    _setup,
    kodi_rpc,
    Monitor,
    getCachedChannels,
    getCachedDictionary,
    cleanLocalCache,
    getFeatured,
)
from resources.lib.constants import (
    GET_CHANNEL_URL,
    IMG_CATCHUP,
    PLAY_URL,
    IMG_CATCHUP_SHOWS,
    CATCHUP_SRC,
    M3U_SRC,
    EPG_SRC,
    M3U_CHANNEL,
    IMG_CONFIG,
    EPG_PATH,
    ADDON,
    ADDON_ID,
)

# additional imports
import urlquick
from uuid import uuid4
from urllib.parse import urlencode
import inputstreamhelper
from time import time, sleep
from datetime import datetime, timedelta, date
import m3u8
import requests
import gzip
import xml.etree.ElementTree as ET
import os
import json

# Root path of plugin

monitor = Monitor()


@Route.register
def root(plugin):
    yield Listitem.from_dict(
        **{
            "label": "Featured",
            "art": {
                "thumb": IMG_CATCHUP_SHOWS + "cms/TKSS_Carousal1.jpg",
                "icon": IMG_CATCHUP_SHOWS + "cms/TKSS_Carousal1.jpg",
                "fanart": IMG_CATCHUP_SHOWS + "cms/TKSS_Carousal1.jpg",
            },
            "callback": Route.ref("/resources/lib/main:show_featured"),
        }
    )
    for e in ["Genres", "Languages"]:
        yield Listitem.from_dict(
            **{
                "label": e,
                "callback": Route.ref("/resources/lib/main:show_listby"),
                "params": {"by": e},
            }
        )


# Shows Featured Content
@Route.register
def show_featured(plugin, id=None):
    for each in getFeatured():
        if id:
            if int(each.get("id", 0)) == int(id):
                data = each.get("data", [])
                for child in data:
                    info_dict = {
                        "art": {
                            "thumb": IMG_CATCHUP_SHOWS + child.get("episodePoster", ""),
                            "icon": IMG_CATCHUP_SHOWS + child.get("episodePoster", ""),
                            "fanart": IMG_CATCHUP_SHOWS + child.get("episodePoster", ""),
                            "clearart": IMG_CATCHUP + child.get("logoUrl", ""),
                            "clearlogo": IMG_CATCHUP + child.get("logoUrl", ""),
                        },
                        "info": {
                            "originaltitle": child.get("showname"),
                            "tvshowtitle": child.get("showname"),
                            "genre": child.get("showGenre"),
                            "plot": child.get("description"),
                            "episodeguide": child.get("episode_desc"),
                            "episode": 0
                            if child.get("episode_num") == -1
                            else child.get("episode_num"),
                            "cast": child.get("starCast", "").split(", "),
                            "director": child.get("director"),
                            "duration": child.get("duration") * 60,
                            "tag": child.get("keywords"),
                            "mediatype": "movie"
                            if child.get("channel_category_name") == "Movies"
                            else "episode",
                        },
                    }
                    if child.get("showStatus") == "Now":
                        info_dict["label"] = info_dict["info"]["title"] = (
                            child.get("showname", "") + " [COLOR red] [ LIVE ] [/COLOR]"
                        )
                        info_dict["callback"] = play
                        info_dict["params"] = {"channel_id": child.get("channel_id")}
                        yield Listitem.from_dict(**info_dict)
                    elif child.get("showStatus") == "future":
                        timetext = datetime.fromtimestamp(
                            int(child.get("startEpoch", 0) * 0.001)
                        ).strftime("    [ %I:%M %p -") + datetime.fromtimestamp(
                            int(child.get("endEpoch", 0) * 0.001)
                        ).strftime(" %I:%M %p ]   %a")
                        info_dict["label"] = info_dict["info"]["title"] = child.get(
                            "showname", ""
                        ) + (" [COLOR green]%s[/COLOR]" % timetext)
                        info_dict["callback"] = ""
                        yield Listitem.from_dict(**info_dict)
                    elif child.get("showStatus") == "catchup":
                        timetext = datetime.fromtimestamp(
                            int(child.get("startEpoch", 0) * 0.001)
                        ).strftime("    [ %I:%M %p -") + datetime.fromtimestamp(
                            int(child.get("endEpoch", 0) * 0.001)
                        ).strftime(" %I:%M %p ]   %a")
                        info_dict["label"] = info_dict["info"]["title"] = child.get(
                            "showname", ""
                        ) + (" [COLOR yellow]%s[/COLOR]" % timetext)
                        info_dict["callback"] = play
                        info_dict["params"] = {
                            "channel_id": child.get("channel_id"),
                            "showtime": child.get("showtime", "").replace(":", ""),
                            "srno": datetime.fromtimestamp(
                                int(child.get("startEpoch", 0) * 0.001)
                            ).strftime("%Y%m%d"),
                            "programId": child.get("srno", ""),
                            "begin": datetime.utcfromtimestamp(
                                int(child.get("startEpoch", 0) * 0.001)
                            ).strftime("%Y%m%dT%H%M%S"),
                            "end": datetime.utcfromtimestamp(
                                int(child.get("endEpoch", 0) * 0.001)
                            ).strftime("%Y%m%dT%H%M%S"),
                        }
                        yield Listitem.from_dict(**info_dict)
        else:
            yield Listitem.from_dict(
                **{
                    "label": each.get("name"),
                    "art": {
                        "thumb": IMG_CATCHUP_SHOWS
                        + each.get("data", [{}])[0].get("episodePoster"),
                        "icon": IMG_CATCHUP_SHOWS
                        + each.get("data", [{}])[0].get("episodePoster"),
                        "fanart": IMG_CATCHUP_SHOWS
                        + each.get("data", [{}])[0].get("episodePoster"),
                    },
                    "callback": Route.ref("/resources/lib/main:show_featured"),
                    "params": {"id": each.get("id")},
                }
            )


# Shows Filter options
@Route.register
def show_listby(plugin, by):
    dictionary = getCachedDictionary()
    GENRE_MAP = dictionary.get("channelCategoryMapping")
    LANG_MAP = dictionary.get("languageIdMapping")
    langValues = list(LANG_MAP.values())
    langValues.append("Extra")
    CONFIG = {
        "Genres": GENRE_MAP.values(),
        "Languages": langValues,
    }
    for each in CONFIG[by]:
        tvImg = IMG_CONFIG[by].get(each, {}).get("tvImg", "")
        promoImg = IMG_CONFIG[by].get(each, {}).get("promoImg", "")
        yield Listitem.from_dict(
            **{
                "label": each,
                "art": {"thumb": tvImg, "icon": tvImg, "fanart": promoImg},
                "callback": Route.ref("/resources/lib/main:show_category"),
                "params": {"categoryOrLang": each, "by": by},
            }
        )


def is_lang_allowed(langId, langMap):
    if langId in langMap.keys():
        return Settings.get_boolean(langMap[langId])
    else:
        return Settings.get_boolean("Extra")


def is_genre_allowed(id, map):
    if id in map.keys():
        return Settings.get_boolean(map[id])
    else:
        return False


def isPlayAbleLang(each, LANG_MAP):
    return not each.get("channelIdForRedirect") and is_lang_allowed(
        str(each.get("channelLanguageId")), LANG_MAP
    )


def isPlayAbleGenre(each, GENRE_MAP):
    return not each.get("channelIdForRedirect") and is_genre_allowed(
        str(each.get("channelCategoryId")), GENRE_MAP
    )


# Shows channels by selected filter/category
@Route.register
def show_category(plugin, categoryOrLang, by):
    resp = getCachedChannels()
    dictionary = getCachedDictionary()
    GENRE_MAP = dictionary.get("channelCategoryMapping")
    LANG_MAP = dictionary.get("languageIdMapping")

    def fltr(x):
        fby = by.lower()[:-1]
        if fby == "genre":
            return GENRE_MAP[
                str(x.get("channelCategoryId"))
            ] == categoryOrLang and isPlayAbleLang(x, LANG_MAP)
        else:
            if categoryOrLang == "Extra":
                return str(
                    x.get("channelLanguageId")
                ) not in LANG_MAP.keys() and isPlayAbleGenre(x, GENRE_MAP)
            else:
                if str(x.get("channelLanguageId")) not in LANG_MAP.keys():
                    return False
                return LANG_MAP[
                    str(x.get("channelLanguageId"))
                ] == categoryOrLang and isPlayAbleGenre(x, GENRE_MAP)

    try:
        flist = list(filter(fltr, resp))
        if len(flist) < 1:
            yield Listitem.from_dict(
                **{
                    "label": "No Results Found, Go Back",
                    "callback": show_listby,
                    "params": {"by": by},
                }
            )
        else:
            for each in flist:
                if Settings.get_boolean("number_toggle"):
                    channel_number = int(each.get("channel_order")) + 1
                    channel_name = str(channel_number) + " " + each.get("channel_name")
                else:
                    channel_name = each.get("channel_name")
                litm = Listitem.from_dict(
                    **{
                        "label": channel_name,
                        "art": {
                            "thumb": IMG_CATCHUP + each.get("logoUrl"),
                            "icon": IMG_CATCHUP + each.get("logoUrl"),
                            "fanart": IMG_CATCHUP + each.get("logoUrl"),
                            "clearlogo": IMG_CATCHUP + each.get("logoUrl"),
                            "clearart": IMG_CATCHUP + each.get("logoUrl"),
                        },
                        "callback": play,
                        "params": {"channel_id": each.get("channel_id")},
                    }
                )
                if each.get("isCatchupAvailable"):
                    litm.context.container(
                        show_epg, "Catchup", 0, each.get("channel_id")
                    )
                yield litm
    except Exception as e:
        Script.notify("Error", e)
        monitor.waitForAbort(1)
        return False


# Shows EPG container from Context menu
@Route.register
def show_epg(plugin, day, channel_id):
    resp = urlquick.get(
        CATCHUP_SRC.format(day, channel_id), max_age=-1
    ).json()
    epg = sorted(resp["epg"], key=lambda show: show["startEpoch"], reverse=False)
    livetext = "[COLOR red] [ LIVE ] [/COLOR]"
    for each in epg:
        current_epoch = int(time() * 1000)
        if not each["stbCatchupAvailable"] or each["startEpoch"] > current_epoch:
            continue
        islive = each["startEpoch"] < current_epoch and each["endEpoch"] > current_epoch
        showtime = (
            "   " + livetext
            if islive
            else datetime.fromtimestamp(int(each["startEpoch"] * 0.001)).strftime(
                "    [ %I:%M %p -"
            )
            + datetime.fromtimestamp(int(each["endEpoch"] * 0.001)).strftime(
                " %I:%M %p ]   %a"
            )
        )
        yield Listitem.from_dict(
            **{
                "label": each["showname"] + showtime,
                "art": {
                    "thumb": IMG_CATCHUP_SHOWS + each["episodePoster"],
                    "icon": IMG_CATCHUP_SHOWS + each["episodePoster"],
                    "fanart": IMG_CATCHUP_SHOWS + each["episodePoster"],
                },
                "callback": play,
                "info": {
                    "title": each["showname"] + showtime,
                    "originaltitle": each["showname"],
                    "tvshowtitle": each["showname"],
                    "genre": each["showGenre"],
                    "plot": each["description"],
                    "episodeguide": each.get("episode_desc"),
                    "episode": 0 if each["episode_num"] == -1 else each["episode_num"],
                    "cast": each["starCast"].split(", "),
                    "director": each["director"],
                    "duration": each["duration"] * 60,
                    "tag": each["keywords"],
                    "mediatype": "episode",
                },
                "params": {
                    "channel_id": each.get("channel_id"),
                    "showtime": each.get("showtime", "").replace(":", ""),
                    "srno": datetime.fromtimestamp(
                        int(each.get("startEpoch", 0) * 0.001)
                    ).strftime("%Y%m%d"),
                    "programId": each.get("srno", ""),
                    "begin": datetime.utcfromtimestamp(
                        int(each.get("startEpoch", 0) * 0.001)
                    ).strftime("%Y%m%dT%H%M%S"),
                    "end": datetime.utcfromtimestamp(
                        int(each.get("endEpoch", 0) * 0.001)
                    ).strftime("%Y%m%dT%H%M%S"),
                },
            }
        )
    if int(day) == 0:
        for i in range(-1, -7, -1):
            label = (
                "Yesterday"
                if i == -1
                else (date.today() + timedelta(days=i)).strftime("%A %d %B")
            )
            yield Listitem.from_dict(
                **{
                    "label": label,
                    "callback": Route.ref("/resources/lib/main:show_epg"),
                    "params": {"day": i, "channel_id": channel_id},
                }
            )


# Play live stream / catchup according to params.
# Also ensures that user is logged in.
# 🔥 CLEAN & FIXED PLAY FUNCTION ONLY
# Replace your existing play() function with this

@Resolver.register
@isLoggedIn
def play(plugin, channel_id, showtime=None, srno=None, programId=None, begin=None, end=None):
    import xbmc
    import xbmcgui
    import requests
    import time

    sony_headers = getSonyHeaders()

    def get_stream():
        try:
            res = requests.post(
                "https://jiotvapi.media.jio.com/playback/apis/v1/geturl?langId=6",
                data="stream_type=Seek&channel_id=" + str(channel_id),
                headers=sony_headers,
                verify=False,
                timeout=10,
            )
            return res.json().get("result", "")
        except Exception as e:
            xbmc.log("❌ Stream fetch error: " + str(e), xbmc.LOGERROR)
            return None

    # 🔹 Initial stream fetch
    url = get_stream()
    if not url:
        xbmcgui.Dialog().notification("Error", "Stream not available")
        return False

    # 🔥 Start playback
    player = xbmc.Player()

    def play_url(u):
        item = xbmcgui.ListItem(path=u)
        item.setProperty("IsPlayable", "true")
        item.setProperty("inputstream", "inputstream.adaptive")
        item.setProperty("inputstream.adaptive.manifest_type", "hls")
        item.setProperty("inputstream.adaptive.stream_headers", "user-agent=jiotv")
        item.setProperty("inputstream.adaptive.manifest_headers", "user-agent=jiotv")
        player.play(u, item)

    play_url(url)
    xbmc.sleep(2000)
    xbmc.executebuiltin('Dialog.Close(all)')

    # 🔁 AUTO REFRESH LOOP (MAIN FIX)
    while True:
        time.sleep(5)

        # 🔴 EXIT if user stopped or switched channel
        if not player.isPlaying():
            xbmc.log("🛑 Player stopped → exiting loop", xbmc.LOGINFO)
            break

        # 🔄 Refresh only if playback dropped
        if not player.isPlayingVideo():
            xbmc.log("⚠️ Stream stopped → refreshing", xbmc.LOGINFO)

            new_url = get_stream()

            if new_url:
                play_url(new_url)
                xbmc.log("✅ Stream restarted", xbmc.LOGINFO)
            else:
                xbmc.log("❌ Failed to refresh stream", xbmc.LOGERROR)
                break

    return None



# Login `route` to access from Settings
@Script.register
def login(plugin):
    method = Dialog().yesno(
        "Login", "Select Login Method", yeslabel="Keyboard", nolabel="WEB"
    )
    if method == 1:
        login_type = Dialog().yesno(
            "Login", "Select Login Type", yeslabel="OTP", nolabel="Password"
        )
        if login_type == 1:
            mobile = Settings.get_string("mobile")
            if not mobile or (len(mobile) != 10):
                mobile = Dialog().numeric(0, "Enter your Jio mobile number")
                ADDON.setSetting("mobile", mobile)
            error = sendOTPV2(mobile)
            if error:
                Script.notify("Login Error", error)
                return
            otp = Dialog().numeric(0, "Enter OTP")
            ULogin(mobile, otp, mode="otp")
        elif login_type == 0:
            username = keyboard("Enter your Jio mobile number or email")
            password = keyboard("Enter your password", hidden=True)
            ULogin(username, password)
    elif method == 0:
        pDialog = DialogProgress()
        pDialog.create(
            "JioTV", "Visit [B]http://%s:48996/[/B] to login" % get_local_ip()
        )
        for i in range(120):
            sleep(1)
            with PersistentDict("headers") as db:
                headers = db.get("headers")
            if headers or pDialog.iscanceled():
                break
            pDialog.update(i)
        pDialog.close()


@Script.register
def setmobile(plugin):
    prevMobile = Settings.get_string("mobile")
    mobile = Dialog().numeric(0, "Update Jio mobile number", prevMobile)
    kodi_rpc("Addons.SetAddonEnabled", {"addonid": ADDON_ID, "enabled": False})
    ADDON.setSetting("mobile", mobile)
    kodi_rpc("Addons.SetAddonEnabled", {"addonid": ADDON_ID, "enabled": True})
    monitor.waitForAbort(1)
    Script.notify("Jio number set", "")


@Script.register
def applyall(plugin):
    kodi_rpc("Addons.SetAddonEnabled", {"addonid": ADDON_ID, "enabled": False})
    monitor.waitForAbort(1)
    kodi_rpc("Addons.SetAddonEnabled", {"addonid": ADDON_ID, "enabled": True})
    monitor.waitForAbort(1)
    Script.notify("All settings applied", "")


# Logout `route` to access from Settings
@Script.register
def logout(plugin):
    ULogout()


# M3u Generate `route`
@Script.register
def m3ugen(plugin, notify="yes"):
    channels = getCachedChannels()
    dictionary = getCachedDictionary()
    GENRE_MAP = dictionary.get("channelCategoryMapping")
    LANG_MAP = dictionary.get("languageIdMapping")

    m3ustr = '#EXTM3U x-tvg-url="%s"\n' % EPG_SRC

    for i, channel in enumerate(channels):
        channel_id = int(channel.get("channel_id"))

        if 5000 <= channel_id <= 5022:
            continue  # Skip ZEE range from default block, handled separately below

        if str(channel.get("channelLanguageId")) not in LANG_MAP.keys():
            lang = "Extra"
        else:
            lang = LANG_MAP[str(channel.get("channelLanguageId"))]

        if str(channel.get("channelCategoryId")) not in GENRE_MAP.keys():
            genre = "Extragenre"
        else:
            genre = GENRE_MAP[str(channel.get("channelCategoryId"))]

        if not Settings.get_boolean(lang):
            continue

        group = lang + ";" + genre
        _play_url = PLAY_URL + "channel_id={0}".format(channel_id)

        catchup = ""
        if channel.get("isCatchupAvailable"):
            catchup = ' catchup="vod" catchup-source="{0}channel_id={1}&showtime={{H}}{{M}}{{S}}&srno={{Y}}{{m}}{{d}}&programId={{catchup-id}}" catchup-days="7"'.format(
                PLAY_URL, channel_id
            )

        m3ustr += M3U_CHANNEL.format(
            tvg_id=channel_id,
            channel_name=channel.get("channel_name"),
            group_title=group,
            tvg_chno=int(channel.get("channel_order", i)) + 1,
            tvg_logo=IMG_CATCHUP + channel.get("logoUrl", ""),
            catchup=catchup,
            play_url=_play_url,
        )

    # Hardcoded ZEE free channels
    zee_channels = [
        {"@id": "5016", "display-name": "Zee Anmol Cinema", "icon": {"@src": "https://akamaividz2.zee5.com/image/upload/w_396,h_224,c_scale,f_webp,q_auto:eco/resources/0-9-zeeanmol/cover/1920x77021724318"}},
        {"@id": "5017", "display-name": "Zee Action", "icon": {"@src": "https://akamaividz2.zee5.com/image/upload/w_396,h_224,c_scale,f_webp,q_auto:eco/resources/0-9-zeeaction/cover/1920x770126103899"}},
        {"@id": "5023", "display-name": "Zee Chitramandir", "icon": {"@src": "https://akamaividz2.zee5.com/image/upload/w_1755,h_987,c_scale,f_webp,q_auto:eco/resources/0-9-394/list_clean/1920x1080liste8fe4dcfd539403d973018b5d3e16309.png"}},
        {"@id": "5024", "display-name": "Zee Anmol TV", "icon": {"@src": "https://akamaividz2.zee5.com/image/upload/w_1755,h_987,c_scale,f_webp,q_auto:eco/resources/0-9-zeeanmol/list_clean/1920x1080list0481942c331940e0a2356355bcdec8bb.png"}},
        {"@id": "5025", "display-name": "Zee Anmol Cinema_2", "icon": {"@src": "https://akamaividz2.zee5.com/image/upload/w_396,h_224,c_scale,f_webp,q_auto:eco/resources/0-9-zeeanmol/cover/1920x77021724318"}},
        {"@id": "5026", "display-name": "Big Magic", "icon": {"@src": "https://akamaividz2.zee5.com/image/upload/w_396,h_224,c_scale,f_webp,q_auto:eco/resources/0-9-zeeanmol/cover/1920x77021724318"}},
    ]

    for zee in zee_channels:
        cid = zee["@id"]
        name = zee["display-name"]
        logo = zee["icon"]["@src"]

        m3ustr += (
            f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" group-title="ZEE" tvg-logo="{logo}",{name}\n'
            f'plugin://plugin.video.jiotv/resources/lib/main/play/?channel_id={cid}\n'
        )

    with open(M3U_SRC, "w+", encoding="utf-8") as f:
        f.write(m3ustr.replace("\xa0", " "))

    if notify == "yes":
        Script.notify("JioTV", "Playlist updated.")


# EPG Generate `route`
@Script.register
def epg_setup(plugin):
    Script.notify("Please wait", "Epg setup in progress")
    pDialog = DialogProgress()
    pDialog.create("Epg setup in progress")
    url = Settings.get_string("epgurl")
    if not url or (len(url) < 5):
        url = "https://kiranreddyrebel.github.io/epg.xml.gz"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    with open(EPG_PATH, "wb") as f:
        f.write(response.content)
    pDialog.update(20)
    with gzip.open(EPG_PATH, "rb") as f:
        data = f.read()
        xml_content = data.decode("utf-8")
        root = ET.fromstring(xml_content)
    pDialog.update(30)
    pDialog.update(35)
    pDialog.update(45)
    for program in root.iterfind(".//programme"):
        icon = program.find("icon")
        icon_src = icon.get("src")
        jpg_name = icon_src.rsplit("/", 1)[-1]
        catchup_id = os.path.splitext(jpg_name)[0]
        program.set("catchup-id", catchup_id)
        title = program.find("title")
        title.text = title.text.strip()
    pDialog.update(60)
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    doctype_declaration = '<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
    full_xml_bytes = (
        xml_declaration.encode("UTF-8")
        + doctype_declaration.encode("UTF-8")
        + ET.tostring(root, encoding="UTF-8")
    )
    gzip_bytes = gzip.compress(full_xml_bytes)
    pDialog.update(80)
    with open(EPG_PATH, "wb") as f:
        f.write(gzip_bytes)
    pDialog.update(100)
    pDialog.close()
    Script.notify("JioTV", "Epg generated")


# PVR Setup `route` to access from Settings
@Script.register
def pvrsetup(plugin):
    executebuiltin("RunPlugin(plugin://plugin.video.jiotv/resources/lib/main/m3ugen/)")
    IDdoADDON = "pvr.iptvsimple"

    def set_setting(id, value):
        if Addon(IDdoADDON).getSetting(id) != value:
            Addon(IDdoADDON).setSetting(id, value)

    if check_addon(IDdoADDON):
        set_setting("m3uPathType", "0")
        set_setting("m3uPath", M3U_SRC)
        set_setting("epgPathType", "1")
        set_setting("epgUrl", EPG_SRC)
        set_setting("epgCache", "false")
        set_setting("useInputstreamAdaptiveforHls", "true")
        set_setting("catchupEnabled", "true")
        set_setting("catchupWatchEpgBeginBufferMins", "0")
        set_setting("catchupWatchEpgEndBufferMins", "0")
    _setup(M3U_SRC, EPG_SRC)
    


# Cache cleanup
@Script.register
def cleanup(plugin):
    urlquick.cache_cleanup(-1)
    cleanLocalCache()
    Script.notify("Cache Cleaned", "")