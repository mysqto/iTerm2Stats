#!/usr/bin/env python3

import os
import time

import iterm2

ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA/klEQVQ4jc3SvS5FURAF4M8NDYmIn5aEZ6ChQaFBrxD3JRRqbyEqxRVar" \
         "mhJROjFC4jCT8JtEAU5yRyZyBGnUJhkZe89s9aafWYffxUDaOEjsFThu5zqO+jPxb1UPMIoprAemMQYjhOvlQ06kdzCLM4TscQZ5rAd50" \
         "42uMUuVvCWRBuB8vwanH3cZIMRzOPxW9fFQM49BLfQaITBfQxpsMajDMWQC43uSHZhIfZPaGMYV5iuMCm5XwbF2hv7O2zGVV8wU2HQhx6" \
         "85+RpxeR/wkkpaiSDgxrf/yv3sEb3dhbkGxTxXKN7MeTKaOIaE1jDZfxtBS6wivHgFNz/EPgE799W245hq7EAAAAASUVORK5CYII="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABm0lEQVRIie2WzUoCURTHfwVhQl+6cJNPU" \
         "KvcFPUMFT1BH1g9QCCmm15HCgrqEQIjKygLpEWbWrgyE11YgS1mJqfhjHMu3Hb+4cAwc/7nd8/M3MuBoWAROAUaQBeoAjkgpvDG3Nx7oA" \
         "PUgRKQiTLuA99AT4gtBTgb4v0CNsNMSwOgBQXU01FIjU9COj+LgCaBHTevBrTdqOF8mm0gEQEvSeBGCDQOFIGPkGL+aPo8ErwugbsCNA3" \
         "cKoDBqACzArwtgR8E6NuA4svAyoDnrwL8TgLnfNC4olNPUZ2P++AHEjhGf8sUIwpqwT0g7+ZliTgLkuh+JC24Sf9v/9WoAN4ApgatzFDT" \
         "wLoGvGoR6mlNA57/B/CcJqmFvHXCpNnXraBJ6nhEec+6njE/qaKiFoRIHT/a7QOAJw344h/A55qkBPCOvdfcAGa0KyxYBOcx0BhwaQF6h" \
         "W5W+6OMBfCCKTSFM132cAY1U6Dnqbq11Kr4jGnMRp9DnAHAW/i1CbgM3ARWOwnsASfAC87c3HGvj4FdYMKXn3JrlE3AQ1nXDxnvStm/nl" \
         "D9AAAAAElFTkSuQmCC"


def emoji(country):
    offset = 127397
    return chr(ord(country[0]) + offset) + chr(ord(country[1]) + offset)


timezones = {
    "Africa/Abidjan": "🇨🇮",
    "Africa/Accra": "🇬🇭",
    "Africa/Addis_Ababa": "🇪🇹",
    "Africa/Algiers": "🇩🇿",
    "Africa/Asmara": "🇪🇷",
    "Africa/Asmera": "🇪🇷",
    "Africa/Bamako": "🇲🇱",
    "Africa/Bangui": "🇨🇫",
    "Africa/Banjul": "🇬🇲",
    "Africa/Bissau": "🇬🇼",
    "Africa/Blantyre": "🇲🇼",
    "Africa/Brazzaville": "🇨🇬",
    "Africa/Bujumbura": "🇧🇮",
    "Africa/Cairo": "🇪🇬",
    "Africa/Casablanca": "🇲🇦",
    "Africa/Ceuta": "🇪🇸",
    "Africa/Conakry": "🇬🇳",
    "Africa/Dakar": "🇸🇳",
    "Africa/Dar_es_Salaam": "🇹🇿",
    "Africa/Djibouti": "🇩🇯",
    "Africa/Douala": "🇨🇲",
    "Africa/El_Aaiun": "🇪🇭",
    "Africa/Freetown": "🇸🇱",
    "Africa/Gaborone": "🇧🇼",
    "Africa/Harare": "🇿🇼",
    "Africa/Johannesburg": "🇿🇦",
    "Africa/Juba": "🇸🇸",
    "Africa/Kampala": "🇺🇬",
    "Africa/Khartoum": "🇸🇩",
    "Africa/Kigali": "🇷🇼",
    "Africa/Kinshasa": "🇨🇩",
    "Africa/Lagos": "🇳🇬",
    "Africa/Libreville": "🇬🇦",
    "Africa/Lome": "🇹🇬",
    "Africa/Luanda": "🇦🇴",
    "Africa/Lubumbashi": "🇨🇩",
    "Africa/Lusaka": "🇿🇲",
    "Africa/Malabo": "🇬🇶",
    "Africa/Maputo": "🇲🇿",
    "Africa/Maseru": "🇱🇸",
    "Africa/Mbabane": "🇸🇿",
    "Africa/Mogadishu": "🇸🇴",
    "Africa/Monrovia": "🇱🇷",
    "Africa/Nairobi": "🇰🇪",
    "Africa/Ndjamena": "🇹🇩",
    "Africa/Niamey": "🇳🇪",
    "Africa/Nouakchott": "🇲🇷",
    "Africa/Ouagadougou": "🇧🇫",
    "Africa/Porto-Novo": "🇧🇯",
    "Africa/Sao_Tome": "🇸🇹",
    "Africa/Timbuktu": "🇲🇱",
    "Africa/Tripoli": "🇱🇾",
    "Africa/Tunis": "🇹🇳",
    "Africa/Windhoek": "🇳🇦",
    "America/Adak": "🇺🇸",
    "America/Anchorage": "🇺🇸",
    "America/Anguilla": "🇦🇮",
    "America/Antigua": "🇦🇬",
    "America/Araguaina": "🇧🇷",
    "America/Argentina/Buenos_Aires": "🇦🇷",
    "America/Argentina/Catamarca": "🇦🇷",
    "America/Argentina/ComodRivadavia": "🇦🇷",
    "America/Argentina/Cordoba": "🇦🇷",
    "America/Argentina/Jujuy": "🇦🇷",
    "America/Argentina/La_Rioja": "🇦🇷",
    "America/Argentina/Mendoza": "🇦🇷",
    "America/Argentina/Rio_Gallegos": "🇦🇷",
    "America/Argentina/Salta": "🇦🇷",
    "America/Argentina/San_Juan": "🇦🇷",
    "America/Argentina/San_Luis": "🇦🇷",
    "America/Argentina/Tucuman": "🇦🇷",
    "America/Argentina/Ushuaia": "🇦🇷",
    "America/Aruba": "🇦🇼",
    "America/Asuncion": "🇵🇾",
    "America/Atikokan": "🇨🇦",
    "America/Atka": "🇺🇸",
    "America/Bahia": "🇧🇷",
    "America/Bahia_Banderas": "🇲🇽",
    "America/Barbados": "🇧🇧",
    "America/Belem": "🇧🇷",
    "America/Belize": "🇧🇿",
    "America/Blanc-Sablon": "🇨🇦",
    "America/Boa_Vista": "🇧🇷",
    "America/Bogota": "🇨🇴",
    "America/Boise": "🇺🇸",
    "America/Buenos_Aires": "🇦🇷",
    "America/Cambridge_Bay": "🇨🇦",
    "America/Campo_Grande": "🇧🇷",
    "America/Cancun": "🇲🇽",
    "America/Caracas": "🇻🇪",
    "America/Catamarca": "🇦🇷",
    "America/Cayenne": "🇬🇫",
    "America/Cayman": "🇰🇾",
    "America/Chicago": "🇺🇸",
    "America/Chihuahua": "🇲🇽",
    "America/Coral_Harbour": "🇨🇦",
    "America/Cordoba": "🇦🇷",
    "America/Costa_Rica": "🇨🇷",
    "America/Creston": "🇨🇦",
    "America/Cuiaba": "🇧🇷",
    "America/Curacao": "🇨🇼",
    "America/Danmarkshavn": "🇬🇱",
    "America/Dawson": "🇨🇦",
    "America/Dawson_Creek": "🇨🇦",
    "America/Denver": "🇺🇸",
    "America/Detroit": "🇺🇸",
    "America/Dominica": "🇩🇲",
    "America/Edmonton": "🇨🇦",
    "America/Eirunepe": "🇧🇷",
    "America/El_Salvador": "🇸🇻",
    "America/Ensenada": "🇲🇽",
    "America/Fort_Nelson": "🇨🇦",
    "America/Fort_Wayne": "🇺🇸",
    "America/Fortaleza": "🇧🇷",
    "America/Glace_Bay": "🇨🇦",
    "America/Godthab": "🇬🇱",
    "America/Goose_Bay": "🇨🇦",
    "America/Grand_Turk": "🇹🇨",
    "America/Grenada": "🇬🇩",
    "America/Guadeloupe": "🇬🇵",
    "America/Guatemala": "🇬🇹",
    "America/Guayaquil": "🇪🇨",
    "America/Guyana": "🇬🇾",
    "America/Halifax": "🇨🇦",
    "America/Havana": "🇨🇺",
    "America/Hermosillo": "🇲🇽",
    "America/Indiana/Indianapolis": "🇺🇸",
    "America/Indiana/Knox": "🇺🇸",
    "America/Indiana/Marengo": "🇺🇸",
    "America/Indiana/Petersburg": "🇺🇸",
    "America/Indiana/Tell_City": "🇺🇸",
    "America/Indiana/Vevay": "🇺🇸",
    "America/Indiana/Vincennes": "🇺🇸",
    "America/Indiana/Winamac": "🇺🇸",
    "America/Indianapolis": "🇺🇸",
    "America/Inuvik": "🇨🇦",
    "America/Iqaluit": "🇨🇦",
    "America/Jamaica": "🇯🇲",
    "America/Jujuy": "🇦🇷",
    "America/Juneau": "🇺🇸",
    "America/Kentucky/Louisville": "🇺🇸",
    "America/Kentucky/Monticello": "🇺🇸",
    "America/Knox_IN": "🇺🇸",
    "America/Kralendijk": "🇧🇶",
    "America/La_Paz": "🇧🇴",
    "America/Lima": "🇵🇪",
    "America/Los_Angeles": "🇺🇸",
    "America/Louisville": "🇺🇸",
    "America/Lower_Princes": "🇸🇽",
    "America/Maceio": "🇧🇷",
    "America/Managua": "🇳🇮",
    "America/Manaus": "🇧🇷",
    "America/Marigot": "🇲🇫",
    "America/Martinique": "🇲🇶",
    "America/Matamoros": "🇲🇽",
    "America/Mazatlan": "🇲🇽",
    "America/Mendoza": "🇦🇷",
    "America/Menominee": "🇺🇸",
    "America/Merida": "🇲🇽",
    "America/Metlakatla": "🇺🇸",
    "America/Mexico_City": "🇲🇽",
    "America/Miquelon": "🇵🇲",
    "America/Moncton": "🇨🇦",
    "America/Monterrey": "🇲🇽",
    "America/Montevideo": "🇺🇾",
    "America/Montreal": "🇨🇦",
    "America/Montserrat": "🇲🇸",
    "America/Nassau": "🇧🇸",
    "America/New_York": "🇺🇸",
    "America/Nipigon": "🇨🇦",
    "America/Nome": "🇺🇸",
    "America/Noronha": "🇧🇷",
    "America/North_Dakota/Beulah": "🇺🇸",
    "America/North_Dakota/Center": "🇺🇸",
    "America/North_Dakota/New_Salem": "🇺🇸",
    "America/Ojinaga": "🇲🇽",
    "America/Panama": "🇵🇦",
    "America/Pangnirtung": "🇨🇦",
    "America/Paramaribo": "🇸🇷",
    "America/Phoenix": "🇺🇸",
    "America/Port_of_Spain": "🇹🇹",
    "America/Port-au-Prince": "🇭🇹",
    "America/Porto_Acre": "🇧🇷",
    "America/Porto_Velho": "🇧🇷",
    "America/Puerto_Rico": "🇵🇷",
    "America/Punta_Arenas": "🇨🇱",
    "America/Rainy_River": "🇨🇦",
    "America/Rankin_Inlet": "🇨🇦",
    "America/Recife": "🇧🇷",
    "America/Regina": "🇨🇦",
    "America/Resolute": "🇨🇦",
    "America/Rio_Branco": "🇧🇷",
    "America/Rosario": "🇦🇷",
    "America/Santa_Isabel": "🇲🇽",
    "America/Santarem": "🇧🇷",
    "America/Santiago": "🇨🇱",
    "America/Santo_Domingo": "🇩🇴",
    "America/Sao_Paulo": "🇧🇷",
    "America/Scoresbysund": "🇬🇱",
    "America/Shiprock": "🇺🇸",
    "America/Sitka": "🇺🇸",
    "America/St_Barthelemy": "🇧🇱",
    "America/St_Johns": "🇨🇦",
    "America/St_Kitts": "🇰🇳",
    "America/St_Lucia": "🇱🇨",
    "America/St_Thomas": "🇻🇮",
    "America/St_Vincent": "🇻🇨",
    "America/Swift_Current": "🇨🇦",
    "America/Tegucigalpa": "🇭🇳",
    "America/Thule": "🇬🇱",
    "America/Thunder_Bay": "🇨🇦",
    "America/Tijuana": "🇲🇽",
    "America/Toronto": "🇨🇦",
    "America/Tortola": "🇻🇬",
    "America/Vancouver": "🇨🇦",
    "America/Virgin": "🇺🇸",
    "America/Whitehorse": "🇨🇦",
    "America/Winnipeg": "🇨🇦",
    "America/Yakutat": "🇺🇸",
    "America/Yellowknife": "🇨🇦",
    "Antarctica/Casey": "🇦🇶",
    "Antarctica/Davis": "🇦🇶",
    "Antarctica/DumontDUrville": "🇦🇶",
    "Antarctica/Macquarie": "🇦🇺",
    "Antarctica/Mawson": "🇦🇶",
    "Antarctica/McMurdo": "🇦🇶",
    "Antarctica/Palmer": "🇦🇶",
    "Antarctica/Rothera": "🇦🇶",
    "Antarctica/South_Pole": "🇦🇶",
    "Antarctica/Syowa": "🇦🇶",
    "Antarctica/Troll": "🇦🇶",
    "Antarctica/Vostok": "🇦🇶",
    "Arctic/Longyearbyen": "🇸🇯",
    "Asia/Aden": "🇾🇪",
    "Asia/Almaty": "🇰🇿",
    "Asia/Amman": "🇯🇴",
    "Asia/Anadyr": "🇷🇺",
    "Asia/Aqtau": "🇰🇿",
    "Asia/Aqtobe": "🇰🇿",
    "Asia/Ashgabat": "🇹🇲",
    "Asia/Ashkhabad": "🇹🇲",
    "Asia/Atyrau": "🇰🇿",
    "Asia/Baghdad": "🇮🇶",
    "Asia/Bahrain": "🇧🇭",
    "Asia/Baku": "🇦🇿",
    "Asia/Bangkok": "🇹🇭",
    "Asia/Barnaul": "🇷🇺",
    "Asia/Beirut": "🇱🇧",
    "Asia/Bishkek": "🇰🇬",
    "Asia/Brunei": "🇧🇳",
    "Asia/Calcutta": "🇮🇳",
    "Asia/Chita": "🇷🇺",
    "Asia/Choibalsan": "🇲🇳",
    "Asia/Chongqing": "🇨🇳",
    "Asia/Chungking": "🇨🇳",
    "Asia/Colombo": "🇱🇰",
    "Asia/Dacca": "🇧🇩",
    "Asia/Damascus": "🇸🇾",
    "Asia/Dhaka": "🇧🇩",
    "Asia/Dili": "🇹🇱",
    "Asia/Dubai": "🇦🇪",
    "Asia/Dushanbe": "🇹🇯",
    "Asia/Famagusta": "🇨🇾",
    "Asia/Gaza": "🇵🇸",
    "Asia/Harbin": "🇨🇳",
    "Asia/Hebron": "🇵🇸",
    "Asia/Ho_Chi_Minh": "🇻🇳",
    "Asia/Hong_Kong": "🇭🇰",
    "Asia/Hovd": "🇲🇳",
    "Asia/Irkutsk": "🇷🇺",
    "Asia/Istanbul": "🇹🇷",
    "Asia/Jakarta": "🇮🇩",
    "Asia/Jayapura": "🇮🇩",
    "Asia/Jerusalem": "🇮🇱",
    "Asia/Kabul": "🇦🇫",
    "Asia/Kamchatka": "🇷🇺",
    "Asia/Karachi": "🇵🇰",
    "Asia/Kashgar": "🇨🇳",
    "Asia/Kathmandu": "🇳🇵",
    "Asia/Katmandu": "🇳🇵",
    "Asia/Khandyga": "🇷🇺",
    "Asia/Kolkata": "🇮🇳",
    "Asia/Krasnoyarsk": "🇷🇺",
    "Asia/Kuala_Lumpur": "🇲🇾",
    "Asia/Kuching": "🇲🇾",
    "Asia/Kuwait": "🇰🇼",
    "Asia/Macao": "🇲🇴",
    "Asia/Macau": "🇲🇴",
    "Asia/Magadan": "🇷🇺",
    "Asia/Makassar": "🇮🇩",
    "Asia/Manila": "🇵🇭",
    "Asia/Muscat": "🇴🇲",
    "Asia/Nicosia": "🇨🇾",
    "Asia/Novokuznetsk": "🇷🇺",
    "Asia/Novosibirsk": "🇷🇺",
    "Asia/Omsk": "🇷🇺",
    "Asia/Oral": "🇰🇿",
    "Asia/Phnom_Penh": "🇰🇭",
    "Asia/Pontianak": "🇮🇩",
    "Asia/Pyongyang": "🇰🇵",
    "Asia/Qatar": "🇶🇦",
    "Asia/Qostanay": "🇰🇿",
    "Asia/Qyzylorda": "🇰🇿",
    "Asia/Rangoon": "🇲🇲",
    "Asia/Riyadh": "🇸🇦",
    "Asia/Saigon": "🇻🇳",
    "Asia/Sakhalin": "🇷🇺",
    "Asia/Samarkand": "🇺🇿",
    "Asia/Seoul": "🇰🇷",
    "Asia/Shanghai": "🇨🇳",
    "Asia/Singapore": "🇸🇬",
    "Asia/Srednekolymsk": "🇷🇺",
    "Asia/Taipei": "🇹🇼",
    "Asia/Tashkent": "🇺🇿",
    "Asia/Tbilisi": "🇬🇪",
    "Asia/Tehran": "🇮🇷",
    "Asia/Tel_Aviv": "🇮🇱",
    "Asia/Thimbu": "🇧🇹",
    "Asia/Thimphu": "🇧🇹",
    "Asia/Tokyo": "🇯🇵",
    "Asia/Tomsk": "🇷🇺",
    "Asia/Ujung_Pandang": "🇮🇩",
    "Asia/Ulaanbaatar": "🇲🇳",
    "Asia/Ulan_Bator": "🇲🇳",
    "Asia/Urumqi": "🇨🇳",
    "Asia/Ust-Nera": "🇷🇺",
    "Asia/Vientiane": "🇱🇦",
    "Asia/Vladivostok": "🇷🇺",
    "Asia/Yakutsk": "🇷🇺",
    "Asia/Yangon": "🇲🇲",
    "Asia/Yekaterinburg": "🇷🇺",
    "Asia/Yerevan": "🇦🇲",
    "Atlantic/Azores": "🇵🇹",
    "Atlantic/Bermuda": "🇧🇲",
    "Atlantic/Canary": "🇪🇸",
    "Atlantic/Cape_Verde": "🇨🇻",
    "Atlantic/Faeroe": "🇫🇴",
    "Atlantic/Faroe": "🇫🇴",
    "Atlantic/Jan_Mayen": "🇸🇯",
    "Atlantic/Madeira": "🇵🇹",
    "Atlantic/Reykjavik": "🇮🇸",
    "Atlantic/South_Georgia": "🇬🇸",
    "Atlantic/St_Helena": "🇸🇭",
    "Atlantic/Stanley": "🇫🇰",
    "Australia/ACT": "🇦🇺",
    "Australia/Adelaide": "🇦🇺",
    "Australia/Brisbane": "🇦🇺",
    "Australia/Broken_Hill": "🇦🇺",
    "Australia/Canberra": "🇦🇺",
    "Australia/Currie": "🇦🇺",
    "Australia/Darwin": "🇦🇺",
    "Australia/Eucla": "🇦🇺",
    "Australia/Hobart": "🇦🇺",
    "Australia/LHI": "🇦🇺",
    "Australia/Lindeman": "🇦🇺",
    "Australia/Lord_Howe": "🇦🇺",
    "Australia/Melbourne": "🇦🇺",
    "Australia/North": "🇦🇺",
    "Australia/NSW": "🇦🇺",
    "Australia/Perth": "🇦🇺",
    "Australia/Queensland": "🇦🇺",
    "Australia/South": "🇦🇺",
    "Australia/Sydney": "🇦🇺",
    "Australia/Tasmania": "🇦🇺",
    "Australia/Victoria": "🇦🇺",
    "Australia/West": "🇦🇺",
    "Australia/Yancowinna": "🇦🇺",
    "Brazil/Acre": "🇧🇷",
    "Brazil/DeNoronha": "🇧🇷",
    "Brazil/East": "🇧🇷",
    "Brazil/West": "🇧🇷",
    "Canada/Atlantic": "🇨🇦",
    "Canada/Central": "🇨🇦",
    "Canada/Eastern": "🇨🇦",
    "Canada/Mountain": "🇨🇦",
    "Canada/Newfoundland": "🇨🇦",
    "Canada/Pacific": "🇨🇦",
    "Canada/Saskatchewan": "🇨🇦",
    "Canada/Yukon": "🇨🇦",
    "CET": "🇪🇺",
    "Chile/Continental": "🇨🇱",
    "Chile/EasterIsland": "🇨🇱",
    "CST6CDT": "🇨🇦",
    "Cuba": "🇨🇺",
    "EET": "🇪🇺",
    "Egypt": "🇪🇬",
    "Eire": "🇪🇺",
    "EST": "🇺🇸",
    "EST5EDT": "🇺🇸",
    "Etc/GMT": "",
    "Etc/GMT+0": "",
    "Etc/GMT+1": "",
    "Etc/GMT+10": "",
    "Etc/GMT+11": "",
    "Etc/GMT+12": "",
    "Etc/GMT+2": "",
    "Etc/GMT+3": "",
    "Etc/GMT+4": "",
    "Etc/GMT+5": "",
    "Etc/GMT+6": "",
    "Etc/GMT+7": "",
    "Etc/GMT+8": "",
    "Etc/GMT+9": "",
    "Etc/GMT0": "",
    "Etc/GMT-0": "",
    "Etc/GMT-1": "",
    "Etc/GMT-10": "",
    "Etc/GMT-11": "",
    "Etc/GMT-12": "",
    "Etc/GMT-13": "",
    "Etc/GMT-14": "",
    "Etc/GMT-2": "",
    "Etc/GMT-3": "",
    "Etc/GMT-4": "",
    "Etc/GMT-5": "",
    "Etc/GMT-6": "",
    "Etc/GMT-7": "",
    "Etc/GMT-8": "",
    "Etc/GMT-9": "",
    "Etc/Greenwich": "",
    "Etc/UCT": "",
    "Etc/Universal": "",
    "Etc/UTC": "",
    "Etc/Zulu": "",
    "Europe/Amsterdam": "🇳🇱",
    "Europe/Andorra": "🇦🇩",
    "Europe/Astrakhan": "🇷🇺",
    "Europe/Athens": "🇬🇷",
    "Europe/Belfast": "🇬🇧",
    "Europe/Belgrade": "🇷🇸",
    "Europe/Berlin": "🇩🇪",
    "Europe/Bratislava": "🇸🇰",
    "Europe/Brussels": "🇧🇪",
    "Europe/Bucharest": "🇷🇴",
    "Europe/Budapest": "🇭🇺",
    "Europe/Busingen": "🇩🇪",
    "Europe/Chisinau": "🇲🇩",
    "Europe/Copenhagen": "🇩🇰",
    "Europe/Dublin": "🇮🇪",
    "Europe/Gibraltar": "🇬🇮",
    "Europe/Guernsey": "🇬🇬",
    "Europe/Helsinki": "🇫🇮",
    "Europe/Isle_of_Man": "🇮🇲",
    "Europe/Istanbul": "🇹🇷",
    "Europe/Jersey": "🇯🇪",
    "Europe/Kaliningrad": "🇷🇺",
    "Europe/Kiev": "🇺🇦",
    "Europe/Kirov": "🇷🇺",
    "Europe/Lisbon": "🇵🇹",
    "Europe/Ljubljana": "🇸🇮",
    "Europe/London": "🇬🇧",
    "Europe/Luxembourg": "🇱🇺",
    "Europe/Madrid": "🇪🇸",
    "Europe/Malta": "🇲🇹",
    "Europe/Mariehamn": "🇦🇽",
    "Europe/Minsk": "🇧🇾",
    "Europe/Monaco": "🇲🇨",
    "Europe/Moscow": "🇷🇺",
    "Europe/Oslo": "🇳🇴",
    "Europe/Paris": "🇫🇷",
    "Europe/Podgorica": "🇲🇪",
    "Europe/Prague": "🇨🇿",
    "Europe/Riga": "🇱🇻",
    "Europe/Rome": "🇮🇹",
    "Europe/Samara": "🇷🇺",
    "Europe/San_Marino": "🇸🇲",
    "Europe/Sarajevo": "🇧🇦",
    "Europe/Saratov": "🇷🇺",
    "Europe/Simferopol": "🇺🇦",
    "Europe/Skopje": "🇲🇰",
    "Europe/Sofia": "🇧🇬",
    "Europe/Stockholm": "🇸🇪",
    "Europe/Tallinn": "🇪🇪",
    "Europe/Tirane": "🇦🇱",
    "Europe/Tiraspol": "🇲🇩",
    "Europe/Ulyanovsk": "🇷🇺",
    "Europe/Uzhgorod": "🇺🇦",
    "Europe/Vaduz": "🇱🇮",
    "Europe/Vatican": "🇻🇦",
    "Europe/Vienna": "🇦🇹",
    "Europe/Vilnius": "🇱🇹",
    "Europe/Volgograd": "🇷🇺",
    "Europe/Warsaw": "🇵🇱",
    "Europe/Zagreb": "🇭🇷",
    "Europe/Zaporozhye": "🇺🇦",
    "Europe/Zurich": "🇨🇭",
    "GB": "🇬🇧",
    "GB-Eire": "🇬🇧",
    "GMT": "🇬🇧",
    "GMT+0": "🇬🇧",
    "GMT0": "🇬🇧",
    "GMT-0": "🇬🇧",
    "Greenwich": "🇬🇧",
    "Hongkong": "🇭🇰",
    "HST": "🇺🇸",
    "Iceland": "🇮🇸",
    "Indian/Antananarivo": "🇲🇬",
    "Indian/Chagos": "🇮🇴",
    "Indian/Christmas": "🇨🇽",
    "Indian/Cocos": "🇨🇨",
    "Indian/Comoro": "🇰🇲",
    "Indian/Kerguelen": "🇹🇫",
    "Indian/Mahe": "🇸🇨",
    "Indian/Maldives": "🇲🇻",
    "Indian/Mauritius": "🇲🇺",
    "Indian/Mayotte": "🇾🇹",
    "Indian/Reunion": "🇷🇪",
    "Iran": "🇮🇷",
    "Israel": "🇮🇱",
    "Jamaica": "🇯🇲",
    "Japan": "🇯🇵",
    "Kwajalein": "🇲🇭",
    "Libya": "🇱🇾",
    "MET": "🇪🇺",
    "Mexico/BajaNorte": "🇲🇽",
    "Mexico/BajaSur": "🇲🇽",
    "Mexico/General": "🇲🇽",
    "MST": "🇺🇸",
    "MST7MDT": "🇺🇸",
    "Navajo": "🇺🇸",
    "NZ": "🇳🇿",
    "NZ-CHAT": "🇳🇿",
    "Pacific/Apia": "🇼🇸",
    "Pacific/Auckland": "🇳🇿",
    "Pacific/Bougainville": "🇵🇬",
    "Pacific/Chatham": "🇳🇿",
    "Pacific/Chuuk": "🇫🇲",
    "Pacific/Easter": "🇨🇱",
    "Pacific/Efate": "🇻🇺",
    "Pacific/Enderbury": "🇰🇮",
    "Pacific/Fakaofo": "🇹🇰",
    "Pacific/Fiji": "🇫🇯",
    "Pacific/Funafuti": "🇹🇻",
    "Pacific/Galapagos": "🇪🇨",
    "Pacific/Gambier": "🇵🇫",
    "Pacific/Guadalcanal": "🇸🇧",
    "Pacific/Guam": "🇬🇺",
    "Pacific/Honolulu": "🇺🇸",
    "Pacific/Johnston": "🇺🇲",
    "Pacific/Kiritimati": "🇰🇮",
    "Pacific/Kosrae": "🇫🇲",
    "Pacific/Kwajalein": "🇲🇭",
    "Pacific/Majuro": "🇲🇭",
    "Pacific/Marquesas": "🇵🇫",
    "Pacific/Midway": "🇺🇲",
    "Pacific/Nauru": "🇳🇷",
    "Pacific/Niue": "🇳🇺",
    "Pacific/Norfolk": "🇳🇫",
    "Pacific/Noumea": "🇳🇨",
    "Pacific/Pago_Pago": "🇦🇸",
    "Pacific/Palau": "🇵🇼",
    "Pacific/Pitcairn": "🇵🇳",
    "Pacific/Pohnpei": "🇫🇲",
    "Pacific/Ponape": "🇫🇲",
    "Pacific/Port_Moresby": "🇵🇬",
    "Pacific/Rarotonga": "🇨🇰",
    "Pacific/Saipan": "🇲🇵",
    "Pacific/Samoa": "🇼🇸",
    "Pacific/Tahiti": "🇵🇫",
    "Pacific/Tarawa": "🇰🇮",
    "Pacific/Tongatapu": "🇹🇴",
    "Pacific/Truk": "🇫🇲",
    "Pacific/Wake": "🇺🇲",
    "Pacific/Wallis": "🇼🇫",
    "Pacific/Yap": "🇫🇲",
    "Poland": "🇵🇱",
    "Portugal": "🇵🇹",
    "PRC": "🇨🇳",
    "PST8PDT": "🇮🇳",
    "ROC": "🇹🇼",
    "ROK": "🇰🇷",
    "Singapore": "🇸🇬",
    "Turkey": "🇹🇷",
    "UCT": "",
    "Universal": "",
    "US/Alaska": "🇺🇸",
    "US/Aleutian": "🇺🇸",
    "US/Arizona": "🇺🇸",
    "US/Central": "🇺🇸",
    "US/Eastern": "🇺🇸",
    "US/East-Indiana": "🇺🇸",
    "US/Hawaii": "🇺🇸",
    "US/Indiana-Starke": "🇺🇸",
    "US/Michigan": "🇺🇸",
    "US/Mountain": "🇺🇸",
    "US/Pacific": "🇺🇸",
    "US/Pacific-New": "🇺🇸",
    "US/Samoa": "🇺🇸",
    "UTC": "",
    "WET": "🇷🇺",
    "W-SU": "",
    "Zulu": ""
}


def timezone():
    global timezones
    local_zone = os.path.realpath('/etc/localtime')
    for key, value in timezones.items():
        if local_zone.endswith(key):
            return value


def local_time():
    return "{} {}".format(time.strftime('%m-%d %H:%M:%S'), timezone())


async def main(connection):
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    component = iterm2.StatusBarComponent(
        short_description="Enhanced Time",
        detailed_description="Display current tme with extra information",
        knobs=[],
        exemplar=local_time(),
        update_cadence=1,
        identifier="catj.moe.localtime",
        icons=[icon1x, icon2x])

    @iterm2.StatusBarRPC
    async def localtime(knobs):
        return local_time()

    # Register the component.
    await component.async_register(connection, localtime)


iterm2.run_forever(main)