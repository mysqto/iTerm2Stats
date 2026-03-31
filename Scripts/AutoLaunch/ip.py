#!/usr/bin/env python3
import asyncio
import json
import psutil
import socket
import urllib.error
import urllib.request
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Tuple

import iterm2

from psutil._common import bytes2human

af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}

duplex_map = {
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_UNKNOWN: "?",
}

# The name of the iTerm2 variable to store the result
VARIABLE = "external_ip"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
USER_AGENT_BROWSER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

service_url = "https://ipinfo.io/json"
update_interval = 120
country_keys = ["country", "country_iso"]

# Media streaming cache configuration
MEDIA_CACHE_INTERVAL = 300  # 5 minutes
media_cache = {}
media_cache_lock = asyncio.Lock()
last_media_check = 0

# Icons
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA7klEQVQ4jbWRvWpCQRCFP41I/AGfwoi+gNhYqm2w0kdIE6K+xu3FxjdIiJU2VlaKXWoLk0K0s1TBsDADA9l7vSk8MHDYPefM7gz3Qhf4BH6kHO/E6ZUX8TWkJqIJxSzCrDUNM7eN6Eue7vhaOm/M/bMv4MMInoCB8CzQAErAXM7e1ZQ0AWXDM0BaeAHoAXv5okPFF2D5CbgIPwIv8sW+nCVUmDKmFVA023gUngPGQN1ol74Z1MwMDtLZ8Z1nE1VfgEMQY41BmFkxijAPb5kVbzJENTr+GtesaJmA5n/Nim9gGyV4uBFwBhay4r8AfgFM5lUYQdNtmQAAAABJRU5ErkJggg=="
ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABnUlEQVRIieXWu2sVQRTH8c8VX7cwV9OZhKRNwETEv0B7NZW1IKQSsQwG/xY7TRHCRUEU/wNFfICojRZaJFgkNqYxXIudhWUzN87s3cQiPziwc+bxPfM6sxw1dTLajmMR1zGLqeD/gU94gj622gquixX8wuAfto37oc9ImsCrBGDd3mK6KXRKsYy50NK+YzIX2sWbEaClvcbpHPCDFqClLadCx6UdpFTbxrk65FgEvIixiL8TbKfi61X8JzCPZ7V+PdzYf66F+kMiL/W74isDvIObYSJdfKv1XU8Bf2kA3gjla6H8sNb3cx0SW+rzKdFFtKO4QnC2VjeROkDujGdwJnxfiIxRPRfgeAS8GQbK0YJilhexZO/d3UgZZF3zPR5ma3VIbI9XU6LL1OOURqfwU3sJZBMnUyO83SL4ViqUIhO9bAH6XN7PBoqD834E6EeRHJ2qSXxoAH0nMWnspx6eZkD74o9MI3Vwz/CsNlDc77sa7GmK5ux9eQb4GuoOVJexW4H+waWDhpZarYAfHRYUrlbAVw4T3MELDRPEf9Vfh9wnPhAHcssAAAAASUVORK5CYII="

FLAGS_OFFSET = 127397
A = 65
Z = 90


def emoji(country):
    first = ord(country[0])
    second = ord(country[1])
    if (len(country) != 2) or (first > Z or first < A) or (second > Z or second < A):
        return country
    return chr(first + FLAGS_OFFSET) + chr(second + FLAGS_OFFSET)


# ============ Media Streaming Checkers ============

def check_with_timeout(url, method='GET', headers=None, data=None, timeout=8):
    """Make HTTP request with timeout and handle gzip compression"""
    import gzip
    try:
        req_headers = {
            'User-Agent': USER_AGENT_BROWSER,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        if headers:
            req_headers.update(headers)
        
        request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_data = response.read()
            # Check if response is gzip compressed
            if response.info().get('Content-Encoding') == 'gzip':
                raw_data = gzip.decompress(raw_data)
            return raw_data.decode('utf-8', errors='ignore'), response.status
    except urllib.error.HTTPError as e:
        raw_data = e.read()
        # Try to decompress error response if gzipped
        try:
            if e.headers.get('Content-Encoding') == 'gzip':
                raw_data = gzip.decompress(raw_data)
        except:
            pass
        return raw_data.decode('utf-8', errors='ignore'), e.code
    except Exception:
        return None, 0


def check_netflix() -> Tuple[str, str]:
    """Check Netflix availability"""
    try:
        # Check with a specific title
        content, code = check_with_timeout('https://www.netflix.com/title/81280792', headers={
            'Cookie': 'OptanonConsent=isGpcEnabled=0'
        })
        if not content:
            return "Netflix", "Failed"
        
        # Check for blocking messages
        if "Oh no!" in content or "Not Available" in content:
            return "Netflix", "Originals Only"
        
        # Extract region
        import re
        match = re.search(r'data-country="([A-Z]{2})"', content)
        if match:
            region = match.group(1)
            return "Netflix", f"Yes {emoji(region)} ({region})"
        
        # Try to find region in other places
        match = re.search(r'"currentCountry":"([A-Z]{2})"', content)
        if match:
            region = match.group(1)
            return "Netflix", f"Yes {emoji(region)} ({region})"
        
        return "Netflix", "Yes"
    except Exception:
        return "Netflix", "Failed"


def check_youtube_premium() -> Tuple[str, str]:
    """Check YouTube Premium availability"""
    try:
        content, code = check_with_timeout('https://www.youtube.com/premium', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content:
            return "YouTube Premium", "Failed"
        
        if 'Premium is not available' in content:
            return "YouTube Premium", "No"
        
        # Extract region
        import re
        match = re.search(r'"INNERTUBE_CONTEXT_GL":"([A-Z]{2})"', content)
        region = match.group(1) if match else "Unknown"
        
        if 'ad-free' in content.lower() or 'premium' in content.lower():
            if region != "Unknown":
                return "YouTube Premium", f"Yes {emoji(region)} ({region})"
            return "YouTube Premium", "Yes"
        
        return "YouTube Premium", "No"
    except Exception:
        return "YouTube Premium", "Failed"


def check_disney_plus() -> Tuple[str, str]:
    """Check Disney+ Region"""
    try:
        content, code = check_with_timeout('https://www.disneyplus.com/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content:
            return "Disney+", "Failed"
        
        # Check for unavailable messages
        if 'preview' in content.lower() or 'unavailable' in content.lower():
            return "Disney+", "No"
        
        import re
        # Try multiple patterns to extract region
        match = re.search(r'"countryCode"\s*:\s*"([A-Z]{2})"', content)
        if not match:
            match = re.search(r'"region"\s*:\s*"([A-Z]{2})"', content)
        if not match:
            match = re.search(r'Region:\s*([A-Z]{2})', content)
        
        if match:
            region = match.group(1)
            if region and len(region) == 2:
                return "Disney+", f"Yes {emoji(region)} ({region})"
        
        # If we got 200 but no region, still consider it available
        if code == 200:
            return "Disney+", "Yes"
        
        return "Disney+", "No"
    except Exception:
        return "Disney+", "Failed"


def check_dazn() -> Tuple[str, str]:
    """Check Dazn availability"""
    try:
        data = json.dumps({"Version":"2","LandingPageKey":"generic","Languages":"en-US","Platform":"web","Manufacturer":"","PromoCode":"","PlatformAttributes":{}}).encode()
        content, code = check_with_timeout(
            'https://startup.core.indazn.com/misl/v5/Startup',
            method='POST',
            headers={
                'content-type': 'application/json',
                'origin': 'https://www.dazn.com',
                'referer': 'https://www.dazn.com/'
            },
            data=data
        )
        
        if not content:
            return "Dazn", "Failed"
        
        if "Security policy has been breached" in content:
            return "Dazn", "IP Banned"
        
        # Parse JSON response
        try:
            data_obj = json.loads(content)
            # Check if allowed
            is_allowed = data_obj.get('Region', {}).get('isAllowed', False)
            region = data_obj.get('Region', {}).get('GeolocatedCountry', '')
            
            if is_allowed:
                if region and len(region) == 2:
                    return "Dazn", f"Yes {emoji(region)} ({region})"
                return "Dazn", "Yes"
        except json.JSONDecodeError:
            # Fallback to regex parsing
            import re
            allowed = re.search(r'"isAllowed":\s*(true|false)', content)
            region_match = re.search(r'"GeolocatedCountry"\s*:\s*"([A-Z]{2})"', content)
            
            if allowed and allowed.group(1) == 'true':
                if region_match:
                    region = region_match.group(1)
                    return "Dazn", f"Yes {emoji(region)} ({region})"
                return "Dazn", "Yes"
        
        return "Dazn", "No"
    except Exception:
        return "Dazn", "Failed"


def check_amazon_prime() -> Tuple[str, str]:
    """Check Amazon Prime Video availability"""
    try:
        content, code = check_with_timeout('https://www.primevideo.com', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content:
            return "Amazon Prime Video", "Failed"
        
        if 'isServiceRestricted' in content:
            return "Amazon Prime Video", "No"
        
        import re
        match = re.search(r'"currentTerritory":"([A-Z]{2})"', content)
        if match:
            region = match.group(1)
            return "Amazon Prime Video", f"Yes {emoji(region)} ({region})"
        
        return "Amazon Prime Video", "Yes"
    except Exception:
        return "Amazon Prime Video", "Failed"


def check_tiktok() -> Tuple[str, str]:
    """Check TikTok Region"""
    try:
        content, code = check_with_timeout('https://www.tiktok.com/', headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content or code != 200:
            return "TikTok", "Failed"
        
        import re
        match = re.search(r'"region":"([A-Z]{2})"', content)
        if match:
            region = match.group(1)
            if region != 'Unknown':
                return "TikTok", f"Yes {emoji(region)} ({region})"
        
        return "TikTok", "No"
    except Exception:
        return "TikTok", "Failed"


def check_tvb_anywhere() -> Tuple[str, str]:
    """Check TVBAnywhere+ availability"""
    try:
        content, code = check_with_timeout('https://uapisfm.tvbanywhere.com.sg/geoip/check/platform/android', headers={
            'Accept': 'application/json'
        })
        if not content:
            return "TVBAnywhere+", "Failed"
        
        try:
            data = json.loads(content)
            country_code = data.get('country_code', '')
            if data.get('allow_in_this_location') or country_code in ['HK', 'TW', 'SG']:
                if country_code and len(country_code) == 2:
                    return "TVBAnywhere+", f"Yes {emoji(country_code)} ({country_code})"
                return "TVBAnywhere+", "Yes"
        except:
            pass
        
        return "TVBAnywhere+", "No"
    except Exception:
        return "TVBAnywhere+", "Failed"


def check_iqiyi() -> Tuple[str, str]:
    """Check iQiyi Oversea Region"""
    try:
        content, code = check_with_timeout('https://www.iq.com/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content or code != 200:
            return "iQyi Oversea Region", "Failed"
        
        import re
        # Try multiple patterns
        match = re.search(r'__NEXT_DATA__.*?"region_code":"([^"]+)"', content, re.DOTALL)
        if not match:
            match = re.search(r'"region_code"\s*:\s*"([^"]+)"', content)
        if not match:
            match = re.search(r'data-locale="[a-z]{2}_([A-Z]{2})"', content)
        
        if match:
            region = match.group(1).upper()
            # Handle special cases
            if region == 'NTW':
                region = 'TW'
            if region and len(region) == 2:
                return "iQyi Oversea Region", f"{emoji(region)} ({region})"
            return "iQyi Oversea Region", region
        
        return "iQyi Oversea Region", "Unknown"
    except Exception:
        return "iQyi Oversea Region", "Failed"


def check_youtube_cdn() -> Tuple[str, str]:
    """Check YouTube CDN location"""
    try:
        content, code = check_with_timeout('https://redirector.googlevideo.com/report_mapping')
        if content and code == 200:
            # Extract ISP info from response
            return "YouTube CDN", "Available"
        return "YouTube CDN", "Unknown"
    except Exception:
        return "YouTube CDN", "Failed"


def check_netflix_cdn() -> Tuple[str, str]:
    """Check Netflix Preferred CDN"""
    try:
        content, code = check_with_timeout('https://api.fast.com/netflix/speedtest/v2?https=true&token=YXNkZmFzZGxmbnNkYWZoYXNkZmhrYWxm&urlCount=1', headers={
            'Accept': 'application/json'
        })
        if not content or code != 200:
            return "Netflix Preferred CDN", "Failed"
        
        try:
            data = json.loads(content)
            if data and isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if not isinstance(first_item, dict):
                    return "Netflix Preferred CDN", "Unknown"
                
                url = first_item.get('url', '')
                location_data = first_item.get('location', {})
                location_name = ''
                
                if isinstance(location_data, dict):
                    location_name = location_data.get('city', '')
                
                import re
                # Extract CDN domain
                if url:
                    match = re.search(r'https?://([^/]+)', url)
                    cdn_host = match.group(1) if match else ''
                    
                    # Try to get ISP/location info
                    if cdn_host:
                        # Extract meaningful part of hostname
                        parts = cdn_host.split('.')
                        if len(parts) > 2:
                            cdn_name = parts[-3] if parts[-3] not in ['com', 'net', 'org'] else parts[-2]
                        else:
                            cdn_name = parts[0]
                        
                        if location_name:
                            return "Netflix Preferred CDN", f"{cdn_name.upper()} in {location_name}"
                        return "Netflix Preferred CDN", cdn_host
        except Exception as e:
            # Silently fail - don't print error in production
            pass
        
        return "Netflix Preferred CDN", "Unknown"
    except Exception:
        return "Netflix Preferred CDN", "Failed"


def check_spotify() -> Tuple[str, str]:
    """Check Spotify Registration"""
    try:
        data = "birth_day=11&birth_month=11&birth_year=2000&collect_personal_info=undefined&creation_flow=&creation_point=https%3A%2F%2Fwww.spotify.com%2Fhk-en%2F&displayname=Gay%20Lord&gender=male&iagree=1&key=a1e486e2729f46d6bb368d6b2bcda326&platform=www&referrer=&send-email=0&thirdpartyemail=0&identifier_token=AgE6YTvEzkReHNfJpO114514".encode()
        content, code = check_with_timeout(
            'https://spclient.wg.spotify.com/signup/public/v1/account',
            method='POST',
            headers={
                'Accept-Language': 'en',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=data
        )
        
        if not content:
            return "Spotify Registration", "Failed"
        
        try:
            result = json.loads(content)
            status_code = result.get('status')
            region = result.get('country', 'Unknown')
            is_launched = result.get('is_country_launched')
            
            # Status 320 or 120 means not available
            if status_code in [320, 120]:
                return "Spotify Registration", "No"
            
            # Check if country is launched
            if is_launched == False:
                return "Spotify Registration", "No"
            
            # Status 311 means available
            if status_code == 311:
                if region and region != 'Unknown':
                    return "Spotify Registration", f"Yes {emoji(region)} ({region})"
                return "Spotify Registration", "Yes"
        except:
            pass
        
        return "Spotify Registration", "Failed"
    except Exception:
        return "Spotify Registration", "Failed"


def check_chatgpt() -> Tuple[str, str]:
    """Check ChatGPT availability and region"""
    try:
        # First check the main page to see if we're blocked
        content, code = check_with_timeout('https://chat.openai.com/', headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        
        # 403/451 means blocked
        if code in [403, 451]:
            return "ChatGPT", "No"
        
        # Check for unsupported_country or VPN detection
        if content:
            if 'unsupported_country' in content.lower() or 'not available' in content.lower():
                return "ChatGPT", "No"
            if 'vpn' in content.lower():
                return "ChatGPT", "No (VPN Detected)"
        
        # Network failure
        if code == 0:
            return "ChatGPT", "Failed"
        
        # If we got here, check the CDN endpoint to get region
        cdn_content, cdn_code = check_with_timeout('https://ios.chat.openai.com/', headers={
            'Accept': '*/*'
        })
        
        if cdn_content:
            import re
            # Try to extract country code from various locations
            match = re.search(r'"country":\s*"([A-Z]{2})"', cdn_content)
            if not match:
                match = re.search(r'country["\s:]+([A-Z]{2})', cdn_content)
            if not match:
                match = re.search(r'"country_code":\s*"([A-Z]{2})"', cdn_content)
            
            if match:
                region = match.group(1)
                return "ChatGPT", f"Yes {emoji(region)} ({region})"
        
        # If available but no region detected
        if code == 200 or code in [301, 302, 307, 308]:
            return "ChatGPT", "Yes"
        
        return "ChatGPT", f"Unknown ({code})"
    except Exception:
        return "ChatGPT", "Failed"


def check_gemini() -> Tuple[str, str]:
    """Check Gemini AI availability and region"""
    try:
        content, code = check_with_timeout('https://gemini.google.com/', headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        if not content:
            return "Gemini", "Failed"
        
        if code == 403:
            return "Gemini", "No"
        
        if code == 200:
            import re
            # Try multiple patterns to extract region
            # Pattern 1: gl parameter (Google Location)
            match = re.search(r'"gl"\s*:\s*"([A-Z]{2})"', content)
            if not match:
                # Pattern 2: country code
                match = re.search(r'"country"\s*:\s*"([A-Z]{2})"', content)
            if not match:
                # Pattern 3: countryCode
                match = re.search(r'"countryCode"\s*:\s*"([A-Z]{2})"', content)
            if not match:
                # Pattern 4: data-country attribute
                match = re.search(r'data-country="([A-Z]{2})"', content)
            if not match:
                # Pattern 5: hl parameter (might indicate region)
                match = re.search(r'"hl"\s*:\s*"[a-z]{2}-([A-Z]{2})"', content)
            
            if match:
                region = match.group(1)
                return "Gemini", f"Yes {emoji(region)} ({region})"
            
            return "Gemini", "Yes"
        
        return "Gemini", "Unknown"
    except Exception:
        return "Gemini", "Failed"


def check_bing_region() -> Tuple[str, str]:
    """Check Bing Region"""
    try:
        content, code = check_with_timeout('https://www.bing.com/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content:
            return "Bing Region", "Failed"
        
        import re
        match = re.search(r'Region:"([^"]+)"', content)
        if not match:
            match = re.search(r'"Market":"([a-z]{2}-[A-Z]{2})"', content)
            if match:
                market = match.group(1)
                region = market.split('-')[1] if '-' in market else market
                if region and len(region) == 2:
                    return "Bing Region", f"{emoji(region)} {region}"
        
        if match:
            region = match.group(1)
            if len(region) == 2:
                return "Bing Region", f"{emoji(region)} {region}"
            return "Bing Region", region
        
        return "Bing Region", "Unknown"
    except Exception:
        return "Bing Region", "Failed"


def check_wikipedia() -> Tuple[str, str]:
    """Check Wikipedia Editability"""
    try:
        content, code = check_with_timeout('https://www.wikipedia.org/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if code == 200:
            return "Wikipedia Editability", "Yes"
        return "Wikipedia Editability", "Unknown"
    except Exception:
        return "Wikipedia Editability", "Failed"


def check_instagram_audio() -> Tuple[str, str]:
    """Check Instagram Music/Audio"""
    try:
        content, code = check_with_timeout('https://www.instagram.com/instagram/channel/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content:
            return "Instagram Audio", "Failed"
        
        # Instagram blocks audio in certain regions
        if 'music is not available' in content.lower() or 'audio not available' in content.lower():
            return "Instagram Audio", "No"
        elif code == 200:
            # Try to extract region if available
            import re
            match = re.search(r'"country_code":"([A-Z]{2})"', content)
            if match:
                region = match.group(1)
                return "Instagram Audio", f"Yes {emoji(region)} ({region})"
            return "Instagram Audio", "Yes"
        
        return "Instagram Audio", "Unknown"
    except Exception:
        return "Instagram Audio", "Failed"


def check_reddit() -> Tuple[str, str]:
    """Check Reddit Access"""
    try:
        content, code = check_with_timeout('https://www.reddit.com/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content:
            return "Reddit", "Failed"
        
        if code == 200:
            # Try to extract region/locale if available
            import re
            match = re.search(r'"locale":"([a-z]{2}_[A-Z]{2})"', content)
            if match:
                locale = match.group(1)
                region = locale.split('_')[1] if '_' in locale else None
                if region:
                    return "Reddit", f"Yes {emoji(region)} ({region})"
            return "Reddit", "Yes"
        elif code == 403:
            return "Reddit", "No"
        
        return "Reddit", "Unknown"
    except Exception:
        return "Reddit", "Failed"


def check_steam_currency() -> Tuple[str, str]:
    """Check Steam Currency"""
    try:
        # Use store homepage which has currency info
        content, code = check_with_timeout('https://store.steampowered.com/', headers={
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if not content or code != 200:
            return "Steam Currency", "Failed"
        
        import re
        # Try to get currency from various locations
        # Pattern 1: wallet_currency
        currency_match = re.search(r'"wallet_currency"\s*:\s*"([^"]+)"', content)
        if not currency_match:
            # Pattern 2: sCurrencyCode
            currency_match = re.search(r'"sCurrencyCode"\s*:\s*"([^"]+)"', content)
        if not currency_match:
            # Pattern 3: data-currency
            currency_match = re.search(r'data-currency="([^"]+)"', content)
        
        # Try to get country
        country_match = re.search(r'"sClientCountry"\s*:\s*"([A-Z]{2})"', content)
        if not country_match:
            country_match = re.search(r'data-country="([A-Z]{2})"', content)
        
        if currency_match:
            currency = currency_match.group(1).upper()
            if country_match:
                region = country_match.group(1).upper()
                return "Steam Currency", f"{currency} {emoji(region)} ({region})"
            return "Steam Currency", currency
        
        return "Steam Currency", "Unknown"
    except Exception:
        return "Steam Currency", "Failed"


# List of all checkers
MEDIA_CHECKERS = [
    check_dazn,
    check_tiktok,
    check_disney_plus,
    check_netflix,
    check_youtube_premium,
    check_amazon_prime,
    check_tvb_anywhere,
    check_iqiyi,
    check_youtube_cdn,
    check_netflix_cdn,
    check_spotify,
    check_chatgpt,
    check_gemini,
    check_bing_region,
    check_wikipedia,
    check_instagram_audio,
    check_reddit,
    check_steam_currency,
]


async def check_all_media_services():
    """Check all media services in parallel"""
    global media_cache, last_media_check
    
    async with media_cache_lock:
        current_time = time.time()
        
        # Return cached results if still valid
        if media_cache and (current_time - last_media_check) < MEDIA_CACHE_INTERVAL:
            return media_cache
        
        # Run all checks in parallel using ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [loop.run_in_executor(executor, checker) for checker in MEDIA_CHECKERS]
            results = await asyncio.gather(*futures, return_exceptions=True)
        
        # Process results
        media_cache = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                service, status = result
                media_cache[service] = status
            elif isinstance(result, Exception):
                print(f"Error checking service: {result}")
        
        last_media_check = current_time
        return media_cache


# ============ Network Info Functions ============

async def get_external_ip():
    try:
        request = urllib.request.Request(service_url, data=None,
                                         headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(request) as response:
            resp = response.read().decode("utf-8").strip()
            obj = json.loads(resp)
            ip = obj["ip"]
            country = '🌍'
            for country_key in country_keys:
                if country_key in obj and len(obj[country_key]) == 2:
                    country = obj[country_key]
                    break
            return '{}|{}'.format(ip, emoji(country))
    except (urllib.error.HTTPError, urllib.error.URLError, TypeError):
        return '{}|{}'.format(local_ip(), '📶')


def local_ip():
    unfiltered_addresses = psutil.net_if_addrs()
    for interface, addresses in unfiltered_addresses.items():
        if interface.startswith('en'):
            return addresses[0].address
    return socket.gethostbyname(socket.gethostname())


def ifconfig(text_color="inherit", bg_color="inherit"):
    import io
    out = io.StringIO()
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    print(f'<style>pre {{font-family: Menlo,monospace; font-size: 12px; color: {text_color} !important; background-color: {bg_color} !important; margin: 0; padding: 0; white-space: pre-wrap;}}</style>', file=out)
    print("<pre>", file=out)
    for nic, addrs in psutil.net_if_addrs().items():
        print("%s:" % (nic), file=out)
        if nic in stats:
            st = stats[nic]
            print("    stats          : ", end='', file=out)
            print("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                st.speed, duplex_map[st.duplex], st.mtu,
                "yes" if st.isup else "no"), file=out)
        if nic in io_counters:
            io = io_counters[nic]
            print("    incoming       : ", end='', file=out)
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin), file=out)
            print("    outgoing       : ", end='', file=out)
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout), file=out)
        for addr in addrs:
            if not addr.address or addr.address.startswith('fe80::'):
                continue
            print("    %-4s" % af_map.get(addr.family, addr.family), end="", file=out)
            print(" address   : %s" % addr.address, file=out)
            if addr.broadcast:
                print("       broadcast   : %s" % addr.broadcast, file=out)
            if addr.netmask:
                print("         netmask   : %s" % addr.netmask, file=out)
            if addr.ptp:
                print("             p2p   : %s" % addr.ptp, file=out)
        print("", file=out)
    print("</pre>", file=out)
    result = out.getvalue()
    out.close()
    return result


async def external_ip_task(app):
    while True:
        if not service_url:
            await asyncio.sleep(1)
        global update_interval
        text = "Loading"
        try:
            text = await get_external_ip()
        except:
            text = "Loading"
        if text:
            await app.async_set_variable("user." + VARIABLE, text)
            await asyncio.sleep(update_interval)
        else:
            await asyncio.sleep(5)


async def media_check_task():
    """Background task to periodically check media services"""
    while True:
        try:
            print("Starting media services check...")
            await check_all_media_services()
            await asyncio.sleep(MEDIA_CACHE_INTERVAL)
        except Exception as e:
            print(f"Error in media check task: {e}")
            await asyncio.sleep(60)


async def main(connection):
    app = await iterm2.async_get_app(connection)
    
    # Start background tasks
    asyncio.create_task(external_ip_task(app))
    asyncio.create_task(media_check_task())
 
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    update_interval_knob = "ip_update_interval"
    service_url_knob = "ip_provider_url"
    knobs = [iterm2.StringKnob("Update Interval", "60", "60", update_interval_knob),
             iterm2.StringKnob("Provider URL", "https://ifconfig.co/json", "https://ifconfig.co/json",
                               service_url_knob)]

    # Register the status bar component
    component = iterm2.StatusBarComponent(
        short_description="External IP",
        detailed_description="Shows public IP address and streaming service availability",
        knobs=knobs,
        exemplar=local_ip(),
        update_cadence=None,
        identifier="catj.moe.ip",
        icons=[icon1x, icon2x])

    @iterm2.RPC
    async def onclick(session_id):
        session = app.get_session_by_id(session_id)
        
        # Get colors from profile
        profile = await session.async_get_profile()
        background_color = profile.background_color
        bg_color_css = f"rgba({int(background_color.red)}, {int(background_color.green)}, {int(background_color.blue)}, {background_color.alpha})"
        text_red = 255 - int(background_color.red)
        text_green = 255 - int(background_color.green)
        text_blue = 255 - int(background_color.blue)
        text_color_css = f"rgb({text_red}, {text_green}, {text_blue})"

        # Get cached media results (or check if cache is empty)
        media_results = await check_all_media_services()
        
        # Build media table with custom ordering
        # Define desired order (Netflix and Netflix CDN should be together)
        service_order = [
            "Netflix", "Netflix Preferred CDN",
            "YouTube Premium", "YouTube CDN",
            "Amazon Prime Video",
            "Disney+",
            "Dazn",
            "Spotify",
            "TikTok",
            "TVBAnywhere+",
            "iQyi Oversea Region",
            "ChatGPT",
            "Gemini",
            "Bing Region",
            "Wikipedia Editability",
            "Instagram Audio",
            "Reddit",
            "Steam Currency"
        ]
        
        # Sort by custom order, putting unknown services at the end
        def service_sort_key(item):
            service_name = item[0]
            try:
                return service_order.index(service_name)
            except ValueError:
                return len(service_order)  # Put unknown services at the end
        
        sorted_services = sorted(media_results.items(), key=service_sort_key)
        
        media_html = '<table style="width: 100%; border-collapse: collapse;">'
        media_html += '<thead><tr>'
        media_html += f'<th style="text-align: left; padding: 8px; border-bottom: 2px solid {text_color_css}; color: {text_color_css};">Service</th>'
        media_html += f'<th style="text-align: left; padding: 8px; border-bottom: 2px solid {text_color_css}; color: {text_color_css};">Status</th>'
        media_html += '</tr></thead><tbody>'
        
        for service, status in sorted_services:
            # Color code status
            if "Yes" in status:
                status_color = "#4CAF50"  # Green
            elif "No" in status or "Failed" in status:
                status_color = "#F44336"  # Red
            else:
                status_color = text_color_css
            
            media_html += '<tr>'
            media_html += f'<td style="padding: 6px 8px; color: {text_color_css};">{service}</td>'
            media_html += f'<td style="padding: 6px 8px; color: {status_color}; font-weight: 500;">{status}</td>'
            media_html += '</tr>'
        
        media_html += '</tbody></table>'
        
        # Get network info
        ifconfig_content = ifconfig(text_color_css, bg_color_css)
        
        # Build complete HTML with tabs
        html_content = f"""
        <html style="margin: 0; padding: 0; background-color: {bg_color_css}; width: 100%; height: 100%; border-radius: 8px; overflow: hidden;">
        <head>
            <style>
                html, body {{
                    margin: 0 !important;
                    padding: 0 !important;
                    background-color: {bg_color_css} !important;
                    color: {text_color_css} !important;
                    width: 100% !important;
                    height: 100% !important;
                    border-radius: 8px !important;
                    overflow: hidden !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', monospace;
                }}
                
                .container {{
                    padding: 10px;
                    height: 100%;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;
                }}
                
                .tabs {{
                    display: flex;
                    border-bottom: 2px solid {text_color_css};
                    margin-bottom: 10px;
                }}
                
                .tab {{
                    padding: 10px 20px;
                    cursor: pointer;
                    background-color: transparent;
                    color: {text_color_css};
                    border: none;
                    border-bottom: 3px solid transparent;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.2s;
                }}
                
                .tab:hover {{
                    opacity: 0.7;
                }}
                
                .tab.active {{
                    border-bottom-color: {text_color_css};
                    font-weight: 600;
                }}
                
                .tab-content {{
                    display: none;
                    flex: 1;
                    overflow: auto;
                }}
                
                .tab-content.active {{
                    display: block;
                }}
                
                table {{
                    width: 100% !important;
                    background-color: transparent !important;
                    color: {text_color_css} !important;
                    border-collapse: collapse;
                    font-size: 12px;
                }}
                
                th {{
                    text-align: left;
                    padding: 8px !important;
                    border-bottom: 2px solid {text_color_css};
                    color: {text_color_css} !important;
                    font-weight: 600;
                    background-color: transparent !important;
                }}
                
                td {{
                    padding: 6px 8px !important;
                    color: {text_color_css} !important;
                    background-color: transparent !important;
                    border: none !important;
                }}
                
                tr:hover {{
                    background-color: rgba({text_red}, {text_green}, {text_blue}, 0.1) !important;
                }}
                
                h2 {{
                    margin: 0 0 10px 0;
                    padding: 0;
                    color: {text_color_css} !important;
                    font-size: 16px;
                }}
                
                pre {{
                    font-family: Menlo,monospace;
                    font-size: 12px;
                    color: {text_color_css} !important;
                    background-color: {bg_color_css} !important;
                    margin: 0;
                    padding: 0;
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Network & Media Streaming</h2>
                <div class="tabs">
                    <button class="tab active" onclick="showTab('media')">Media Streaming</button>
                    <button class="tab" onclick="showTab('network')">Network Info</button>
                </div>
                
                <div id="media-content" class="tab-content active">
                    {media_html}
                </div>
                
                <div id="network-content" class="tab-content">
                    {ifconfig_content}
                </div>
            </div>
            
            <script>
                function showTab(tabName) {{
                    // Hide all tab contents
                    var contents = document.getElementsByClassName('tab-content');
                    for (var i = 0; i < contents.length; i++) {{
                        contents[i].classList.remove('active');
                    }}
                    
                    // Remove active class from all tabs
                    var tabs = document.getElementsByClassName('tab');
                    for (var i = 0; i < tabs.length; i++) {{
                        tabs[i].classList.remove('active');
                    }}
                    
                    // Show selected tab content
                    document.getElementById(tabName + '-content').classList.add('active');
                    
                    // Add active class to clicked tab
                    event.target.classList.add('active');
                }}
            </script>
        </body>
        </html>
        """
        
        await component.async_open_popover(session_id, html_content, iterm2.util.Size(650, 680))

    # Status bar RPC
    @iterm2.StatusBarRPC
    async def external_ip(knobs, value=iterm2.Reference("iterm2.user." + VARIABLE + "?")):
        global update_interval
        global service_url
        if update_interval_knob in knobs and knobs[update_interval_knob]:
            update_interval = int(knobs[update_interval_knob])
        if service_url_knob in knobs and knobs[service_url_knob]:
            service_url = knobs[service_url_knob]
        if value:
            return value
        return local_ip()

    # Register the component
    await component.async_register(connection, external_ip, onclick=onclick)


iterm2.run_forever(main)
