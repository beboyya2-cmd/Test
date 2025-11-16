import requests
import time
import subprocess
import random
import string

# ============================================================================
# SESSION POOL (50 sessions)
# ============================================================================

def generate_session_id():
    timestamp = int(time.time() * 1000)
    random_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"session_{timestamp}_{random_code}"

SESSION_IDS = [
    "session_1763294853907_m4mzvgd9r",
    "session_1763294853908_r826nlsbg",
    "session_1763294853910_59ncg0uhl",
    "session_1763294853911_qvfs2ewsj",
    "session_1763294853913_npm8xd9ra",
    "session_1763294853914_kgstwm5s8",
    "session_1763294853916_z4qbfh4xt",
    "session_1763294853917_rvk0ek13g",
    "session_1763294853919_gaw0owmw4",
    "session_1763294853921_kc9bkjcos",
    "session_1763294853922_zcuigv1qg",
    "session_1763294853924_tf6yb1f5k",
    "session_1763294853925_ko725csac",
    "session_1763294853927_dyf2mpgb0",
    "session_1763294853928_593lhn92p",
    "session_1763294853930_b6a1o41mo",
    "session_1763294853931_sss6068uz",
    "session_1763294853933_nyqqqdpmx",
    "session_1763294853934_pmhk482vm",
    "session_1763294853936_e15dv7gs6",
    "session_1763294853937_1rkhuhjex",
    "session_1763294853939_rcrgzfjk2",
    "session_1763294853940_1d3ym65li",
    "session_1763294853942_euhs8qrdj",
    "session_1763294853943_ksj9m2d6a",
    "session_1763294853945_i3qwn8rbx",
    "session_1763294853947_ahi5gwumd",
    "session_1763294853948_bbqtmp099",
    "session_1763294853950_f15quifxr",
    "session_1763294853951_olx8w007v",
    "session_1763294853953_mulmntz7c",
    "session_1763294853954_5n4grt4hh",
    "session_1763294853956_a2up27fio",
    "session_1763294853957_e1bm1f9r1",
    "session_1763294853959_59jycbogn",
    "session_1763294853960_uzqhze6cg",
    "session_1763294853962_n221mxv0p",
    "session_1763294853963_akdl5eaob",
    "session_1763294853965_ripbwysg7",
    "session_1763294853966_urgpki6h8",
    "session_1763294853968_9ler2aykk",
    "session_1763294853969_ozpk5swf1",
    "session_1763294853971_i9qzvnor2",
    "session_1763294853973_do8rmp4ax",
    "session_1763294853974_dw1ted1xx",
    "session_1763294853976_s1yajx8d7",
    "session_1763294853977_0t9bebdxi",
    "session_1763294853979_ssj1ggq1n",
    "session_1763294853980_fhzyn0muy",
    "session_1763294853982_8rbhh3816",
]

if len(SESSION_IDS) < 50:
    for i in range(50 - len(SESSION_IDS)):
        SESSION_IDS.append(generate_session_id())
        time.sleep(0.001)

COOKIE_STRING = "intercom-device-id-x55eda6t=57526347-f0e0-4309-a6b0-e42a1c50e99c; __stripe_mid=9b58c873-5a15-4cc9-87d0-368957d993199ffbc5; ph_phc_TXdpocbGVeZVm5VJmAsHTMrCofBQu3e0kN8HGMNGTVW_posthog=%7B%22distinct_id%22%3A%220199e518-a658-7ebd-9944-81f521f1d880%22%2C%22%24sesid%22%3A%5B1760768907411%2C%220199f601-332c-7e4f-a481-50851994be49%22%2C1760768897836%5D%7D; sessionid=66d147dc-3b4c-40b2-955c-791705b6b029; intercom-session-x55eda6t=NVA3REgxYmJiaDgvWnp5anNJcnJpNmJxdzZOZ3Q0c2VqaXdtU1FqL3JzMFpZRUNFR3lVRXlOMEtNdXJYeUx6RUxWUnBzbDRKVU80Y2F5RlJLVnNDa25GWnhPbXFDK2ttcFFSaU90dEk3aEk9LS1QandJUHJuei90ZjJEVzBibG0vTnZRPT0=--639e36a21d5bbe44ee42c42e4cf7379cdd3403fe; __Host-next-auth.csrf-token=16bba1605c4b8ef576fcc73f9738322a90a93e57debcf40d957b7c846a719b28%7C1da500e11659a845c9b54dbcdb1b11c3c786a8591d00e2d5a676aa1757886ff4; __Secure-next-auth.callback-url=https%3A%2F%2Fbuild.blackbox.ai; __stripe_sid=3fd7c91d-f412-44f4-88f6-bf42ee6a6b72bf659e; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..0FNNW_P8pu8jeLH4.dd5xzxhS2BDO2p86ZzBHhWsBTIOkUaShDHixw8N1oHMbnKP-d3VtP8Ne6fzElq3c_fjcsEjknJ-encSJlflosi-LJTMr_zuPj1q1w9EDRn6d3dOc4khL9s5RocAe11fwQhcZKwJjWYg3P-94p_piCKtZ8gEBbfyoklbTKGOnqUp3LG9fk54eLHVFuIWj3e4gX5TWM76qmDpo1CPNDNj03Hs12ZOkI3d_Go1Ny5Q_YzQfTl_TzEy3gfJLGgb1GfQqEdsAnqoYmkXJzeZGAG7Z2ZpLFKWVZflc3quNe9zqPsmNWLhbqWu7x64BAlsrmiBUbv0Bb3B3pRbjzMM8S_L6fGM_EagFkb-SB0740VweQU1T1YEy_f84-kh4V2cSPsYWvu6qs02ZdZSwARpk6LWiRHFsQd76sgarDLmTQNC7bpSPxqi3LPLHkw3xRdlAWrr1Qa-LC5-sZR_aYgaQx-dxVtlTbDT5i21lZsf2L8ZwoQmSe10lF4vb_km5r02JqHTOloq0BW7lenOorS-gG1gfyUhmFUM_-Lfblbk5pbW-bOXYMHpKaeHKDxwD8sV0mg.nchQw2ktICTBVxrneGPEhw"
MAIN_SCRIPT_LINK = "https://raw.githubusercontent.com/beboyya2-cmd/Test/refs/heads/main/main.py"
REVIVAL_SCRIPT_LINK = "https://raw.githubusercontent.com/beboyya2-cmd/Test/refs/heads/main/revive.py"
REQUIREMENTS = "requests beautifulsoup4 python-telegram-bot"
CUSTOM_COMMANDS = []

def parse_cookies(cookie_string):
    cookies = {}
    for cookie in cookie_string.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookies[name] = value
    return cookies

def create_sandbox(session_id, cookies):
    url = "https://build.blackbox.ai/api/create-sandbox-for-session"
    headers = {"accept": "*/*", "content-type": "application/json", "referer": "https://build.blackbox.ai/chat-history"}
    payload = {"sessionId": session_id, "ports": [3000], "runDevServer": True}
    try:
        response = requests.post(url, headers=headers, json=payload, cookies=cookies, timeout=45)
        data = response.json()
        return data.get("sandboxId")
    except:
        return None

def create_terminal(sandbox_id, cookies):
    url = "https://build.blackbox.ai/api/terminals/create"
    headers = {"accept": "*/*", "content-type": "application/json", "referer": f"https://build.blackbox.ai/?sandboxId={sandbox_id}"}
    payload = {"sandboxId": sandbox_id, "name": f"terminal_{int(time.time() * 1000)}"}
    response = requests.post(url, headers=headers, json=payload, cookies=cookies, timeout=30)
    return response.json()["terminal"]["terminalId"]

def execute_command(sandbox_id, terminal_id, command, cookies):
    url = "https://build.blackbox.ai/api/terminals/execute"
    headers = {"accept": "*/*", "content-type": "application/json", "referer": f"https://build.blackbox.ai/?sandboxId={sandbox_id}"}
    payload = {"sandboxId": sandbox_id, "terminalId": terminal_id, "command": command, "workingDirectory": "."}
    try:
        requests.post(url, headers=headers, json=payload, cookies=cookies, timeout=10)
    except:
        pass

def find_available_session(cookies):
    shuffled = SESSION_IDS.copy()
    random.shuffle(shuffled)
    for session_id in shuffled:
        sandbox_id = create_sandbox(session_id, cookies)
        if sandbox_id:
            return sandbox_id, session_id
        time.sleep(0.5)
    new_session = generate_session_id()
    sandbox_id = create_sandbox(new_session, cookies)
    if sandbox_id:
        SESSION_IDS.append(new_session)
        return sandbox_id, new_session
    return None, None

time.sleep(14400)
subprocess.run(["pkill", "-f", "main_script.py"])
time.sleep(30)
cookies = parse_cookies(COOKIE_STRING)
sandbox_id, used_session = find_available_session(cookies)
if not sandbox_id:
    exit(1)
terminal_id = create_terminal(sandbox_id, cookies)
execute_command(sandbox_id, terminal_id, "sudo dnf install -y python3 python3-pip", cookies)
execute_command(sandbox_id, terminal_id, f"pip3 install --upgrade {REQUIREMENTS}", cookies)
if CUSTOM_COMMANDS:
    for cmd in CUSTOM_COMMANDS:
        execute_command(sandbox_id, terminal_id, cmd, cookies)
execute_command(sandbox_id, terminal_id, f"curl -fsSL -o main_script.py {MAIN_SCRIPT_LINK}", cookies)
execute_command(sandbox_id, terminal_id, f"curl -fsSL -o revival_script.py {REVIVAL_SCRIPT_LINK}", cookies)
execute_command(sandbox_id, terminal_id, "nohup python3 main_script.py > main_script.log 2>&1 &", cookies)
execute_command(sandbox_id, terminal_id, "nohup python3 revival_script.py > revival_script.log 2>&1 &", cookies)
