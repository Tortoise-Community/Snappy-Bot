from discord import Color

tortoise_guild_id = 577192344529404154
website_url = "https://www.tortoisecommunity.org/"
events_url = "https://www.tortoisecommunity.org/events"
rules_url = "https://www.tortoisecommunity.org/rules"
verification_url = "https://www.tortoisecommunity.org/verification/"
github_repo_link = "https://github.com/Tortoise-Community/Tortoise-BOT"
tortoise_paste_service_link = "https://paste.tortoisecommunity.org/"
tortoise_paste_endpoint = "https://paste.tortoisecommunity.org/documents/"
line_img_url = "https://cdn.discordapp.com/attachments/649868379372388352/723173852796158062/animated-line.gif"
github_repo_stats_endpoint = "https://api.github.com/repos/Tortoise-Community/"
project_url = "https://www.tortoisecommunity.org/pages/projects/"

# Channel IDs
welcome_channel_id = 738731842538176522
announcements_channel_id = 578197131526144024
react_for_roles_channel_id = 603651772950773761

mod_mail_report_channel_id = 693790120712601610
bug_reports_channel_id = 693790120712601610
code_submissions_channel_id = 610079185569841153
suggestions_channel_id = 708734512296624239

# Log Channel IDs
system_log_channel_id = 593883395436838942
deterrence_log_channel_id = 597119801701433357
bot_log_channel_id = 693090079329091615
successful_verifications_channel_id = 581139962611892229
verification_channel_id = 602156675863937024
website_log_channel_id = 649868379372388352
bot_dev_channel_id = 692851221223964822
error_log_channel_id = 690650346665803777
member_count_channel_id = 723526255495872566
general_channel_id = 577192344533598472
staff_channel_id = 580809054067097600

# Roles
muted_role_id = 707007421066772530
verified_role_id = 599647985198039050
trusted_role_id = 703657957438652476
moderator_role = 577368219875278849
admin_role = 577196762691928065
new_member_role = 1441848294828670978

# Keys are IDs of reaction emojis
# Values are role IDs which will get added if that reaction gets added/removed
self_assignable_roles = {
    582547250635603988: 589128905290547217,     # Python
    603276263414562836: 589129320480636986,     # Javascript
    723277556459241573: 591254311162347561,     # HTML/CSS
    723274176991068261: 589131126619111424,     # SQL
    603275563972689942: 589131022520811523,     # C
    603275529587654665: 589129873809735700,     # C++
    723280469122089131: 589130125208190991,     # C#
    723272019126255726: 589129070609039454,     # Java
    723276957810163731: 589129583375286415,     # R
    610825682070798359: 610834658267103262,     # events
    583614910215356416: 603157798225838101,     # announcements
    782187224195268629: 781210603997757471      # challenges
}


# Emoji IDs
mod_mail_emoji_id = 706195614857297970
event_emoji_id = 611403448750964746
bug_emoji_id = 723274927968354364
suggestions_emoji_id = 613185393776656384
verified_emoji_id = 610713784268357632
upvote_emoji_id = 741202481090002994
hit_emoji_id = 755715814883196958
stay_emoji_id = 755717238732095562
double_emoji_id = 755715816657518622
blank_card_emoji = "<:card:755715225642336287>"

# Badges
partner = "<:partner:753957703155449916>"
staff = "<:staff:753957681336942673>"
nitro = "<:nitro:753957661912989747>"
hs_bal = "<:balance:753957264460873728>"
hs_bril = "<:brilliance:753957311537479750>"
hs_brav = "<:bravery:753957296475996234>"
hs_ev = "<:events:753957640069185637>"
verified_bot_dev = "<:dev:753957609328869384>"
bg_1 = "<:bug1:753957385844031538>"
bg_2 = "<:bug2:753957425664753754>"
ear_supp = "<:early:753957626097696888>"

# Emotes
idle = "🌙"
game_emoji = "🎮"
online = "<:online:753999406562410536>"
offline = "<:offline:753999424446922782>"
dnd = "<:dnd:753999445728952503>"
spotify_emoji = "<:spotify:754238046123196467>"
tick_yes = "<:tickyes:758291659330420776>"
tick_no = "<:tickno:753974818549923960>"
pin_emoji = "<:pinunread:754233175244537976>"
user_emoji = "<:user:754234411922227250>"
git_start_emoji = "<:git_star:758616139646763064>"
git_fork_emoji = "<:git_fork:758616130780004362>"
git_commit_emoji = "<:git_commit:758616123590574090>"
git_repo_emoji = "<:repo:758616137977561119>"
success_emoji = "<:success:781891698590482442>"
failure_emoji = "<:failure:1443554881196789780>"




# Special
tortoise_developers = (197918569894379520, 612349409736392928)

# Embeds are not monospaced so we need to use spaces to make different lines "align"
# But discord doesn't like spaces and strips them down.
# Using a combination of zero width space + regular space solves stripping problem.
embed_space = "\u200b "

# After this is exceeded the link to tortoise paste service should be sent
max_message_length = 1000






