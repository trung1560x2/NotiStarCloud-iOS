import os
import sys
import ssl
import uuid
import zlib
import struct
import socket
import plistlib
import tempfile

UDID = "00008160-001C45EA3C60000A"
PAIR_RECORD_PATH = rf"C:\ProgramData\Apple\Lockdown\{UDID}.plist"
APP_URL = "https://trung1560x2.github.io/NotiStarCloud-iOS/?ota=v4"
LOCAL_APP_URL = "http://192.168.11.116:8989/?ota=v4"

def make_icon_png(size=192):
    """Generates a sleek OneUI 7 / iOS 18 rounded gradient icon PNG in pure Python."""
    width = height = size
    raw_rows = []
    cx, cy = width / 2.0, height / 2.0
    for y in range(height):
        row = bytearray([0])  # filter type 0
        for x in range(width):
            # Smooth cosmic blue-purple gradient
            t = (x + y) / (width + height)
            r = int(18 * (1 - t) + 98 * t)
            g = int(105 * (1 - t) + 54 * t)
            b = int(255 * (1 - t) + 245 * t)
            a = 255

            # Draw a crisp white bell/cloud star emblem in center
            dx = (x - cx) / (size * 0.32)
            dy = (y - cy) / (size * 0.32)
            dist2 = dx * dx + dy * dy
            # Bell dome + base + notification dot
            in_dome = (dx * dx + (dy + 0.1) ** 2 < 0.42 and dy < 0.35)
            in_base = (abs(dx) < 0.78 and 0.25 <= dy <= 0.45)
            in_clapper = (dx * dx + (dy - 0.62) ** 2 < 0.06)
            in_badge = ((dx - 0.52) ** 2 + (dy + 0.52) ** 2 < 0.13)

            if in_badge:
                r, g, b = 52, 211, 153  # Emerald cloud sync dot
            elif in_dome or in_base or in_clapper:
                r, g, b = 255, 255, 255

            row.extend((r, g, b, a))
        raw_rows.append(bytes(row))

    raw_data = b"".join(raw_rows)
    def png_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw_data, 9)
    return b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", idat) + png_chunk(b"IEND", b"")


def build_mobileconfig(icon_bytes):
    """Builds an Apple iOS Configuration Profile (.mobileconfig) installing NotiStar Cloud WebClip."""
    profile_Data = {
        "PayloadContent": [
            {
                "FullScreen": True,
                "Icon": icon_bytes,
                "IgnoreManifestScope": True,
                "IsRemovable": True,
                "Label": "NotiStar Cloud",
                "PayloadDescription": "NotiStar Cloud OneUI 7 iOS App (Google Drive Sync & Anti-Revoke)",
                "PayloadDisplayName": "NotiStar Cloud (OneUI 7)",
                "PayloadIdentifier": "com.notistar.cloud.ios.webclip.cloud",
                "PayloadType": "com.apple.webClip.managed",
                "PayloadUUID": "A1B2C3D4-E5F6-4789-9012-3456789ABC01",
                "PayloadVersion": 1,
                "Precomposed": True,
                "URL": APP_URL,
            },
            {
                "FullScreen": True,
                "Icon": icon_bytes,
                "IgnoreManifestScope": True,
                "IsRemovable": True,
                "Label": "NotiStar LAN",
                "PayloadDescription": "NotiStar Cloud Local Wi-Fi Mode (Instant Offline/LAN)",
                "PayloadDisplayName": "NotiStar Cloud (LAN)",
                "PayloadIdentifier": "com.notistar.cloud.ios.webclip.lan",
                "PayloadType": "com.apple.webClip.managed",
                "PayloadUUID": "A1B2C3D4-E5F6-4789-9012-3456789ABC02",
                "PayloadVersion": 1,
                "Precomposed": True,
                "URL": LOCAL_APP_URL,
            }
        ],
        "PayloadDescription": "Cài đặt ứng dụng NotiStar Cloud (OneUI 7) lên màn hình chính iPhone. Tự động đồng bộ tin nhắn thu hồi, ảnh Base64, OTP và biến động số dư với Google Drive.",
        "PayloadDisplayName": "NotiStar Cloud OneUI 7 (iOS)",
        "PayloadIdentifier": "com.notistar.cloud.ios.profile",
        "PayloadOrganization": "NotiStar Cloud OneUI 7",
        "PayloadRemovalDisallowed": False,
        "PayloadType": "Configuration",
        "PayloadUUID": "F1E2D3C4-B5A6-4890-8123-9876543210FE",
        "PayloadVersion": 1,
    }
    return plistlib.dumps(profile_Data)


def usbmux_request(sock, payload, tag=1):
    body = plistlib.dumps(payload)
    header = struct.pack("<IIII", 16 + len(body), 1, 8, tag)
    sock.sendall(header + body)


def usbmux_reply(sock):
    hdr = b""
    while len(hdr) < 16:
        chunk = sock.recv(16 - len(hdr))
        if not chunk:
            raise EOFError("usbmuxd closed connection")
        hdr += chunk
    length, version, msg_type, tag = struct.unpack("<IIII", hdr)
    body = b""
    while len(body) < length - 16:
        chunk = sock.recv(length - 16 - len(body))
        if not chunk:
            raise EOFError("usbmuxd closed body")
        body += chunk
    return plistlib.loads(body)


def usbmux_connect(dev_id, port):
    s = socket.create_connection(("127.0.0.1", 27015), timeout=10)
    net_port = socket.htons(port)
    usbmux_request(s, {
        "MessageType": "Connect",
        "ProgName": "NotiStarInstaller",
        "ClientVersionString": "1.0",
        "DeviceID": dev_id,
        "PortNumber": net_port,
    }, tag=2)
    resp = usbmux_reply(s)
    if resp.get("Number") != 0:
        s.close()
        raise RuntimeError(f"usbmuxd Connect to port {port} failed: {resp}")
    return s


def plist_send(sock, data_dict):
    raw = plistlib.dumps(data_dict)
    sock.sendall(struct.pack(">I", len(raw)) + raw)


def plist_recv(sock):
    hdr = b""
    while len(hdr) < 4:
        c = sock.recv(4 - len(hdr))
        if not c:
            raise EOFError("Lockdown/service socket closed")
        hdr += c
    (size,) = struct.unpack(">I", hdr)
    body = b""
    while len(body) < size:
        c = sock.recv(size - len(body))
        if not c:
            raise EOFError("Lockdown/service socket closed mid-body")
        body += c
    return plistlib.loads(body)


def wrap_lockdown_ssl(sock, pair_record):
    cert_fd, cert_path = tempfile.mkstemp(suffix=".pem")
    key_fd, key_path = tempfile.mkstemp(suffix=".pem")
    try:
        os.write(cert_fd, pair_record["HostCertificate"])
        os.close(cert_fd)
        os.write(key_fd, pair_record["HostPrivateKey"])
        os.close(key_fd)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        # Allow older TLS versions/ciphers if device requires
        try:
            ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
        except Exception:
            pass
        ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
        return ctx.wrap_socket(sock, server_side=False)
    finally:
        try:
            os.remove(cert_path)
            os.remove(key_path)
        except Exception:
            pass


def push_profile_over_usb(mobileconfig_bytes):
    with open(PAIR_RECORD_PATH, "rb") as f:
        pair_record = plistlib.load(f)

    # 1. List USB devices
    mux = socket.create_connection(("127.0.0.1", 27015), timeout=10)
    usbmux_request(mux, {
        "MessageType": "ListDevices",
        "ProgName": "NotiStarInstaller",
        "ClientVersionString": "1.0",
    }, tag=1)
    dev_list = usbmux_reply(mux)
    mux.close()

    dev_id = None
    for entry in dev_list.get("DeviceList", []):
        props = entry.get("Properties", {})
        if props.get("SerialNumber") == UDID and props.get("ConnectionType") == "USB":
            dev_id = entry.get("DeviceID")
            break
    if dev_id is None and dev_list.get("DeviceList"):
        dev_id = dev_list["DeviceList"][0]["DeviceID"]
    if dev_id is None:
        raise RuntimeError("No iPhone found on usbmuxd!")

    print(f"[+] Connected to iPhone over USB (DeviceID={dev_id}, UDID={UDID})")

    # 2. Connect to lockdownd (port 62078)
    ld = usbmux_connect(dev_id, 62078)
    plist_send(ld, {
        "Request": "StartSession",
        "HostID": pair_record["HostID"],
        "SystemBUID": pair_record["SystemBUID"],
        "Label": "NotiStarInstaller",
    })
    sess_resp = plist_recv(ld)
    if sess_resp.get("Error"):
        raise RuntimeError(f"Lockdown StartSession error: {sess_resp}")
    if sess_resp.get("EnableSessionSSL"):
        ld = wrap_lockdown_ssl(ld, pair_record)
    print(f"[+] Lockdown SSL session established (SessionID={sess_resp.get('SessionID')})")

    # 3. StartService com.apple.mobile.MCInstall
    plist_send(ld, {
        "Request": "StartService",
        "Service": "com.apple.mobile.MCInstall",
        "Label": "NotiStarInstaller",
    })
    svc_resp = plist_recv(ld)
    print(f"[+] StartService MCInstall response: {svc_resp}")
    if svc_resp.get("Error"):
        raise RuntimeError(f"StartService MCInstall error: {svc_resp}")

    mc_port = svc_resp["Port"]
    mc_ssl = svc_resp.get("EnableServiceSSL", False)

    # 4. Connect to MCInstall port
    mc = usbmux_connect(dev_id, mc_port)
    if mc_ssl:
        mc = wrap_lockdown_ssl(mc, pair_record)

    # 5. Send InstallProfile command!
    print("[+] Sending NotiStarCloud_OneUI7.mobileconfig to iPhone via MCInstall...")
    plist_send(mc, {
        "RequestType": "InstallProfile",
        "Payload": mobileconfig_bytes,
    })
    mc_resp = plist_recv(mc)
    print(f"[+] MCInstall response: {mc_resp}")
    mc.close()
    ld.close()
    return mc_resp


if __name__ == "__main__":
    icon_png = make_icon_png(192)
    with open(r"e:\MOD\NotiStarCloud_iOS\icon.png", "wb") as f:
        f.write(icon_png)
    with open(r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\icon.png", "wb") as f:
        f.write(icon_png)

    mc_bytes = build_mobileconfig(icon_png)
    for out_p in [
        r"e:\MOD\NotiStarCloud_OneUI7.mobileconfig",
        r"e:\MOD\NotiStarCloud_iOS\NotiStarCloud_OneUI7.mobileconfig",
        r"e:\MOD\NotiStarCloud_iOS\WebApp_PWA\NotiStarCloud_OneUI7.mobileconfig",
    ]:
        with open(out_p, "wb") as f:
            f.write(mc_bytes)
    print(f"[+] Built NotiStarCloud_OneUI7.mobileconfig ({len(mc_bytes)} bytes)")

    push_profile_over_usb(mc_bytes)
