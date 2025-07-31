from curl_cffi import requests
from urllib.parse import parse_qs, unquote
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz, time

wib = pytz.timezone('Asia/Jakarta')

class EmoryaBot: # Mengubah nama kelas menjadi EmoryaBot
    def __init__(self) -> None:
        self.BASE_API = "https://api.emorya.com" # Base API untuk Emorya
        self.REF_CODE = "YOUR_EMORYA_REF_CODE" # Ganti dengan kode referral Emorya Anda jika ada
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.query_id = {}
        self.username = {}
        self.tokens = {} # Untuk menyimpan token otorisasi Emorya
        self.spin_cooldowns = {} # Untuk menyimpan waktu cooldown spin per user

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Emorya Bot {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
            
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def extract_query_data(self, query: str):
        try:
            account = parse_qs(query).get('user', [None])[0]
            account_data = json.loads(unquote(account))
            user_id = account_data.get("id", None)
            username = account_data.get("username", "Unknown")

            return user_id, username
        except Exception as e:
            return None, None
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxyscrape Free Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Proxyscrape Free" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        url = "https://api.ipify.org?format=json"
        proxies = {"http":proxy, "https":proxy} if proxy else None
        try:
            response = await asyncio.to_thread(requests.get, url=url, proxies=proxies, timeout=30, impersonate="chrome110", verify=False)
            response.raise_for_status()
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
    
    # --- Metode API Emorya ---

    async def user_login(self, user_id: str, proxy=None, retries=5):
        # *** PENTING: Anda perlu mengidentifikasi endpoint login yang sebenarnya
        # *** dari Emorya bot. Ini adalah ASUMSI berdasarkan pola TWA umumnya.
        # *** Periksa traffic jaringan saat pertama kali membuka bot Emorya.
        # Misalnya: POST ke /auth/login atau /register
        url = f"{self.BASE_API}/auth/login" # <--- ASUMSI: SESUAIKAN JIKA BERBEDA
        data = json.dumps({"initData": self.query_id[user_id], "source": self.REF_CODE}) # Sesuaikan payload jika diperlukan
        headers = self.HEADERS[user_id].copy()
        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                response_json = response.json()
                # *** PENTING: Identifikasi kunci di mana token disimpan dalam respons login
                auth_token = response_json.get("token") # <--- ASUMSI: SESUAIKAN JIKA KUNCINYA BERBEDA
                if auth_token:
                    self.tokens[user_id] = auth_token
                    return True
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} GET Access Token Failed (Token not found in response) {Style.RESET_ALL}"
                    )
                    return None
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} LOGIN Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
        return None

    async def get_emorya_user_data(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user" # Endpoint untuk mendapatkan data pengguna
        headers = self.HEADERS[user_id].copy()
        headers["Authorization"] = f"Token {self.tokens[user_id]}" # Gunakan token yang didapat dari login
        
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)   
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Error     :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Emorya User Data Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
        return None
            
    async def claim_bmr_calories(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/claim-bmr-calories" # Endpoint untuk klaim kalori BMR
        headers = self.HEADERS[user_id].copy()
        headers["Authorization"] = f"Token {self.tokens[user_id]}"
        headers["Content-Length"] = "0" # Payload kosong
        
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)   
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Claim Kcal:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Claim Calories {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
        return None
                
    async def check_spin_cooldown(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/claim_cooldown" # Endpoint untuk cek cooldown spin
        headers = self.HEADERS[user_id].copy()
        headers["Authorization"] = f"Token {self.tokens[user_id]}"
        
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)   
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Spin Cd.  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to get Spin Cooldown {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
        return None
                
    async def perform_spin(self, user_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wheel/spin" # Endpoint untuk melakukan spin
        headers = self.HEADERS[user_id].copy()
        headers["Authorization"] = f"Token {self.tokens[user_id]}"
        headers["Content-Length"] = "0" # Payload kosong
        
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)   
                if response.status_code == 400: # Contoh penanganan error spesifik
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Spin      :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Spin Not Available (e.g., no spins left, or cooldown) {Style.RESET_ALL}"
                    )
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Spin      :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Perform Spin {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
        return None
    
    # Endpoint wheel/wins tidak perlu dipanggil rutin oleh bot kecuali Anda ingin menampilkan daftar hadiah
    # async def get_wheel_wins(self, user_id: str, proxy=None, retries=5):
    #     url = f"{self.BASE_API}/wheel/wins"
    #     headers = self.HEADERS[user_id].copy()
    #     headers["Authorization"] = f"Token {self.tokens[user_id]}"
    #     await asyncio.sleep(3)
    #     for attempt in range(retries):
    #         proxies = {"http":proxy, "https":proxy} if proxy else None
    #         try:
    #             response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)   
    #             response.raise_for_status()
    #             return response.json()
    #         except Exception as e:
    #             if attempt < retries - 1:
    #                 await asyncio.sleep(5)
    #                 continue
    #             self.log(f"{Fore.RED+Style.BRIGHT}Failed to get wheel wins: {e}{Style.RESET_ALL}")
    #     return None

    # --- Proses Akun ---
            
    async def process_check_connection(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy if proxy else 'No Proxy'} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if is_valid:
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(user_id)
                await asyncio.sleep(1)
                continue

            return False # Jika tidak merotasi dan koneksi gagal, hentikan
            
    async def process_user_login(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        is_connected = await self.process_check_connection(user_id, use_proxy, rotate_proxy)
        if is_connected:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None
            
            if user_id in self.tokens: # Jika sudah ada token, anggap sudah login
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} User already logged in (token exists) {Style.RESET_ALL}"
                )
                return True

            logined = await self.user_login(user_id, proxy)
            if logined:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} GET Access Token Success {Style.RESET_ALL}"
                )
                return True
            
        return False
            
    async def process_accounts(self, user_id: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(user_id, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(user_id) if use_proxy else None

            # --- Dapatkan Data Pengguna ---
            emorya_user_data = await self.get_emorya_user_data(user_id, proxy)
            if emorya_user_data:
                emrs_balance = emorya_user_data.get("transferableEMRS", "0.0")
                referral_code = emorya_user_data.get("referral_code", "N/A")
                total_calories = emorya_user_data.get("totalCalories", 0.0)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}EMRS Balance:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {emrs_balance} EMRS {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Referral Code:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {referral_code} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Total Kcal  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {total_calories} Kcal {Style.RESET_ALL}"
                )
            else:
                self.log(f"{Fore.RED+Style.BRIGHT}Failed to retrieve user data for {self.username.get(user_id, 'Unknown')}{Style.RESET_ALL}")
                return # Hentikan proses untuk akun ini jika data tidak bisa diambil

            # --- Klaim Kalori BMR ---
            claim_kcal_res = await self.claim_bmr_calories(user_id, proxy)
            if claim_kcal_res:
                claimed_amount = claim_kcal_res.get("calories_claimed", 0)
                if claimed_amount > 0:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Claim Kcal:{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Claimed {claimed_amount} Kcal {Style.RESET_ALL}"
                    )
                else:
                    self.log(f"{Fore.CYAN+Style.BRIGHT}Claim Kcal:{Style.RESET_ALL}{Fore.YELLOW+Style.BRIGHT} No Calories to Claim {Style.RESET_ALL}")
            else:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Claim Kcal:{Style.RESET_ALL}{Fore.RED+Style.BRIGHT} Claiming Failed or No Data {Style.RESET_ALL}")

            # --- Spin Roda ---
            spin_cooldown_data = await self.check_spin_cooldown(user_id, proxy)
            if spin_cooldown_data:
                cooldown_timestamp = spin_cooldown_data.get("cooldown", 0)
                current_timestamp = int(time.time()) # Menggunakan time.time() untuk Unix Timestamp saat ini
                
                if cooldown_timestamp <= current_timestamp:
                    self.log(f"{Fore.CYAN+Style.BRIGHT}Spin      :{Style.RESET_ALL}{Fore.GREEN+Style.BRIGHT} Spin Available {Style.RESET_ALL}")
                    
                    # Jeda 15 detik sebelum spin, sesuai observasi Anda
                    self.log(f"{Fore.YELLOW+Style.BRIGHT}Waiting 15 seconds before spinning...{Style.RESET_ALL}")
                    await asyncio.sleep(15)

                    spin_result = await self.perform_spin(user_id, proxy)
                    if spin_result:
                        reward_id = spin_result.get("result", "Unknown")
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Spin      :{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Spin Success! Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{reward_id}{Style.RESET_ALL}"
                        )
                        # Setelah spin, segera perbarui cooldown untuk akun ini
                        # Untuk mencegah spin lagi sebelum waktunya di iterasi berikutnya jika bot berjalan cepat
                        new_cooldown_check = await self.check_spin_cooldown(user_id, proxy)
                        if new_cooldown_check and new_cooldown_check.get("cooldown"):
                            self.spin_cooldowns[user_id] = new_cooldown_check["cooldown"]
                    else:
                        self.log(f"{Fore.RED+Style.BRIGHT}Spin      :{Style.RESET_ALL}{Fore.RED+Style.BRIGHT} Spin Failed {Style.RESET_ALL}")
                else:
                    remaining_time = cooldown_timestamp - current_timestamp
                    formatted_remaining_time = self.format_seconds(remaining_time)
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Spin      :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Cooldown. Next spin in {formatted_remaining_time} {Style.RESET_ALL}"
                    )
                    # Simpan cooldown untuk digunakan di loop utama jika bot tidak dijalankan per akun
                    self.spin_cooldowns[user_id] = cooldown_timestamp
            else:
                self.log(f"{Fore.RED+Style.BRIGHT}Spin      :{Style.RESET_ALL}{Fore.RED+Style.BRIGHT} Could not get Spin Cooldown status {Style.RESET_ALL}")
        
        # --- Bagian lain dari Midas RWA (Daily, Referral, Tasks) tidak ada data yang diberikan untuk Emorya
        # --- Jadi, saya mengomentarinya atau menghapusnya. Jika Emorya memiliki fitur serupa,
        # --- Anda perlu mengidentifikasi endpoint dan logikanya, lalu menambahkannya kembali.
        # await self.user_visited(user_id, proxy) # Kemungkinan tidak relevan untuk Emorya
        # await self.daily_checkin(user_id, proxy) # Kemungkinan tidak relevan untuk Emorya
        # await self.refferal_status(user_id, proxy) # Referral code sudah didapat dari get_emorya_user_data
        # await self.play_game(user_id, proxy) # Spin adalah "game" di Emorya
        # await self.available_tasks(user_id, proxy) # Jika Emorya punya sistem task, perlu diimplementasi
        
    async def main(self):
        try:
            with open('query.txt', 'r') as file:
                queries = [line.strip() for line in file if line.strip()]

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                
                if use_proxy:
                    await self.load_proxies(use_proxy_choice)

                separator = "=" * 20
                for idx, query in enumerate(queries, start=1):
                    if query:
                        user_id, username = self.extract_query_data(query)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(queries)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not user_id or not username:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Query Data {Style.RESET_ALL}"
                            )
                            continue

                        # Header dasar untuk setiap akun
                        self.HEADERS[user_id] = {
                            "Accept": "*/*",
                            "Accept-Encoding": "gzip, deflate, br, zstd",
                            "Accept-Language": "en-US,en;q=0.6",
                            "Origin": "https://telegram.emorya.com", # SESUAIKAN DENGAN DOMAIN INI
                            "Referer": "https://telegram.emorya.com/", # SESUAIKAN DENGAN DOMAIN INI
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "User-Agent": FakeUserAgent().random,
                            "Priority": "u=1, i",
                            "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
                            "Sec-Ch-Ua-Mobile": "?0",
                            "Sec-Ch-Ua-Platform": '"Windows"',
                            "Sec-Gpc": "1",
                        }

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Username  :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {username} {Style.RESET_ALL}"
                        )

                        self.query_id[user_id] = query
                        self.username[user_id] = username
                        
                        await self.process_accounts(user_id, use_proxy, rotate_proxy)
                        await asyncio.sleep(3) # Jeda antar akun
                
                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*50)

                # Menghitung waktu tunggu berdasarkan cooldown spin terlama atau default
                wait_seconds = 6 * 60 * 60 # Default: 6 jam
                if self.spin_cooldowns:
                    # Cari cooldown terlama dari semua akun
                    max_cooldown = max(self.spin_cooldowns.values())
                    current_time = int(time.time())
                    if max_cooldown > current_time:
                        # Set waktu tunggu menjadi sisa cooldown terlama + sedikit buffer
                        wait_seconds = max_cooldown - current_time + 60 # Tambah 1 menit buffer
                        self.log(f"{Fore.YELLOW+Style.BRIGHT}Adjusting wait time to match longest spin cooldown.{Style.RESET_ALL}")
                    else:
                        self.log(f"{Fore.YELLOW+Style.BRIGHT}All spins are ready or cooldowns passed. Using default wait time.{Style.RESET_ALL}")
                
                while wait_seconds > 0:
                    formatted_time = self.format_seconds(wait_seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    wait_seconds -= 1
                print("\n") # Membersihkan baris tunggu
                self.spin_cooldowns.clear() # Reset cooldowns setelah setiap siklus utama

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = EmoryaBot()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"\n{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Emorya Bot - BOT{Style.RESET_ALL}                                      "
        )
