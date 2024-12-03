import cloudscraper
import re
from bot.utils import logger
from bot.config import settings

session = cloudscraper.create_scraper()

baseUrl = "https://api.tapswap.club"
pattern = r'"(https?://[^\s"]+)"'

def get_main_js_format(base_url):
    try:
        response = session.get(base_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        content = response.text
        matches = re.findall(r'src="(/assets/main-[^"]+\.js)"', content)
        if matches:
            # Return all matches, sorted by length (assuming longer is more specific)
            return sorted(set(matches), key=len, reverse=True)
        else:
            return None
    except Exception as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None

def get_base_api(url):
    try:
        logger.info("Checking for changes in api...")
        response = session.get(url)
        response.raise_for_status()
        content = response.text
        match = re.findall(pattern, content)

        if match:
            # print(match.group(1))
            return match
        else:
            logger.info("Could not find 'baseUrl' in the content.")
            return None
    except Exception as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def check_base_url():
    base_url = f"https://app.tapswap.club/?bot={settings.BOT_KEY}"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        if settings.ADVANCED_ANTI_DETECTION:
            r = session.get(
                "https://raw.githubusercontent.com/vanhbakaa/nothing/refs/heads/main/tapswap")
            js_ver = r.text.strip()
            # print(main_js_formats)

            for js in main_js_formats:
                if js_ver in js:
                    logger.success(f"<green>No change in js file: {js_ver}</green>")
                    return True

            return False
        # print(main_js_formats)
        for format in main_js_formats:
            logger.info(f"Trying format: {format}")
            full_url = f"https://app.tapswap.club{format}"
            result = get_base_api(full_url)
            # print(f"{result} | {baseUrl}")
            if baseUrl in result:
                logger.success("<green>No change in api!</green>")
                return True
        return False

    else:
        logger.info("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = session.get(base_url)
            print(response.text[:1000])  # Print first 1000 characters of the page
            return False
        except Exception as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
            return False