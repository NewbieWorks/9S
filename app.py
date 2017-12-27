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

from time import gmtime, strftime, sleep
import pytz
from datetime import datetime
import string
import random
import smtplib as s
import wikipedia
import dropbox

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

dropboxAcc = os.getenv('DROPBOX_ACCESS_TOKEN', None)
servant = dropbox.Dropbox(dropboxAcc)

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
    text_raw = event.message.text
    text = text_raw.lower()
    text_split=text.split()
    profile = line_bot_api.get_profile(event.source.user_id)

    if isinstance(event.source, SourceUser):
        WITA = pytz.timezone('Asia/Makassar')
        waktu = '{:0>2}:{:0>2}:{:0>2} {}/{}/{}'.format(str(datetime.now(WITA).hour),
                                                     str(datetime.now(WITA).minute),
                                                     str(datetime.now(WITA).second),
                                                     str(datetime.now(WITA).month) ,
                                                     str(datetime.now(WITA).day) ,
                                                     str(datetime.now(WITA).year))
        
        if profile.display_name in hist.keys() :
            hist[profile.display_name] += '\n{} : {}'.format(waktu,text_raw)
        else :
            hist[profile.display_name] = '{} : {}'.format(waktu,text_raw)
            

    if text in ('info','help','/help','keywords','keyword') :
        display ='''[[~Command for 9S~]]
====NewbieWorks====
I Learn New Command Everyday ~~

here's some command :

Profile :
send your display name and status message

Bye :
remove 9S from Group or Room

Echo switch (on/off) :
turn (on/off) the echo

Send mail to <<email>> , <<message>> :
send the message to email from NewbieWorksLineBot@gmail.com

Time :
the answer for 'What time is it?'

Apakah <<question>> ? :
Mirror from Kerang Ajaib bot

Info :
show 9S's Commands


and Other Command Coming up soon
(if my master not too busy watching anime)

admin :
{} '''.format('\n'.join(administrators))
        
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=display))
##
##    elif text == 'set admin' :
##        administrators.append(profile.display_name)
                                                         
    
    elif text == 'profile':
        if isinstance(event.source, SourceUser):
            line_bot_api.reply_message(  event.reply_token,
                                        [TextSendMessage( text='Display Name: ' + profile.display_name    ),
                                         TextSendMessage( text='Status : '      + profile.status_message  )] )
        else:
            line_bot_api.reply_message(  event.reply_token,
                                         TextMessage(text="Bot can't use profile API without user ID"))
    elif text == 'sleep' :
        sleep(5)
        line_bot_api.reply_message(  event.reply_token,
                                         TextMessage(text="I've sleep for 5 second"))
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(event.reply_token,
                                       TextMessage(text='I\'ll be back ....'))
            text_message = TextSendMessage(text='so sad ._.')
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message( event.reply_token, TextMessage(text='Fine') )
            line_bot_api.leave_room(event.source.room_id) 
        else:
            line_bot_api.reply_message( event.reply_token,
                                        TextMessage(text="Leave me yourself, this is 1:1 chat ..."))
            
##    elif text == 'confirm':
##        confirm_template = ConfirmTemplate(text='Do it?',
##                                           actions=[MessageTemplateAction(label='Yes', text='Yes!'),
##                                                    MessageTemplateAction(label='No', text='No!'), ])
##        template_message = TemplateSendMessage(alt_text='''YoRHa's Request''',
##                                               template=confirm_template)
##        line_bot_api.reply_message(event.reply_token, template_message)
##        
##    elif text == 'view profiles' :
##        profile = line_bot_api.get_group_member_profile(group_id, user_id)
##        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=profile.display_name),
##                                                       TextSendMessage(text=profile.user_id),
##                                                       TextSendMessage(text=profile.picture_url)])
##
##    elif text == 'buttons':
##        buttons_template = ButtonsTemplate(
##            title='My buttons sample', text='Hello, my buttons', actions=[
##                URITemplateAction(
##                    label='Go to line.me', uri='https://line.me'),
##                PostbackTemplateAction(label='ping', data='ping'),
##                PostbackTemplateAction(
##                    label='ping with text', data='ping',
##                    text='ping'),
##                MessageTemplateAction(label='Translate Rice', text='米')
##            ])
##        template_message = TemplateSendMessage(alt_text='''YoRHa's Request''', template=buttons_template)
##        line_bot_api.reply_message(event.reply_token, template_message)
##        
##    elif text == 'carousel':
##        carousel_template = CarouselTemplate(columns=[CarouselColumn(text='hoge1',
##                                                                     title='fuga1',
##                                                                     actions=[URITemplateAction(label='Go to line.me' ,
##                                                                                                uri='https://line.me'),
##                                                                              PostbackTemplateAction(label='ping',
##                                                                                                     data='ping')   ]
##                                                                     ),
##                                                      CarouselColumn(text='hoge2',
##                                                                     title='fuga2',
##                                                                     actions=[PostbackTemplateAction(label='ping with text',
##                                                                                                     data='ping',
##                                                                                                     text='ping'),
##                                                                              MessageTemplateAction(label='Translate Rice',
##                                                                                                    text='米')]),])
##        template_message = TemplateSendMessage(alt_text='Carousel alt text',
##                                               template=carousel_template)
##        
##        line_bot_api.reply_message(event.reply_token, template_message)
##        
##    elif text == 'image_carousel':
##        image_carousel_template = ImageCarouselTemplate(columns=
##                                                            [ImageCarouselColumn
##                                                                (image_url='https://via.placeholder.com/1024x1024',
##                                                                 action=DatetimePickerTemplateAction
##                                                                    (label='datetime',
##                                                                     data='datetime_postback',
##                                                                     mode='datetime')
##                                                                 ) ,
##                                                             ImageCarouselColumn
##                                                                (image_url='https://via.placeholder.com/1024x1024',
##                                                                 action=DatetimePickerTemplateAction
##                                                                    (label='date',
##                                                                     data='date_postback',
##                                                                     mode='date')
##                                                                 )
##                                                             ]
##                                                        )
##
##        template_message = TemplateSendMessage(alt_text='ImageCarousel alt text',
##                                               template=image_carousel_template)
##        
##        line_bot_api.reply_message(event.reply_token, template_message)
##
            
    elif 'echo switch' in text: # echo switch (on/off)
        global echo
        
        if 'on' in text :
            echo = False
        elif 'off' in text :
            echo  = True
        
        if echo :
            echo = False
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Echo Off'))
        else :
            echo = True
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Echo On'))

    elif text[0:len('echo:')] == 'echo:':
        toRepeat = text_raw.split(':')[1]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=toRepeat))

    elif echo : ##if echo == True / switchen on
        if profile.display_name in hist.keys() :
            hist[profile.display_name] += '\n{}'.format(text_raw)
        else :
            hist[profile.display_name] = text_raw
            
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text_raw))
        
            
    elif text in sapaan or 'selamat' in text.lower().split() :
        if 'natal' in text :
            pass
        else :
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text.capitalize() + ' juga :D'))

    elif text[:len('send mail to ')] == 'send mail to ' : #send mail to <<email>> , <<message>>
        try :
            splited = text.split()
            sender = 'newbieworkslinebot@gmail.com'
            password = 'nathanaelX1'
            for each in  splited :
                if '@' in splited :
                    receiver = each
            msg = ' '.join(b[b.index(',')+1:])

            server = s.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender,password)
            
            server.sendmail(sender,receiver, msg)
            server.quit()

            line_bot_api.reply_message(event.reply_token, TextMessage(text='Messsage Sended'))
            
        except Exception as e:
            now = str(datetime.now(pytz.utc).year) + '-' + str(datetime.now(pytz.utc).month) + '-' + str(datetime.now(pytz.utc).day)
            bugreport.append((profile.display_name,now,e))
            line_bot_api.reply_message(event.reply_token, TextMessage(text='Error : {}'.format(e)))
                

    elif text == 'time' or text == 'what time is it?':
        WIB = pytz.timezone('Asia/Jakarta')
        WITA = pytz.timezone('Asia/Makassar')
        WIT = pytz.timezone('Asia/Jayapura')
        
        nowWIB = '{:0>2}:{:0>2}:{:0>2} {}/{}/{}'.format(str(datetime.now(WIB).hour),
                                                        str(datetime.now(WIB).minute),
                                                        str(datetime.now(WIB).second),
                                                        str(datetime.now(WIB).month) ,
                                                        str(datetime.now(WIB).day) ,
                                                        str(datetime.now(WIB).year))
        
        nowWITA = '{:0>2}:{:0>2}:{:0>2} {}/{}/{}'.format(str(datetime.now(WITA).hour),
                                                         str(datetime.now(WITA).minute),
                                                         str(datetime.now(WITA).second),
                                                         str(datetime.now(WITA).month) ,
                                                         str(datetime.now(WITA).day) ,
                                                         str(datetime.now(WITA).year))
        
        nowWIT = '{:0>2}:{:0>2}:{:0>2} {}/{}/{}'.format(str(datetime.now(WIT).hour),
                                                        str(datetime.now(WIT).minute),
                                                        str(datetime.now(WIT).second),
                                                        str(datetime.now(WIT).month) ,
                                                        str(datetime.now(WIT).day) ,
                                                        str(datetime.now(WIT).year))
        
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='{:<6s} : {}\n{:<6s}: {}\n{:<6s} : {}'.format('WIB',nowWIB,'WITA',nowWITA,'WIT',nowWIT)))

    elif text[0] == 'note' and text[4] == ':' and isinstance(event.source, SourceGroup) : #note:<<text>>
        global note
        note.append(text[text.find(':'):])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='noted'))

    elif text[:len('wiki sum')] == 'wiki sum': #wiki sub <<text>>
        to_search = text[len('wiki sum')+1:]
        
        try :
            texti = wikipedia.summary(to_search)
        except wikipedia.exceptions.DisambiguationError :
            texti = '{} disambiguation:\n'.format(to_search) + '\n'.join(wikipedia.search(to_search))
        except Exception as e :
            texti = e
        
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=texti))

        
    elif ':' in text and isinstance(event.source, SourceUser):
        try : 
            if text == ':send user' : #:send user #to show who the users
                text_to_send = ', '.join(hist.keys())
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text_to_send))

            elif text[:len('send')] == 'send' : #send:<<name>> #to show user's input
                key = text_raw[text_raw.find(':')+1:]
                hist_to_send = hist[key]
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=hist_to_send))

            elif 'clear' in text : # (note/hist/bugreport/administrators):clear
                ob_to_clear = text[0:text.find(':')]
                exec('{}.clear()'.format(ob_to_clear))
                line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(text='{} has been cleared'.format(ob_to_clear)))

            elif text[:len('note:remove')] == 'note:remove' : #note:remove
                index = text[13:]
                line_bot_api.reply_message(event.reply_token,
                                            [TextSendMessage(text='removing : ' + note[int(index)-1]),
                                             TextSendMessage(text='removed')])
                note.pop(int(index)-1)
                                           
            elif text[:len('release')] == 'release': #release <<index>>
                try :
                    index = text[8:]
                except :
                    index = '0'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=note[int(index)-1]))

            elif text == ':bugreport' :
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='\n'.join(bugreport)))

            elif text == ':administrators' :
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='\n'.join(administrators)))
                
        except Exception as e :
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=e))

    elif text[:len('apakah')] == 'apakah' :
        yesorno = [ 'Ya' , 'Tidak' ]
        last_copy = ''
        for char in text :
            if char not in string.punctuation and char != ' ' :
                last_copy += char
        if last_copy in kejaib.keys() :
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=kejaib[last_copy]))
        else :
            kejaib[last_copy] = random.choice(yesorno)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=kejaib[last_copy]))

    elif 'count' in text :
        try :
            a = "line_bot_api.reply_message(event.reply_token,[ TextSendMessage(text='<<Counting to {}>>'.format(str(number))),"
            numerik = ''
            for i in text :
                try :
                    numerik += str(int(i))
                except :
                    pass
                
            number = int(numerik)
            for i in range(number,0,-1) :
                a += "TextSendMessage(text='Count : {}' ),".format(str(i))
            else :
                a = a[:-1] + "])"
                
            exec(a)
            
        except Exception as e:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=e))
            
    else :
        
        if text in profile.display_name :
            if isinstance(event.source, SourceUser):
                line_bot_api.reply_message(  event.reply_token,
                                            [TextSendMessage( text= profile.display_name + ', Let\'s Join NewbieWorks...' ),
                                             TextSendMessage( text='I\'m my master\'s bot'  ),
                                             TextSendMessage( text='Part of NewbieWorks'  )] )

## ------------------project birthday reminder-------------------------------------
##        elif str(datetime.now(pytz.utc).minute) == '5' :
##            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='done'))


        
                                
    
    
            

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
##                
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

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message( event.reply_token, TextSendMessage(text='Hello :D')) # + event.source.type)) return room / group


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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(event.beacon.hwid, event.beacon.dm)))
#---------------------------------------------built-in-----object------------------------------------#
sapaan = ('hai' , 'hello', 'pagi', 'malam', 'siang')
echo = False
note = []
kejaib = {'apakahya':'Tidak', 'apakahtidak':'Ya'}
hist = {}
bugreport = []
administrators = []

#----------------------------------------------------end---------------------------------------------#

if __name__ == "__main__":
    arg_parser = ArgumentParser(        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    
    # create tmp dir for download content
    make_static_tmp_dir()
    
    app.run(host='0.0.0.0', debug=options.debug, port=int(os.environ.get('PORT' , 5000)))

    
    

