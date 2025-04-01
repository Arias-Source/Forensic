import os
import subprocess
import json

def create_firefox_profile(profile_name):
    # Path to the Firefox executable
    firefox_path = "/usr/bin/firefox"  # Update this path if necessary
    profile_path = os.path.expanduser("~/.mozilla/firefox/")

    # Create a new profile directory
    profile_dir = os.path.join(profile_path, f"{profile_name}.default-release")
    os.makedirs(profile_dir, exist_ok=True)

    # Create a user.js file to set preferences
    user_js_path = os.path.join(profile_dir, "user.js")
    preferences = {
        "privacy.trackingprotection.enabled": True,
        "privacy.trackingprotection.pbmode.enabled": True,
        "media.peerconnection.enabled": False,  # Disable WebRTC
        "privacy.donottrackheader.enabled": True,
        "privacy.resistFingerprinting": True,
        "network.cookie.cookieBehavior": 2,  # Block all cookies
        "network.cookie.lifetimePolicy": 2,  # Cookies expire at the end of the session
        "browser.privatebrowsing.autostart": True,
        "extensions.pocket.enabled": False,  # Disable Pocket
        "browser.newtabpage.enabled": False,
        "browser.startup.homepage": "about:blank",
        "javascript.enabled": False,  # Keep JavaScript enabled
        "dom.webnotifications.enabled": False,  # Disable notifications
        "permissions.default.image": 2,  # Block images
        "permissions.default.stylesheet": 2,  # Block stylesheets
        "permissions.default.script": 2,  # Block scripts
        "permissions.default.popups": 2,  # Block popups
        "network.http.referer.default": 0,  # Disable referrer
        "network.http.referer.trimmingPolicy": 2,  # Trim referrer
        "webgl.disabled": True,  # Disable WebGL
        "datareporting.healthreport.uploadEnabled": False,  # Disable Telemetry
        "app.shield.optoutstudies.enabled": True,  # Disable Firefox Studies
        "services.sync.enabled": False,  # Disable Firefox Sync
        "network.dns.disablePrefetch": True,  # Disable DNS Prefetching
        "browser.safebrowsing.enabled": False,  # Disable Safe Browsing
        "browser.formfill.enable": False,  # Disable Form Autofill
        "signon.rememberSignons": False,  # Disable Password Manager
        "media.peerconnection.use_document_iceservers": False,  # Disable WebRTC STUN
        "geo.enabled": False,  # Disable location services
        "browser.cache.disk.enable": False,  # Disable browser cache
        "dom.storage.enabled": False,  # Disable third-party storage access
        "app.update.auto": False,  # Disable automatic updates
        "privacy.resistFingerprinting.letterboxing": True,  # Prevent fingerprinting
        "media.autoplay.default": 5,  # Disable media autoplay
        "dom.allow_cut_copy": False,  # Disable clipboard access
        "media.peerconnection.ice.default_address_only": True,  # Prevent WebRTC IP leak
        "general.useragent.override": "    Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",  # Set a custom user agent
        "privacy.firstparty.isolate": True,  # Enable First Party Isolation
        "privacy.partition.network_state": True,  # Partition network state
        "privacy.partition.serviceWorkers": True,  # Partition service workers
        "privacy.partition.cookies": True,  # Partition cookies
        "network.cookie.thirdparty.sessionOnly": True,  # Only allow third-party cookies for the session
        "security.ssl.enable_ocsp_stapling": True,  # Enable OCSP stapling
        "security.ssl.require_safe_negotiation": True,  # Require safe negotiation
        "security.ssl.treat_unsafe_negotiation_as_broken": True,  # Treat unsafe negotiation as broken
        "security.ssl.enable_alpn": True,  # Enable ALPN
        "security.ssl.enable_ocsp": True,  # Enable OCSP
        "security.ssl.errorReporting.automatic": False,  # Disable automatic error reporting
        "network.trr.mode": 2,  # Use DNS over HTTPS
        "network.trr.uri": "https://cloudflare-dns.com/dns-query",  # Set Cloudflare DNS
        # Additional hardcore blocking preferences
        "plugin.state.flash": 0,  # Disable Flash
        "browser.cache.memory.enable": False,  # Disable memory cache
        "security.mixed_content.block_active_content": True,  # Block mixed content
        "media.navigator.enabled": False,  # Disable camera and microphone access
        "pdfjs.disabled": True,  # Disable built-in PDF viewer
        "toolkit.telemetry.enabled": False,  # Disable telemetry
        "toolkit.telemetry.unified": False,  # Disable unified telemetry
        "app.shield.optoutstudies.enabled": True,  # Disable studies
        "privacy.trackingprotection.pbmode.enabled": True,  # Enable tracking protection in private mode
        "privacy.trackingprotection.cryptomining.enabled": True,  # Enable protection against cryptomining
        "privacy.trackingprotection.fingerprinting.enabled": True,  # Enable protection against fingerprinting
    }

    with open(user_js_path, 'w') as user_js:
        for key, value in preferences.items():
            user_js.write(f'user_pref("{key}", {json.dumps(value)});\n')

    return profile_dir

def run_firefox_with_profile(profile_name):
    # Path to the Firefox executable
    firefox_path = "/usr/bin/firefox"  # Update this path if necessary

    # Run Firefox with the new profile
    subprocess.run([firefox_path, '-P', profile_name, '-no-remote'])

def main():
    profile_name = "Private"
    profile_dir = create_firefox_profile(profile_name)
    run_firefox_with_profile(profile_name)

if __name__ == "__main__":
    main()
