"""Userge Plugin for getting information about an user on GitHub
Syntax: .github USERNAME
"""
import requests

from userge import userge, Message, Config


@userge.on_cmd("git", about={
    'header': "Get info about an GitHub User",
    'usage': "{tr}git [username]",
    'examples': "{tr}git rzlamrr"})
async def fetch_github_info(message: Message):
    username = message.input_or_reply_str
    url = "https://api.github.com/users/{}".format(username)
    r = requests.get(url)
    if r.status_code == 200:
        b = r.json()
        avatar_url = b["avatar_url"]
        html_url = b["html_url"]
        gh_type = b["type"]
        name = b["name"]
        company = b["company"]
        blog = b["blog"]
        location = b["location"]
        bio = b["bio"]
        followers = b["followers"]
        following = b["following"]
        created_at = b["created_at"]
        await userge.send_photo(
            message.chat.id,
            caption="""Name: [{}]({})
Type: {}
Company: {}
Blog: {}
Location: {}
Bio: {}
Followers: {}
Following: {}
Profile Created: {}""".format(
                name, html_url, gh_type, company, blog, location,
                bio, followers, following, created_at),
            photo=avatar_url,
            disable_notification=True
        )
        await message.delete()
    else:
        await message.edit("No user found with `{}` username!".format(username))