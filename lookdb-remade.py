           Remade By Cyb3rtech
         Discord : @antidatabreach
#############################################

import discord
from discord.ext import commands
from fake_useragent import UserAgent
from ipwhois import IPWhois
import asyncio
import aiohttp
import re
from datetime import datetime, timezone
import requests
import os
import socket
import idna
import json
import uuid
from colorama import Fore, Style
from discord import Embed, Colour

#############################################

token = ''
prefix = '+'
ipinfo_token = ''

#############################################

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)
bot.remove_command('help')

#############################################

def print_dark_red(text):
    print(f"\033[31m{text}\033[0m")

def print_dark_blue(text):
    print(f"\033[34m{text}\033[0m")
    
#############################################
    
def clean_filename(hostname):
    return re.sub(r'^([0-9])', '', re.sub(r'[/:"*?<>|]', '', hostname)).replace('^0','').replace('^1','').replace('^2','').replace('^3','').replace('^4','').replace('^5','').replace('^6','').replace('^7','').replace('^8','').replace('^9','')

def check_if_player_exists(filename, player_data, added_players):
    if not os.path.exists(filename):
        return False

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        try:
            existing_player = json.loads(line)
        except json.JSONDecodeError:
            continue

        if existing_player.get('fivem') == player_data.get('fivem'):
            fields_to_check = ['steam', 'name', 'live', 'xbl', 'license', 'license2','name']
            fields_match = True

            for field in fields_to_check:
                existing_field_value = existing_player.get(field)
                new_field_value = player_data.get(field)

                if (existing_field_value is not None or new_field_value is not None) and existing_field_value != new_field_value:
                    fields_match = False
                    break

            if fields_match:
                return True

    if player_data['identifiers'] in added_players:
        return True

    return False

async def get_server_info(server_id, added_players):
    url = f'https://servers-frontend.fivem.net/api/servers/single/{server_id}'
    user_agent = UserAgent()
    headers = {
        'User-Agent': user_agent.random,
        'method': 'GET'
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            server_data = response.json()
            hostname = clean_filename(str(uuid.uuid4()))

            try:
                hostname = clean_filename(server_data['Data']['hostname'])[:100]
            except Exception as err:
                print(err)

            try:
                if len(server_data['Data']['vars']['sv_projectName']) >= 10:
                    hostname = clean_filename(server_data['Data']['vars']['sv_projectName'])[:100]
            except:
                pass

            if not os.path.exists('dump'):
                os.makedirs('dump')

            filename = f'dump/{hostname}.txt'

            for player in server_data['Data']['players']:
                player_data = json.dumps(player, ensure_ascii=False)
                player_identifiers = player['identifiers']

                if not check_if_player_exists(filename, player, added_players):
                    with open(filename, 'a', encoding='utf-8') as file:
                        file.write(player_data)
                        file.write('\n')

                    print(Fore.GREEN + f'[NEW]' + Style.RESET_ALL + f' {player["name"]} a été ajouté !')
                    added_players.append(player_identifiers)

            print('\n' + Fore.MAGENTA + '\n[INFO]' + Style.RESET_ALL + f' Serveur id : {server_id}' + Fore.MAGENTA + '\n[INFO]' + Style.RESET_ALL + f' Enregistrées dans : {filename}' + '\n')

        else:
            print(Fore.RED + f'\n[ERROR]' + Style.RESET_ALL + f" Message d'erreur ({server_id}: {response.status_code})\n")

    except Exception as e:
        print(f'Erreur: {str(e)}')

async def process_servers(server_ids, added_players):
    tasks = []
    for server_id in server_ids:
        tasks.append(asyncio.create_task(get_server_info(server_id, added_players)))
        await asyncio.sleep(0.5)

    await asyncio.gather(*tasks)

async def monitor_servers():
    while True:
        with open('serveur.txt', 'r') as server_file:
            server_ids = [line.strip() for line in server_file.readlines()]

        added_players = []
        await process_servers(server_ids, added_players)
        await asyncio.sleep(0.5)

#############################################

class PaginationView(discord.ui.View):
    def __init__(self, ctx, discord_id, lookup_results, current_page=0):
        super().__init__()
        self.ctx = ctx
        self.discord_id = discord_id
        self.lookup_results = lookup_results
        self.current_page = current_page

        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        self.add_item(discord.ui.Button(label="⬅️", style=discord.ButtonStyle.blurple, disabled=(self.current_page == 0), row=1, custom_id="previous_page"))
        self.add_item(discord.ui.Button(label="➡️", style=discord.ButtonStyle.blurple, disabled=(self.current_page == len(self.lookup_results) - 1), row=1, custom_id="next_page"))
        self.add_item(discord.ui.Button(label="Envoyer en DM", style=discord.ButtonStyle.blurple, row=1, custom_id="send_dm"))

#############################################

    async def update_page(self, interaction: discord.Interaction):
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def create_embed(self):
        result = self.lookup_results[self.current_page]
        server_name = os.path.splitext(os.path.basename(result['filename']))[0]
        embed = discord.Embed(title=f"🔍 Résultats pour Discord ID : {self.discord_id}", color=0x57F287)
        embed.add_field(name="📌 **Nom du serveur**", value=server_name, inline=False)
        embed.add_field(name="📋 **Nom**", value=result.get('name', 'Utilisateur Example'), inline=False)
        embed.add_field(name="<:discord:1257773225790672906> **Discord ID**", value=self.discord_id, inline=False)
        embed.add_field(name="<:steam:1257773282665697405>  **Steam ID**", value=result.get('steam_id', 'Aucune données'), inline=False)
        embed.add_field(name="<:xbox:1257773308905259048> **Xbox Live ID**", value=result.get('xbl_id', 'Aucune données'), inline=False)
        embed.add_field(name="<:microsoft:1257773324818317463> **Microsoft Live ID**", value=result.get('live_id', 'Aucune données'), inline=False)
        embed.add_field(name="<:fivem:1257773345357955072> **FiveM ID**", value=result.get('fivem_id', 'Aucune données'), inline=False)
        embed.add_field(name="<:dossier:1257773357458395186> **Licence ID**", value=result.get('license_id', 'Aucune données'), inline=False)
        embed.add_field(name="<:dossier:1257773357458395186> **Licence 2 ID**", value=result.get('license2_id', 'Aucune données'), inline=False)
        embed.add_field(name="<:ip:1257778397094875218> **IP**", value=f"`{result.get('ip_address', 'Aucune données')}`" if result.get('ip_address') else ' Aucune données', inline=False)
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.lookup_results)} • lookdb remade by cyb3rtech")
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple, row=1)
    async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_page(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, row=1)
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page < len(self.lookup_results) - 1:
            self.current_page += 1
            await self.update_page(interaction)

    @discord.ui.button(label="Envoyer en DM", style=discord.ButtonStyle.green, row=1)
    async def send_dm(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = self.create_embed()
        try:
            await self.ctx.author.send(embed=embed)
            await interaction.response.send_message("Embed envoyé en DM.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Impossible d'envoyer un DM. Vérifiez si vos DM sont ouverts.", ephemeral=True)

#############################################

async def search_in_database(discord_id, ctx, embed):
    database_folder_path = "database"
    results = []

    for filename in os.listdir(database_folder_path):
        file_path = os.path.join(database_folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            print(f"Ignoring line that is not valid JSON: {line}")
                            continue

                        identifiers = data.get('identifiers', [])
                        discord_ids = [identifier.split(":")[1] for identifier in identifiers if identifier.startswith("discord:")]
                        ips = [identifier.split(":")[1] for identifier in identifiers if identifier.startswith("ip:")]

                        if discord_id in discord_ids or (ips and ips[0] != "None" and ips[0] != "False"):
                            result_entry = {
                                'filename': file_path,
                                'name': data.get('name', 'Utilisateur Example'),
                                'steam_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("steam:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'xbl_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("xbl:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'live_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("live:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'fivem_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("fivem:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'license_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("license:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'license2_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("license2:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'ip_address': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("ip:") and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                            }
                            results.append(result_entry)

    return results

#############################################

async def search_in_db(discord_id, ctx, embed):
    dump_folder_path = "dump"
    results = []

    with open("bls.txt", "r") as bls_file:
        if discord_id in bls_file.read().splitlines():
            embed = discord.Embed(title="Erreur", description=f"L'utilisateur avec l'ID Discord {discord_id} est sur la liste noire.", color=0xED4245)
            embed.set_footer(text="lookdb remade by cyb3rtech")
            await ctx.send(embed=embed)
            return results

    for filename in os.listdir(dump_folder_path):
        file_path = os.path.join(dump_folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            print(f"Ignoring line that is not valid JSON: {line}")
                            continue

                        identifiers = data.get('identifiers', [])
                        discord_ids = [identifier.split(":")[1] for identifier in identifiers if identifier.startswith("discord:")]

                        if discord_id in discord_ids:
                            result_entry = {
                                'filename': file_path,
                                'name': data.get('name', 'Utilisateur Example'),
                                'steam_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("steam:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'xbl_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("xbl:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'live_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("live:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'fivem_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("fivem:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'license_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("license:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'license2_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("license2:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                            }
                            results.append(result_entry)

    return results
    
#############################################

async def update_lookup_embed(ctx, message, discord_id, lookup_results):
    if not lookup_results:
        user = ctx.author
        embed = discord.Embed(title=f"🔍 Aucun résultat trouvé pour Discord ID : {discord_id}", color=0xED4245)
        embed.set_footer(text="lookdb remade by cyb3rtech")
        embed.set_thumbnail(url=user.avatar.url)
        await message.edit(content='', embed=embed)
    else:
        view = PaginationView(ctx, discord_id, lookup_results)
        embed = view.create_embed()
        await message.edit(content='', embed=embed, view=view)

async def search_in_db(discord_id, ctx, embed):
    dump_folder_path = "dump"
    results = []

    with open("bls.txt", "r") as bls_file:
        if discord_id in bls_file.read().splitlines():
            embed = discord.Embed(title="Erreur", description=f"L'utilisateur avec l'ID Discord {discord_id} est sur la liste noire.", color=0xED4245)
            embed.set_footer(text="lookdb remade by cyb3rtech")
            await ctx.send(embed=embed)
            return results

    for filename in os.listdir(dump_folder_path):
        file_path = os.path.join(dump_folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            print(f"Ignoring line that is not valid JSON: {line}")
                            continue

                        identifiers = data.get('identifiers', [])
                        discord_ids = [identifier.split(":")[1] for identifier in identifiers if identifier.startswith("discord:")]

                        if discord_id in discord_ids:
                            result_entry = {
                                'filename': file_path,
                                'name': data.get('name', 'Utilisateur Example'),
                                'steam_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("steam:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'xbl_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("xbl:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'live_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("live:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'fivem_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("fivem:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'license_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("license:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'license2_id': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("license2:") and len(identifier.split(":")[1]) >= 4 and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                                'ip_address': next((identifier.split(":")[1] for identifier in identifiers if identifier.startswith("ip:") and identifier.split(":")[1] not in ["None", "False"]), 'Aucune données'),
                            }
                            results.append(result_entry)

    return results
    
#############################################
    
async def get_geoip_info(ip_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ipinfo.io/{ip_address}/json?token={ipinfo_token}") as response:
            if response.status != 200:
                return None
            data = await response.json()
            return data
            
#############################################

@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="📜Liste Des Commandes", description="Voici une liste des commandes disponibles :\n")
    embed.add_field(name="\n🔧 Commandes Créateurs :\n", value="\n", inline=False)
    embed.add_field(name=f"🎮 {prefix}players", value="Affiche le nombre total de joueurs unique enregistrés.", inline=False)
    embed.add_field(name=f"🔍 Commandes de Recherche :", value="\n", inline=False)
    embed.add_field(name=f"🔎 {prefix}lookup <mot-clé>", value="Recherche dans la bdd Fivem.", inline=False)
    embed.add_field(name=f"👑 {prefix}vip <mot-clé>", value="Voir les infos dans la bdd Fivem !", inline=False)
    embed.add_field(name=f"🌐 {prefix}geoip <mot-clé>", value="Voir les infos d'une IP.", inline=False)
    embed.add_field(name=f"📊 Commandes de Statistiques :", value="\n", inline=False)
    embed.add_field(name=f"📈 {prefix}stats", value="Affiche les statistiques du serveur.", inline=False)
    embed.add_field(name=f"🤖 {prefix}botinfo", value="Affiche les informations sur le bot.", inline=False)
    embed.set_footer(text="lookdb remade by cyb3rtech")
    await ctx.send(embed=embed)
    
#############################################

@bot.command(name="ping")
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.send(f"Ping : {int(latency)}ms")
    
#############################################

@bot.command(name="players")
async def players(ctx):
    dump_folder_path = "dump"
    database_folder_path = "database"

    total_lines_dump = 0
    total_lines_database = 0

    for filename in os.listdir(dump_folder_path):
        file_path = os.path.join(dump_folder_path, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    lines_count = sum(1 for line in file)
                    total_lines_dump += lines_count
            except Exception as e:
                await ctx.send(f"Erreur lors de la lecture du fichier {filename}: {e}")

    for filename in os.listdir(database_folder_path):
        file_path = os.path.join(database_folder_path, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    lines_count = sum(1 for line in file)
                    total_lines_database += lines_count
            except Exception as e:
                await ctx.send(f"Erreur lors de la lecture du fichier {filename}: {e}")

    embed = discord.Embed(title="📊 Statistiques des lignes", description="Voici les statistiques actuelles :")
    embed.add_field(name="📁 Base de données (DB)", value=f"{total_lines_database} ligne(s)", inline=False)
    embed.add_field(name="🚗 Fichiers Fivem", value=f"{total_lines_dump} ligne(s)", inline=False)

    await ctx.send(embed=embed)
    
#############################################
    
@bot.command(name="lookup")
async def lookup(ctx, discord_id: str):
    embed = discord.Embed(title="Recherche en cours...", description="Veuillez patienter...", color=0xFFA500)
    message = await ctx.send(embed=embed)

    lookup_results = await search_in_database(discord_id, ctx, embed)
    if not lookup_results:
        lookup_results = await search_in_db(discord_id, ctx, embed)

    try:
        await update_lookup_embed(ctx, message, discord_id, lookup_results)
    except discord.errors.Forbidden:
        await ctx.send("Impossible d'envoyer un message privé. Veuillez vérifier vos paramètres de confidentialité.")

@bot.command(name="vip")
async def vip(ctx, discord_id: str):
    user_id = str(ctx.author.id)

    with open("bls.txt", "r") as bls_file:
        if discord_id in bls_file.read():
            embed = discord.Embed(title="Erreur", description=f"L'utilisateur avec l'ID Discord {discord_id} est sur la liste noire.", color=0xED4245)
            embed.set_footer(text="lookdb remade by cyb3rtech")
            await ctx.send(embed=embed)
            return

    embed = discord.Embed(title=f"Recherche VIP en cours pour {discord_id}", color=0x57F287)
    embed.add_field(name="Recherche en cours...", value="Veuillez patienter...", inline=False)
    message = await ctx.send(embed=embed)

    search_result_dump = await search_in_db(discord_id, ctx, embed)
    search_result_database = await search_in_database(discord_id, ctx, embed)

    combined_results = search_result_dump + search_result_database

    if not combined_results:
        embed = discord.Embed(title=f"🔍 Aucun résultat trouvé pour Discord ID : {discord_id}", color=0xED4245)
        embed.set_footer(text="lookdb remade by cyb3rtech")
        embed.set_thumbnail(url=ctx.author.avatar.url)
        await message.edit(content='', embed=embed)
        return

    current_page = 0

    async def update_embed(page):
        result = combined_results[page]
        server_name = os.path.splitext(os.path.basename(result['filename']))[0]
        embed = discord.Embed(title=f"🔍 Résultats pour Discord ID : {discord_id}", color=0x57F287)
        embed.add_field(name="📌 **Nom du serveur**", value=server_name, inline=False)
        embed.add_field(name="📋 **Nom**", value=f"{result['name']}", inline=False)
        embed.add_field(name="<:discord:1257773225790672906> **Discord ID**", value=f"{discord_id}", inline=False)
        embed.add_field(name="<:steam:1257773282665697405>  **Steam ID**", value=f"{result.get('steam_id', 'Aucune données')}" if len(result.get('steam_id', '')) > 1 else ' Aucune données', inline=False)
        embed.add_field(name="<:xbox:1257773308905259048> **Xbox Live ID**", value=f"{result.get('xbl_id', 'Aucune données')}" if len(result.get('xbl_id', '')) > 1 else ' Aucune données', inline=False)
        embed.add_field(name="<:microsoft:1257773324818317463> **Microsoft Live ID**", value=f"{result.get('live_id', 'Aucune données')}" if len(result.get('live_id', '')) > 1 else ' Aucune données', inline=False)
        embed.add_field(name="<:fivem:1257773345357955072> **FiveM ID**", value=f"{result.get('fivem_id', 'Aucune données')}" if len(result.get('fivem_id', '')) > 1 else ' Aucune données', inline=False)
        embed.add_field(name="<:dossier:1257773357458395186> **Licence ID**", value=f"{result.get('license_id', 'Aucune données')}" if len(result.get('license_id', '')) > 1 else ' Aucune données', inline=False)
        embed.add_field(name="<:dossier:1257773357458395186> **Licence 2 ID**", value=f"{result.get('license2_id', 'Aucune données')}" if len(result.get('license2_id', '')) > 1 else ' Aucune données', inline=False)
        embed.add_field(name="<:ip:1257778397094875218> **IP**", value=f"`{result.get('ip_address', 'Aucune données')}`" if len(result.get('ip_address', '')) > 1 else ' Aucune données', inline=False)
        embed.set_footer(text=f"Page {page + 1}/{len(combined_results)} - lookdb remade by cyb3rtech")
        return embed

    await message.edit(embed=await update_embed(current_page))

@bot.command(name="geoip")
async def geoip(ctx, *, ip_address: str):

    print(f"{prefix}geoip : {ip_address}")
    
    ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    if not ip_pattern.match(ip_address):
        await ctx.send("Adresse IP invalide.")
        return
    
    try:
        geoip_info = await get_geoip_info(ip_address)
        if not geoip_info:
            await ctx.send("Impossible de récupérer les informations de localisation pour cette adresse IP.")
            return
        
        embed = discord.Embed(title=f"Informations pour l'adresse IP : {ip_address}")
        embed.add_field(name="IP", value=ip_address)
        embed.add_field(name="Ville", value=geoip_info.get('city', 'Non disponible'), inline=False)
        embed.add_field(name="Région", value=geoip_info.get('region', 'Non disponible'), inline=False)
        embed.add_field(name="Pays", value=geoip_info.get('country', 'Non disponible'), inline=False)
        embed.add_field(name="Organisation", value=geoip_info.get('org', 'Non disponible'), inline=False)
        embed.set_footer(text="lookdb remade by cyb3rtech")
        await ctx.send(f"Consultez vos MP, je vous ai envoyé les détails pour l'adresse IP: {ip_address}, {ctx.author.mention} .")
        await ctx.author.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {e}")
        
#############################################

@bot.command(name="stats")
async def stats(ctx):
    if not ctx.guild:
        await ctx.send("Cette commande ne peut être utilisée que dans un serveur.")
        return
        
    total_members = ctx.guild.member_count
    online_members = sum(member.status != discord.Status.offline for member in ctx.guild.members)
    voice_channels = sum(1 for channel in ctx.guild.voice_channels if len(channel.members) > 0)
    bot_count = sum(1 for member in ctx.guild.members if member.bot)
    boost_count = ctx.guild.premium_subscription_count
    embed = discord.Embed(title="📊 Statistiques du serveur", description="Voici les statistiques actuelles du serveur.", color=0x57F287)
    embed.add_field(name="👥 Nombre total de membres", value=str(total_members), inline=False)
    embed.add_field(name="🟢 Membres en ligne", value=str(online_members), inline=False)
    embed.add_field(name="🔊 Membres en vocal", value=str(voice_channels), inline=False)
    embed.add_field(name="🤖 Nombre de bots", value=str(bot_count), inline=False)
    embed.add_field(name="✨ Nombre de boosts", value=str(boost_count), inline=False)
    embed.set_footer(text="lookdb remade by cyb3rtech")

    await ctx.send(embed=embed)
    
#############################################

@bot.command(name="botinfo")
async def botinfo(ctx):
    embed = discord.Embed(title="🤖 Informations sur le bot", description="Voici quelques informations sur ce bot.", color=0x57F287)
    embed.add_field(name="Créateur", value="Antidatabreach", inline=False)
    embed.add_field(name="Langage", value="Python (discord.py)", inline=False)
    embed.add_field(name="Description", value="Un bot Discord pour gérer les recherches et statistiques des bases de données Fivem.", inline=False)
    embed.set_footer(text="lookdb remade by cyb3rtech")
    
    await ctx.send(embed=embed)
    
#############################################

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_dark_red(r""" ▄████▄▓██   ██▓ ▄▄▄▄   ▓█████  ██▀███  ▄▄▄█████▓▓█████  ▄████▄   ██░ ██ 
▒██▀ ▀█ ▒██  ██▒▓█████▄ ▓█   ▀ ▓██ ▒ ██▒▓  ██▒ ▓▒▓█   ▀ ▒██▀ ▀█  ▓██░ ██▒
▒▓█    ▄ ▒██ ██░▒██▒ ▄██▒███   ▓██ ░▄█ ▒▒ ▓██░ ▒░▒███   ▒▓█    ▄ ▒██▀▀██░
▒▓▓▄ ▄██▒░ ▐██▓░▒██░█▀  ▒▓█  ▄ ▒██▀▀█▄  ░ ▓██▓ ░ ▒▓█  ▄ ▒▓▓▄ ▄██▒░▓█ ░██ 
▒ ▓███▀ ░░ ██▒▓░░▓█  ▀█▓░▒████▒░██▓ ▒██▒  ▒██▒ ░ ░▒████▒▒ ▓███▀ ░░▓█▒░██▓
░ ░▒ ▒  ░ ██▒▒▒ ░▒▓███▀▒░░ ▒░ ░░ ▒▓ ░▒▓░  ▒ ░░   ░░ ▒░ ░░ ░▒ ▒  ░ ▒ ░░▒░▒
  ░  ▒  ▓██ ░▒░ ▒░▒   ░  ░ ░  ░  ░▒ ░ ▒░    ░     ░ ░  ░  ░  ▒    ▒ ░▒░ ░
░       ▒ ▒ ░░   ░    ░    ░     ░░   ░   ░         ░   ░         ░  ░░ ░
░ ░     ░ ░      ░         ░  ░   ░                 ░  ░░ ░       ░  ░  ░
░       ░ ░           ░                                 ░                """)

    print_dark_blue("\n                    Remade By Cyb3rtech                  \n")  
    print_dark_red(f"❮+❯・{bot.user.name} est en ligne !")
    print_dark_red("❮+❯・discord : https://discord.gg/HBVt4vZ77g")
    bot.loop.create_task(monitor_servers())
    
    await bot.change_presence(activity=discord.Streaming(name="Remade By Cyb3rtech", url="https://www.twitch.tv/cyb3rtech_kdo"))

bot.run(token)
