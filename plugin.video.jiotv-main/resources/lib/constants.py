# -*- coding: utf-8 -*-
import os
from xbmcvfs import translatePath
import xbmcaddon
from codequick.script import Settings

ADDON = xbmcaddon.Addon()
ADDON_ID = 'plugin.video.jiotv'

# Urls
IMG_PUBLIC = "https://jioimages.cdn.jio.com/imagespublic/"
IMG_CATCHUP = "https://jiotv.catchup.cdn.jio.com/dare_images/images/"
IMG_CATCHUP_SHOWS = "https://jiotv.catchup.cdn.jio.com/dare_images/shows/"
PLAY_URL = "plugin://plugin.video.jiotv/resources/lib/main/play/?"
FEATURED_SRC = "https://tv.media.jio.com/apis/v1.6/getdata/featurednew?start=0&limit=30&langId=6"
CHANNELS_SRC_NEW = "https://jiotv.data.cdn.jio.com/apis/v3.0/getMobileChannelList/get/?langId=6&os=android&devicetype=phone&usertype=tvYR7NSNn7rymo3F&version=285"
CHANNELS_SRC = CHANNELS_SRC_NEW if Settings.get_boolean(
    "channelsrc") else "https://jiotv.data.cdn.jio.com/apis/v1.4/getMobileChannelList/get/?os=android&devicetype=phone&usertype=JIO&version=296&langId=6"
GET_CHANNEL_URL = "https://tv.media.jio.com/apis/v2.0/getchannelurl/getchannelurl?langId=6&userLanguages=All"
CATCHUP_SRC = "https://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get?offset={0}&channel_id={1}&langId=6"
M3U_SRC = os.path.join(translatePath(
    ADDON.getAddonInfo("profile")), "playlist.m3u")
EPG_PATH = os.path.join(translatePath(
    ADDON.getAddonInfo("profile")), "jiotv-epg.xml.gz")
M3U_CHANNEL = "\n#EXTINF:0 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" group-title=\"{group_title}\" tvg-chno=\"{tvg_chno}\" tvg-logo=\"{tvg_logo}\"{catchup},{channel_name}\n{play_url}"
# EPG_SRC = "https://kodi.botallen.com/tv/epg.xml.gz"
EPG_SRC = ADDON.getSetting("epgsource")
DICTIONARY_URL = "https://jiotvapi.cdn.jio.com/apis/v1.3/dictionary/dictionary?langId=6"

IMG_CONFIG = {
    "Genres": {
        "Entertainment":  {
            "tvImg":  IMG_PUBLIC + "38/52/Entertainment_1584620980069_tv.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/Entertainment_1579245819981.jpg",
        },
        "Movies":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/movies_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/movies_1579517470920.jpg",
        },
        "Kids":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/kids_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/kids_1579517470920.jpg",
        },
        "Sports":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/Sports_1579245819981.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/Sports_1579245819981.jpg",
        },
        "Lifestyle":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/lifestyle_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/lifestyle_1579517470920.jpg",
        },
        "Infotainment":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/infotainment_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/infotainment_1579517470920.jpg",
        },
        # "Religious":  {
        #     "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        #     "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        # },
        "News":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        },
        "Music":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/Music_1579245819981.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/Music_1579245819981.jpg",
        },
        # "Regional":  {
        #     "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        #     "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        # },
        "Devotional":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/devotional_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/devotional_1579517470920.jpg",
        },
        "Business News":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/business_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/business_1579517470920.jpg",
        },
        "Educational":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/educational_1579517470920.jpg",
        },
        "Shopping":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/shopping_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/shopping_1579517470920.jpg",
        },
        "Jio Darshan":  {
            "tvImg":  IMG_PUBLIC + "logos/langGen/jiodarshan_1579517470920.jpg",
            "promoImg": IMG_PUBLIC + "logos/langGen/jiodarshan_1579517470920.jpg",
        }
    },
    "Languages": {
        "Hindi":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Hindi_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"98/98/Hindi_1580458058289_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528144026.jpg"
        },
        "Marathi":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Marathi_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"30/23/Marathi_1580458084801_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528755040_s.jpg"
        },
        "Punjabi":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Punjabi_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"79/58/Punjabi_1580458722849_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/2105281190010_s.jpg"
        },
        "Urdu":  {
            # "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
            # "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/urdu1.jpg"
        },
        "Bengali":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Bengali_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"72/66/Bengali_1580459416363_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/2105281369026_s.jpg"
        },
        "English":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/English_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"52/8/English_1580458071796_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/Friends_Carousal.jpg"
        },
        "Malayalam":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Malayalam_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"67/0/Malayalam_1580459753008_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/2105281221000_s.jpg"
        },
        "Tamil":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Tamil_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"58/79/Tamil_1580458708325_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528429019.jpg"
        },
        "Gujarati":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Gujarati_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"41/66/Gujarati_1580459392856_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528196027.jpg"
        },
        "Odia":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Odia_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"67/0/Odia_1580459753008_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528722020.jpg"
        },
        "Telugu":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Telugu_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"89/86/Telugu_1580458096736_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528638024.jpg"
        },
        "Bhojpuri":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Bhojpuri_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"87/70/Bhojpuri_1580459428665_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/210528532010.jpg"
        },
        "Kannada":  {
            "tvImg": IMG_PUBLIC + "logos/langGen/Kannada_1579245819981.jpg",
            "promoImg": IMG_PUBLIC+"37/41/Kannada_1580458557594_promo.jpg",
            "image": IMG_CATCHUP_SHOWS + "cms/2105281370026.jpg"
        },
        "Assamese":  {
            # "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
            # "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        },
        "Nepali":  {
            # "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
            # "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        },
        "French":  {
            # "tvImg":  IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
            # "promoImg": IMG_PUBLIC + "logos/langGen/news_1579517470920.jpg",
        }
    }
}
