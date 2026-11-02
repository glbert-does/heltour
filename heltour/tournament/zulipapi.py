import logging
from datetime import datetime
from time import sleep

import pytz
from django.conf import settings
from zulip import Client, ZulipError

from heltour.tournament.chatclient import ChatClient
from heltour.tournament.slackapi import SlackGroup, SlackUser

logger = logging.getLogger(__name__)


class ZulipClient(ChatClient):
    def __init__(self, zulip_env: str):
        self.client = Client(config_file=zulip_env, client="ZulipHeltour")
        register = self.client.register(event_types=["realm"])
        if not register["result"] == "success":
            raise ZulipError(f"ERROR in getting client register: {register['msg']}")
        else:
            try:
                self.max_topic_length = register["max_topic_length"]
                self.max_message_length = register["max_message_length"]
                self.max_stream_name_length = register["max_stream_name_length"]
                self.max_stream_description_length = register[
                    "max_stream_description_length"
                ]
            except KeyError:
                logger.error(
                    "ERROR: Realm response does not contain zulip server setting for "
                    "max lengths of topics/message/stream_name/stream_description"
                )
                raise ZulipError("Realm settings missing")

#    def _retry_once_on_rate_limit(self, fct: callable, **kwargs):
#        r = fct(kwargs)
#        if r["result"] != "success":
#            if r["code"] == "RATE_LIMIT_HIT":
#                time.sleep(r[])
#                r = fct(kwargs)
#        return r

    def _message(self, channel: str|int, channel_type: str, text: str, topic: str="(no topic)", tries: int=0) -> None:
        if len(topic) > self.max_topic_length:
            logger.warning(
                f"topic length exceeds max_topic_length {self.max_topic_length}, cutting it."
            )
            topic = topic[:self.max_topic_length]
        if len(text) > self.max_message_length:
            logger.warning(
                "message length exceeds max_message_length "
                f"{self.max_message_length}, cutting it."
            )
            text = text[:self.max_message_length]
        if channel_type == "channel":
            params = {
                "type": channel_type,
                "to": channel[1:]
                if not isinstance(channel, int) and "#" in channel
                else channel,
                "content": text,
                "topic": topic,
            }
        elif channel_type == "direct":
            params = {
                "type": channel_type,
                "to": channel,
                "content": text,
            }
        else:
            raise ZulipError(f'Unkown channel_type "{channel_type}"')
        r = self.client.send_message(params)
        if r["result"] != "success":
            if (
                settings.ZULIP_ERROR_LOGGING
                and f"{channel}>{topic}" != settings.ZULIP_ERROR_LOG
            ):  # prevent trying to send errors about failed error messages to prevent infinite recursion when zulip is down or something
                self._send_message(
                    channel=settings.ZULIP_ERROR_LOG,
                    text=(
                        f"Could not send message to {channel}>{topic}.\n"
                    f"Error Code: {r['code']}\nError msg: {r['msg']}"
                 ),
                )
            logger.error(f"Could not send message to {channel}>{topic}, error:\n{r['msg']}")
            if r["code"] == "RATE_LIMIT_HIT" and tries < 1:
                sleep(settings.SLEEP_UNIT * r["retry-after"])
                self._message(
                    channel=channel,
                    channel_type=channel_type,
                    text=text,
                    topic=topic,
                    tries=tries + 1,
                )
            elif r["code"] == "RATE_LIMIT_HIT":
                logger.error(f"Hit Rate Limit twice, giving up.\nmsg: {r['msg']}\nretry: {r['retry-after']}")
                raise ZulipRateLimitHit(message=r["msg"], wait=r["retry-after"])
            else:
                raise ZulipError(r["msg"])
        else:
            logger.info(f"Zulip [{channel} > {topic}]: {text}")

    def _send_message(self, channel, text, topic="(no topic)"):
        if not isinstance(channel, int) and ">" in channel:
            channel_split = channel.partition(">")
            self._message(
                channel=channel_split[0],
                channel_type="channel",
                text=text,
                topic=channel_split[2],
            )
        else:
            self._message(channel=channel, channel_type="channel", text=text, topic=topic)

    def _send_direct_message(self, users, text):
        self._message(channel=users, channel_type="direct", text=text, topic="")

    def bold(self, text: str) -> str:
        return f"**{text}**"

    def channellink(
        self,
        channel: str,
        channelprefix: str = "#",
        channelid: str = "",
        topic: str = "",
    ) -> str:
        if topic:
            return f"{channelprefix}**{channel}>{topic}**"
        else:
            return f"{channelprefix}**{channel}**"

    def chatbackend(self) -> str:
        return "Zulip"

    def chatbaceknd_render(self) -> bool:
        return True

    def chatbackend_url(self) -> str:
        return settings.ZULIP_URL

    def dm_link(self, usernames: list[str], userids: list[str], add_bot: bool) -> str:
        if add_bot:
            userids.append(settings.ZULIP_LISTENING_BOT)
        users = ",".join(str(u) for u in userids)
        return f"{settings.ZULIP_URL}/#narrow/dm/{users}-group"

    def inlinecode(self, text: str) -> str:
       return f"`{text}`"

    def italic(self, text: str) -> str:
        return f"*{text}*"

    def link(self, text: str, url: str) -> str:
        return f"[{text}]({url})"

    def ping_mods(self) -> str:
        return "@*mods4545*"

    def userlink_ping(self, user: str) -> str:
        return f"@**{user}**"

    def userlink_silent(self, user: str) -> str:
        return f"@_**{user}**"

    def channel_message(
        self, channel: str, text: str, topic: str = "(no topic)") -> None:
        self._send_message(channel=channel, text=text, topic=topic)

    def send_control_message(self, text: str) -> None:
        self.channel_message(channel="msg-forward", channel_type="channel", text=text, topic="control")

    def direct_user_message(
        self, username: str, text: str, userid: str
    ) -> None:
        self._send_direct_message(users=[int(userid)], text=text)

    def multiple_user_message(
        self, usernames: list[str], text: str, userids: list[str]
    ) -> None:
        userids_int = list(map(int, userids))
        userids_int.append(settings.ZULIP_LISTENING_BOT)
        self._send_direct_message(users=userids_int, text=text)

    def cb_create_team_channel(
        self,
        team,
        channel_name: str,
        user_ids: list[str],
        topic: str,
        intro_message: str,
    ) -> None:

        user_ids_ext = list(map(int, user_ids))
        user_ids_ext.extend([settings.ZULIP_LISTENING_BOT, settings.ZULIP_HELTOUR_BOT])
        try:
            channel = zulipapi.create_channel(
                channel_name=channel_name,
                user_ids=user_ids_ext,
                topic=topic,
                invite_only=True,
                history_public=False,
                can_add_subscribers_ids=user_ids_ext,
                can_remove_subscribers_ids=user_ids_ext,
                can_admin_channel_ids=user_ids_ext,
            )
        except zulipapi.ZulipRateLimitHit as e:
            if tries < 1:
                logger.error(
                    "Error: Hit Rate Limit. "
                    f"Waiting for {e.wait + 10} seconds before retrying once."
                )
                sleep(settings.SLEEP_UNIT * (e.wait + 10))
                channel = create_team_channel(
                    team=team,
                    channel_name=channel_name,
                    user_ids=user_ids,
                    topic=topic,
                    intro_message=intro_message,
                    tries=1,
                )
            else:
                logger.error(f"Error: Hit Rate limit twice. Giving up.\n{e.message}")
                return
        except zulipapi.ZulipError as e:
            logger.error(
                "Could not create slack team, name probably taken: "
                f"{channel_name}\nError msg: {e}"
            )
            return
        with reversion.create_revision():
            reversion.set_comment("Creating zulip channel")
            team.slack_channel = channel.id
            team.save()
        channel_message(channel=int(channel.id), text=intro_message, topic="Welcome!")
        sleep(settings.SLEEP_UNIT)

def invite_user(email, *args, **kwargs):
    params = {
        "invitee_emails": email,
        "invite_expires_in_minutes": 60 * 24 * 7 * 4,  # 4 weeks
        "invite_as": 600,  # 600: guest, 400: member
        "stream_ids": [],  # none, because we can modify default_subscriptions easily, and we do not have any special invitees
        "include_realm_default_subscriptions": "true",
        "notify_referrer_on_join": "false",
    }
    try:
        human_client = Client(
            config_file=settings.ZULIP_CONFIG_NOBOT, client="ZulipHeltour"
        )
    except ZulipError as e:
        raise ZulipError(f"ERROR connecting human client for user invitations: {e}")
        return
    r = human_client.call_endpoint(url="/invites", method="POST", request=params)
    if r["result"] != "success":
        if settings.ZULIP_ERROR_LOGGING:
            send_message(
                channel=settings.ZULIP_ERROR_LOG,
                text=(
                    (
                        f"Could not invite {email}\nError Code: "
                        f"{r['code']}\nError msg: {r['msg']}"
                    ),
                ),
            )
        if r["code"] == "INVITATION_FAILED":
            raise AlreadyInTeamError(r["msg"])
        elif r["code"] == "BAD_REQUEST":
            raise BadRequestError(r["msg"])
        elif r["code"] == "RATE_LIMIT_HIT":
            raise ZulipRateLimitHit(message=r["msg"], wait=r["retry-after"])
        else:
            raise ZulipError(r["msg"])
    else:
        logger.info(f"Zulip: invited {email} to zulip")

    def channel_message(
        self, channel: str, text: str, topic: str = "(no topic)", tries: int = 0
    ) -> None:
        try:
            zulipapi.send_message(channel=channel, text=text, topic=topic)
        except zulipapi.ZulipRateLimitHit as e:
            if tries < 1:
                logger.error(
                    "Error: Hit Rate Limit. "
                    f"Waiting for {2*e.wait} seconds before retrying once."
                )
                sleep(settings.SLEEP_UNIT * e.wait)
                channel_message(channel=channel, text=text, topic=topic, tries=1)
            else:
                logger.error(f"Error: Hit Rate Limit twice. Giving up.\n{e.message}")
        except zulipapi.ZulipError as e:
            logger.error(f"Error sending Zulip message:\n{e}")


def get_user_list():
    r = _client.get_users()
    if not r["result"] == "success":
        if settings.ZULIP_ERROR_LOGGING:
            send_message(
                channel=settings.ZULIP_ERROR_LOG,
                text=(
                    "Could not retrieve user list.\n"
                    f"Error Code: {r['code']}\nError msg: {r['msg']}"
                ),
            )
        if r["code"] == "RATE_LIMIT_HIT":
            raise ZulipRateLimitHit(message=r["msg"], wait=r["retry-after"])
        else:
            raise ZulipError(r["msg"])
    result = []
    for m in r["members"]:
        tz = m.get("timezone")
        if tz:
            tzseconds = (
                pytz.timezone(tz).localize(datetime.now()).utcoffset().total_seconds()
            )
        else:
            tzseconds = 0.0
        result.append(
            SlackUser(
                id=str(m.get("user_id")),
                display_name=m.get("full_name"),
                email=m.get("delivery_email"),
                tz_offset=tzseconds,
                name_deprecated="",
                real_name="",
            )
        )
    return result


def get_user(user_id):
    r = _client.get_user_by_id(user_id)
    if not r["result"] == "success":
        if settings.ZULIP_ERROR_LOGGING:
            send_message(
                channel=settings.ZULIP_ERROR_LOG,
                text=(
                    f"Could not retrieve user {user_id}.\n"
                    f"Error Code: {r['code']}\nError msg: {r['msg']}"
                ),
            )
        if r["code"] == "RATE_LIMIT_HIT":
            raise ZulipRateLimitHit(message=r["msg"], wait=r["retry-after"])
        else:
            raise ZulipError(r["msg"])
    m = r["user"]
    tz = m.get("timezone")
    if tz:
        tzseconds = (
            pytz.timezone(m.get("timezone"))
            .localize(datetime.now())
            .utcoffset()
            .total_seconds()
        )
    else:
        tzseconds = 0.0
    return SlackUser(
        id=str(m.get("user_id")),
        display_name=m.get("full_name"),
        email=m.get("email"),
        tz_offset=tzseconds,
        name_deprecated="",
        real_name="",
    )




def send_forward_message(*, channel, text):
    _message(
        channel="msg-forward",
        channel_type="channel",
        text=f"forward to {channel}\n>{text}",
        topic="logging",
    )


def send_direct_message(*, users, text):
    _message(channel=users, channel_type="direct", text=text, topic="")


def _get_channel_id(channel_name):
    r = _client.get_stream_id(channel_name)
    if r["result"] != "success":
        if r["code"] == "RATE_LIMIT_HIT":
            raise ZulipRateLimitHit(message=r["msg"], wait=r["retry-after"])
        else:
            raise ZulipError(r["msg"])
    return r["stream_id"]


def create_channel(
    channel_name,
    user_ids,
    topic="",
    invite_only=True,
    history_public=False,
    can_add_subscribers_ids=[],
    can_add_subscribers_groups=[],
    can_remove_subscribers_ids=[],
    can_remove_subscribers_groups=[],
    can_admin_channel_ids=[],
    can_admin_channel_groups=[],
):
    if len(channel_name) > _max_stream_name_length:
        logger.warning(
            "channel name length exceeds max_stream_name_length "
            f"{_max_stream_name_length}, cutting it."
        )
        channel_name = channel_name[:_max_stream_name_length]
    if len(topic) > _max_stream_description_length:
        logger.warning(
            "channel description length exceeds max_stream_description_length "
            f"{_max_stream_description_length}, cutting it."
        )
        topic = topic[:_max_stream_description_length]
    if topic:
        stream = [
            {
                "name": channel_name,
                "description": topic,
                "invite_only": invite_only,
                "history_public_to_subscribers": history_public,
            }
        ]
    else:
        stream = [
            {
                "name": channel_name,
                "invite_only": invite_only,
                "history_public_to_subscribers": history_public,
            }
        ]
    r = _client.add_subscriptions(
        streams=stream,
        principals=user_ids,
        invite_only=invite_only,
        history_public_to_subscribers=history_public,
        can_add_subscribers_group={
            "direct_members": can_add_subscribers_ids,
            "direct_subgroups": can_add_subscribers_groups,
        },
        can_remove_subscribers_group={
            "direct_members": can_remove_subscribers_ids,
            "direct_subgroups": can_remove_subscribers_groups,
        },
        can_administer_channel_group={
            "direct_members": can_admin_channel_ids,
            "direct_subgroups": can_admin_channel_groups,
        },
    )
    if r["result"] != "success":
        if settings.ZULIP_ERROR_LOGGING:
            send_message(
                channel=settings.ZULIP_ERROR_LOG,
                text=(
                    f"Could not create channel {channel_name} for user ids {user_ids}.\n"
                    f"Error Code: {r['code']}\nError msg: {r['msg']}"
                ),
            )
        if r["code"] == "RATE_LIMIT_HIT":
            raise ZulipRateLimitHit(message=r["msg"], wait=r["retry-after"])
        else:
            raise ZulipError(r["msg"])
    channel_id = _get_channel_id(channel_name)
    return SlackGroup(channel_id, channel_name)


def invite_to_group(channel_name, user_ids):
    create_channel(channel_name=channel_name, user_ids=user_ids)


class AlreadyInTeamError(ZulipError):
    pass


class BadRequestError(ZulipError):
    pass


class ZulipRateLimitHit(ZulipError):
    def __init__(self, message, wait, *args):
        self.message = message
        self.wait = wait
        super().__init__(message, wait, *args)
