# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


from __future__ import unicode_literals

import errno
import os
import sys
import tempfile
from argparse import ArgumentParser

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)
import time

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='Display Name: ' + profile.display_name
                    ),
                    TextSendMessage(
                        text='Status : ' + profile.status_message
                    )
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="Bot can't use profile API without user ID"))
            
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text='I\'ll be back ....'))
            text_message = TextSendMessage(text='testers!')
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text='Fine'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="Leave me yourself"))
            
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[
            MessageTemplateAction(label='Yes', text='Yes!'),
            MessageTemplateAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='''YoRHa's Request''', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
##    elif text == 'view profiles' :
##        profile = line_bot_api.get_group_member_profile(group_id, user_id)
##        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=profile.display_name))
##        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=profile.user_id))
##        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=profile.picture_url))
    elif (text.split())[0] == 'sendto' :
        lineID = (text.split())[1]
        message = (text.split())[2]
        try:
            target = client._client.findContactByUserid(lineID)
            c = LineContact(client, target)
            c.sendMessage(message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Error'))
            
    elif text == 'buttons':
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                URITemplateAction(
                    label='Go to line.me', uri='https://line.me'),
                PostbackTemplateAction(label='ping', data='ping'),
                PostbackTemplateAction(
                    label='ping with text', data='ping',
                    text='ping'),
                MessageTemplateAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='''YoRHa's Request''', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
        
    elif text == 'carousel':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URITemplateAction(
                    label='Go to line.me', uri='https://line.me'),
                PostbackTemplateAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackTemplateAction(
                    label='ping with text', data='ping',
                    text='ping'),
                MessageTemplateAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'image_carousel':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerTemplateAction(label='datetime',
                                                                    data='datetime_postback',
                                                                    mode='datetime')),
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerTemplateAction(label='date',
                                                                    data='date_postback',
                                                                    mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'imagemap':
        pass
    elif text == 'YoRHa' :
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='For the Glory of Mankind'))
    elif text == '@emi[L]' :
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Summoned...'))
    elif text.lower() == ('hai' or 'hello' or 'pagi' or 'pagii' or 'malam' or 'siang') or ('selamat' in text.lower()) :
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text + 'juga :D'))
	elif text == '7 First Kisses' :
		tosend = '''[SEVEN FIRST KISSES]
Link Sharing by 9S

Episode 1 : https://www.youtube.com/watch?v=PUBrXIikG9k
Episode 2 : https://www.youtube.com/watch?v=_3n3aapyn3g
Episode 3 : https://www.youtube.com/watch?v=xl6FE4xBx7Y
Episode 4 : https://www.youtube.com/watch?v=dAr8bxgHhvo
Episode 5 : https://www.youtube.com/watch?v=fzoQJSAYvLY
Episode 6 : https://www.youtube.com/watch?v=-wkXXkFPcJ4
Episode 7 : https://www.youtube.com/watch?v=qXGf2VAHw28
Episode 8 : https://www.youtube.com/watch?v=jv37Kt5u8WI

~ End at Eps 8 ~'''
		line_bot_api.reply_message(event.reply_token, TextSendMessage(text=tosend))
    elif text == 'info' :
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='still in development, here\'s some command :\n \
                                                                      profile\n\
                                                                      bye\n\
                                                                      confirm (RAW)\n\
                                                                      sendto (ERROR)\n\
                                                                      buttons (RAW)\n\
                                                                      carousel (RAW) \n\
                                                                      image_carousel (RAW) \n\
                                                                      imagemap (RAW) \n\
                                                                      YoRHa \n\
                                                                      @emi[L] \n\
                                                                      info (Untested'))
##    elif text == 'echo on' :
##        echi_switch(on
##    else:
##        line_bot_api.reply_message(
##            event.reply_token, TextSendMessage(text=event.message.text))
##
##def echo_switch(settings) :
##    
##
##@handler.add(MessageEvent, message=LocationMessage)
##def handle_location_message(event):
##    line_bot_api.reply_message(
##        event.reply_token,
##        LocationSendMessage(
##            title=event.message.title, address=event.message.address,
##            latitude=event.message.latitude, longitude=event.message.longitude
##        )
##    )
##
##
##@handler.add(MessageEvent, message=StickerMessage)
##def handle_sticker_message(event):
##    line_bot_api.reply_message(
##        event.reply_token,
##        StickerSendMessage(
##            package_id=event.message.package_id,
##            sticker_id=event.message.sticker_id)
##    )
##
##
### Other Message Type
##@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
##def handle_content_message(event):
##    if isinstance(event.message, ImageMessage):
##        ext = 'jpg'
##    elif isinstance(event.message, VideoMessage):
##        ext = 'mp4'
##    elif isinstance(event.message, AudioMessage):
##        ext = 'm4a'
##    else:
##        return
##
##    message_content = line_bot_api.get_message_content(event.message.id)
##    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
##        for chunk in message_content.iter_content():
##            tf.write(chunk)
##        tempfile_path = tf.name
##
##    dist_path = tempfile_path + '.' + ext
##    dist_name = os.path.basename(dist_path)
##    os.rename(tempfile_path, dist_path)
##
##    line_bot_api.reply_message(
##        event.reply_token, [
##            TextSendMessage(text='Entering Storage\nPlease Wait'),
##            time.sleep(1),
##            TextSendMessage(text='Media has been saved'),
##            TextSendMessage(text='link : ' + request.host_url + os.path.join('static', 'tmp', dist_name))
##        ])
##
##
##@handler.add(MessageEvent, message=FileMessage)
##def handle_file_message(event):
##    message_content = line_bot_api.get_message_content(event.message.id)
##    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
##        for chunk in message_content.iter_content():
##            tf.write(chunk)
##        tempfile_path = tf.name
##
##    dist_path = tempfile_path + '-' + event.message.file_name
##    dist_name = os.path.basename(dist_path)
##    os.rename(tempfile_path, dist_path)
##
##    line_bot_api.reply_message(
##        event.reply_token, [
##            TextSendMessage(text='Entering Storage\nPlease Wait'),
##            time.sleep(1),
##            TextSendMessage(text='File has been saved'),
##            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
##        ])
##
##
##@handler.add(FollowEvent)
##def handle_follow(event):
##    line_bot_api.reply_message(
##        event.reply_token, TextSendMessage(text='Got follow event'))
##
##
##@handler.add(UnfollowEvent)
##def handle_unfollow():
##    app.logger.info("Got Unfollow event")
##

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Hello :D')) # + event.source.type)) return room / group


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))


@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message( event.reply_token,
                                TextSendMessage(text='Got beacon event. hwid={}, device_message(hex string)={}'
                                                .format(event.beacon.hwid, event.beacon.dm)))
    
if __name__ == "__main__":
    arg_parser = ArgumentParser(        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    
    # create tmp dir for download content
    make_static_tmp_dir()
    
    app.run(host='0.0.0.0', debug=options.debug, port=int(os.environ.get('PORT' , 5000)))
